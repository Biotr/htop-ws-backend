import re
import os
import pwd

class ProcessCollector:
    def __init__(self, clk_tck):
        self.clk_tck = clk_tck
        self.prev_proc_times = {}

    def _read_file(self, path):
        with open(path) as f:
            return f.read()

    def _get_stat(self, pid):
        file = self._read_file(f"/proc/{pid}/stat").split()
        status = file[2]
        utime, stime, pri, ni, virt = map(int, [*file[13:15], *file[17:19], file[22]])
        total_time = stime + utime
        return [status, pri, ni, virt, total_time]

    def _get_status(self, pid):
        file = self._read_file(f"/proc/{pid}/status")
        vm_size = int(re.findall(r"VmSize.*?([0-9]\S*)", file)[0])
        res = int(re.findall(r"VmRSS.*?([0-9]\S*)", file)[0])
        rss_file = int(re.findall(r"RssFile.*?([0-9]\S*)", file)[0])
        rss_shmem = int(re.findall(r"RssShmem.*?([0-9]\S*)", file)[0])
        return [vm_size, res, rss_file, rss_shmem]

    def _get_command(self, pid):
        file = self._read_file(f"/proc/{pid}/cmdline")
        return file.strip().replace("\x00", " ")

    def _get_process_owner(self, pid):
        stat_info = os.stat(f"/proc/{pid}")
        uid = stat_info.st_uid
        user = pwd.getpwuid(uid)[0]
        return user

    def collect(self, uptime_diff, meminfo):
        pids = [pid for pid in os.listdir("/proc") if pid.isnumeric()]
        processes = []
        for pid in pids:
            try:
                status, pri, ni, virt, total_time = self._get_stat(pid)
                _, res, rss_file, rss_shmem = self._get_status(pid)
                command = self._get_command(pid)
                owner = self._get_process_owner(pid)
            except Exception:
                continue
            time_diff = total_time - self.prev_proc_times.get(pid, 0)
            pid_cpu_usage = round((time_diff / (uptime_diff * self.clk_tck) * 100))

            self.prev_proc_times[pid] = total_time

            time_plus = total_time / self.clk_tck
            mem_usage = round((res / meminfo) * self.clk_tck, 1)
            shr = rss_file + rss_shmem

            processes.append({"pid": pid, "owner": owner, "pri": pri, "ni": ni, "virt": virt, "res": res, "shr": shr, "status": status, "pid_cpu_usage": pid_cpu_usage, "mem_usage": mem_usage, "time_plus": time_plus, "command": command})
        return processes


