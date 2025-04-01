import os
import pwd
import re
import subprocess
import time
from os import listdir


class Process:
    def __init__(self, pid):
        self.pid = pid
        self.stat_path = f"/proc/{pid}/stat"
        self.status_path = f"/proc/{pid}/status"
        self.cmdline_path = f"/proc/{pid}/cmdline"

    def _read_file(self, path):
        with open(path) as f:
            return f.read()

    def get_stat(self):
        file = self._read_file(self.stat_path).split()
        status = file[2]
        utime, stime, pri, ni, virt = map(int, [*file[13:15], *file[17:19], file[22]])
        total_time = stime + utime
        return [status, pri, ni, virt, total_time]

    def get_status(self):
        file = self._read_file(self.status_path)
        vm_size = int(re.findall(r"VmSize.*?([0-9]\S*)", file)[0])
        res = int(re.findall(r"VmRSS.*?([0-9]\S*)", file)[0])
        rss_file = int(re.findall(r"RssFile.*?([0-9]\S*)", file)[0])
        rss_shmem = int(re.findall(r"RssShmem.*?([0-9]\S*)", file)[0])
        return [vm_size, res, rss_file, rss_shmem]

    def get_command(self):
        file = self._read_file(self.cmdline_path)
        return file.strip().replace("\x00", " ")

    def get_process_owner(self):
        stat_info = os.stat(f"/proc/{self.pid}")
        uid = stat_info.st_uid
        user = pwd.getpwuid(uid)[0]
        return user


def get_clock_ticks():
    getconf_result = subprocess.run(["getconf CLK_TCK"], shell=True, capture_output=True, text=True)  # TODO search for info about getting this data
    return int(getconf_result.stdout)

class SystemInfo:
    def __init__(self):
        self.cores_prev = dict()
        self.cores_usage = dict()
        self.cores_number = 0
        self.load_avg = []
        self.clk_tck = get_clock_ticks()
        self.prev_total_time = dict()
        self.uptime_prev = None
        self.uptime = 0 
        self.processes=list()
        self.meminfo = dict()
    def _read_file(self, prefix):
        with open(f"/proc/{prefix}") as f:
            return f.read()

    def set_cores_info(self):
        file = self._read_file("stat").split("\n")
        cores = [core for core in file if core.startswith("cpu")]
        for core in cores:
            core = [int(i) if i.isnumeric() else i for i in core.split()]
            cpu_total = sum(core[1:])
            cpu_idled = core[4]
            cpu_number = core[0]

            cpu_total_delta = cpu_total - self.cores_prev.get(core[0], {}).get("total", 0)
            cpu_total_delta = cpu_total_delta if cpu_total_delta != 0 else 1
            cpu_idled_delta = cpu_idled - self.cores_prev.get(core[0], {}).get("idled", 0)
            cpu_percentage = round(((cpu_total_delta - cpu_idled_delta) / cpu_total_delta) * 100, 1)
            self.cores_prev[cpu_number] = {"total": cpu_total, "idled": cpu_idled}
            self.cores_usage[cpu_number] = str(cpu_percentage)

    def set_uptime(self):
        file = self._read_file("uptime").split()
        self.uptime = float(file[0])

    def set_load_average(self):
        file = self._read_file("loadavg").split()
        self.load_avg = file[:3]

    def set_memory_info(self):
        free_result = subprocess.run(["free"], shell=True, capture_output=True, text=True)
        total, *rest, shared, buff_cache, available = [int(i) for i in free_result.stdout.split()[7:13]]
        swap_total, swap_used, swap_free = [int(i) for i in free_result.stdout.split()[14:]]
        mem_used = total - available - shared - buff_cache
        swap_used = swap_total - swap_free
        self.meminfo = {"total_mem":total, "used_mem":mem_used, "swap_mem":swap_total,"swap_used": swap_used}

    def set_processes(self):
        pids = [pid for pid in listdir("/proc") if pid.isnumeric()]
        processes = []
        for pid in pids:
            try:
                process = Process(pid)
                status, pri, ni, virt, total_time = process.get_stat()
                _, res, rss_file, rss_shmem = process.get_status()
                command = process.get_command()
                owner = process.get_process_owner()
            except Exception as e:
                continue
            uptime_diff = 1 if self.uptime_prev is None else self.uptime - self.uptime_prev
            time_diff = total_time - self.prev_total_time.get(pid,0) 
            pid_cpu_usage = round((time_diff/(uptime_diff*self.clk_tck)*100))

            self.prev_total_time[pid]=total_time
        
            time_plus = total_time/self.clk_tck
            mem_usage = round((res / self.meminfo["total_mem"]) * 100, 1)
            shr = rss_file + rss_shmem

            processes.append({"pid":pid,"owner":owner,"pri":pri,"ni":ni,"virt":virt,"res":res,"shr":shr,"status":status,"pid_cpu_usage":pid_cpu_usage,"mem_usage":mem_usage,"time_plus":time_plus,"command":command})
        self.uptime_prev = self.uptime
        self.processes = processes

    def update(self):
        self.set_cores_info()
        self.set_load_average() 
        self.set_uptime()
        self.set_memory_info()
        self.set_processes()
        return {"cores_usage":self.cores_usage,"load_average":self.load_avg,"uptime":self.uptime,"mem_info":self.meminfo}

if __name__ == "__main__":
    sys = SystemInfo()
    while True:
        sys.update()
        print(sys.meminfo)
        time.sleep(1)
