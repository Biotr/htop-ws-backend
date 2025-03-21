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
        self.processes_dict = dict()
        self.prev_total_time = dict()

    def _read_file(self, prefix):
        with open(f"/proc/{prefix}") as f:
            return f.read()

    def set_cores_usage(self):
        file = self._read_file("stat").split("\n")
        cores = [core for core in file if core.startswith("cpu")]
        for core in cores:
            core = [int(i) if i.isnumeric() else i for i in core.split()]
            cpu_total = sum(core[1:])
            cpu_idled = core[4]
            cpu_total_delta = cpu_total - self.cores_usage.get(core[0], {}).get("total", 0)
            cpu_total_delta = cpu_total_delta if cpu_total_delta != 0 else 1
            cpu_idled_delta = cpu_idled - self.cores_usage.get(core[0], {}).get("idled", 0)
            cpu_percentage = round(((cpu_total_delta - cpu_idled_delta) / cpu_total_delta) * 100, 1)
            self.cores_prev[core[0]] = {"total": cpu_total, "idled": cpu_idled}
            self.cores_usage[core[0]] = str(cpu_percentage)
        self.cores_number = len(self.cores_usage) - 1

    def set_uptime(self):
        file = self._read_file("uptime").split()
        self.uptime = float(file[0])

    def set_load_average(self):
        file = self._read_file("loadavg").split()
        self.load_avg = file[:3]

    def get_cores_usage(self):
        self.set_cores_usage()
        return self.cores_usage

    def set_processes(self):
        pids = [pid for pid in listdir if pid.isnumeric()]
        for pid in pids:
            try:
                process = Process(pid)
                [status, pri, ni, virt, total_time] = process.get_stat()
                [vm_size, res, rss_file, rss_shmem] = process.get_status()
                command = process.get_command()
                owner = process.get_process_owner()
            except:
                continue
            uptime = self.uptime
            self.set_uptime()
            pid_cpu_usage = round()


def get_mem_usage():
    free_result = subprocess.run(["free"], shell=True, capture_output=True, text=True)
    total, *rest, shared, buff_cache, available = [int(i) for i in free_result.stdout.split()[7:13]]
    swap_total, swap_used, swap_free = [int(i) for i in free_result.stdout.split()[14:]]
    mem_used = total - available - shared - buff_cache
    swap_used = swap_total - swap_free
    return [total, mem_used, swap_total, swap_used]


def get_cpu_usage(cores_prev={}, cores_usage={}):
    with open("/proc/stat", "r") as f_cpu:
        file_cpu = f_cpu.readlines()
    cores = [core for core in file_cpu if core.startswith("cpu")]
    for core in cores:
        core = [int(i) if i.isnumeric() else i for i in core.split()]
        cpu_total = sum(core[1:])
        cpu_idled = core[4]
        cpu_total_delta = cpu_total - cores_prev.get(core[0], {}).get("total", 0)
        cpu_total_delta = cpu_total_delta if cpu_total_delta != 0 else 1
        cpu_idled_delta = cpu_idled - cores_prev.get(core[0], {}).get("idled", 0)
        cpu_percentage = round(((cpu_total_delta - cpu_idled_delta) / cpu_total_delta) * 100, 1)
        cores_prev[core[0]] = {"total": cpu_total, "idled": cpu_idled}
        cores_usage[core[0]] = str(cpu_percentage)
    return cores_usage


def get_uptime():
    with open(f"/proc/uptime") as f_uptime:
        file_uptime = f_uptime.read().split()
    uptime = float(file_uptime[0])
    return uptime


def get_load_average():
    with open("/proc/loadavg") as f:
        file = f.read()
    load_average = file.split(" ")[:3]
    return load_average


process_prev = dict()

uptime_prev = 0


def get_processes(clk_tck=len(get_cpu_usage()) - 2):
    mem_output = get_mem_usage()
    pids = [pid for pid in listdir("/proc") if pid.isnumeric()]
    uptime = get_uptime()
    processes = list()
    for pid in pids:
        try:
            process = Process(pid)
            [status, pri, ni, virt, total_time] = process.get_stat()
            [vm_size, res, rss_file, rss_shmem] = process.get_status()
            command = process.get_command()
            owner = process.get_process_owner()
        except:
            continue
        cpu_usage = round(
            ((total_time - process_prev.get(pid, 0)) / ((uptime - uptime_prev) * (clk_tck - 1))) * 100,
            1,
        )
        process_prev[pid] = total_time
        time_plus = total_time / clk_tck
        mem_usage = round((res / mem_output[0]) * 100, 1)
        shr = rss_file + rss_shmem
        processes.append(
            [
                pid,
                owner,
                pri,
                ni,
                virt,
                res,
                shr,
                status,
                cpu_usage,
                mem_usage,
                time_plus,
                command,
            ]
        )
    print(uptime, uptime_prev)
    print(uptime - uptime_prev)
    uptime_prev = uptime
    return processes


if __name__ == "__main__":
    while True:
        get_processes()
        time.sleep(1)
