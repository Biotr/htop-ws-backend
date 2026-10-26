from collectors.system import SystemCollector
from collectors.process import ProcessCollector
import asyncio


class MetricsEngine:
    def __init__(self):
        self.system_collector = SystemCollector()
        self.clk_tck = self.system_collector.get_clock_ticks()
        self.process_collector = ProcessCollector(self.clk_tck)
        self.data = {}
        self.prev_uptime = None

    async def run_loop(self):
        while True:
            uptime = self.system_collector.get_uptime()
            uptime_diff = 1.0 if self.prev_uptime is None else uptime - self.prev_uptime
            self.prev_uptime = uptime

            cpu_usage = self.system_collector.get_cpu_usage()
            load_avg = self.system_collector.get_load_avg()
            memory = self.system_collector.get_memory_info()
            processes = self.process_collector.collect(uptime_diff, memory["total"])

            self.data = {
                "cpu_usage": cpu_usage,
                "load_avg": load_avg,
                "memory_usage": memory,
                "processes": processes,
                "uptime": uptime,
            }
            await asyncio.sleep(1)
