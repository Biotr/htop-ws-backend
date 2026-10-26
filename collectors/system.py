import subprocess


class SystemCollector:
    def __init__(self):
        self.prev_cores = {}

    def _read_file(self, prefix):
        with open(f"/proc/{prefix}") as f:
            return f.read()

    def get_cpu_usage(self):
        file = self._read_file("stat").split("\n")
        cores = [core for core in file if core.startswith("cpu")]
        cores_usage = {}
        for core in cores:
            core = [int(i) if i.isnumeric() else i for i in core.split()]
            cpu_total = sum(core[1:])
            cpu_idled = core[4]
            cpu_number = core[0]

            cpu_total_delta = cpu_total - self.prev_cores.get(core[0], {}).get("total", 0)
            cpu_total_delta = cpu_total_delta if cpu_total_delta != 0 else 1
            cpu_idled_delta = cpu_idled - self.prev_cores.get(core[0], {}).get("idled", 0)
            cpu_percentage = round(((cpu_total_delta - cpu_idled_delta) / cpu_total_delta) * 100, 1)
            self.prev_cores[cpu_number] = {"total": cpu_total, "idled": cpu_idled}
            cores_usage[cpu_number] = str(cpu_percentage)
        return cores_usage

    def get_uptime(self):
        file = self._read_file("uptime").split()
        uptime = float(file[0])
        return uptime

    def get_load_avg(self):
        file = self._read_file("loadavg").split()
        load_avg = file[:3]
        return load_avg

    def get_clock_ticks(self):
        getconf_result = subprocess.run(["getconf CLK_TCK"], shell=True, capture_output=True, text=True)
        return int(getconf_result.stdout)

    def get_memory_info(self):
        free_result = subprocess.run(["free"], shell=True, capture_output=True, text=True)
        total, _, _, shared, buff_cache, available = [int(i) for i in free_result.stdout.split()[7:13]]
        swap_total, swap_used, swap_free = [int(i) for i in free_result.stdout.split()[14:]]
        mem_used = total - available - shared - buff_cache
        swap_used = swap_total - swap_free
        memory_info = {
            "total": total,
            "used": mem_used,
            "swap_total": swap_total,
            "swap_used": swap_used,
        }
        return memory_info
