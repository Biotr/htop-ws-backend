import time
import os
import re
import subprocess
from os import listdir
from os.path import isfile, join
cores_prev = dict()
process_prev = dict()
uptime_prev = 0
def get_cpu_usage():
	with open('/proc/stat','r') as f_cpu:
		file_cpu = f_cpu.readlines()
	cores = [core for core in file_cpu if core.startswith('cpu')]	
	return cores

def get_mem_usage():
	result = subprocess.run(['free'], shell=True, capture_output=True, text=True)
	total, *rest, shared, buff_cache, available = [int(i) for i in result.stdout.split()[7:13]]
	swap_total, swap_used, swap_free = [int(i) for i in result.stdout.split()[14:]]
	mem_used = total - available - shared - buff_cache 
	swap_used = swap_total - swap_free
	return [total, mem_used, swap_total, swap_used]

def get_uptime():
	with open(f'/proc/uptime') as f_uptime:
		file_uptime = f_uptime.read().split()
	uptime = float(file_uptime[1])	
	return uptime



while(True):
	os.system('clear')
	mem_output = get_mem_usage()
	cores_usage = list()
	for core in get_cpu_usage():
		core = [int(i) if i.isnumeric() else i for i in core.strip().split()]
		cpu_total = sum(core[1:])
		cpu_total_delta = cpu_total - cores_prev.get(core[0],[0,0])[0]
		cpu_idled_delta = core[4] - cores_prev.get(core[0],[0,0])[1]
		cpu_percentage = round(((cpu_total_delta - cpu_idled_delta)/cpu_total_delta)*100,1)
		cores_usage.append(cpu_percentage)
		cores_prev[core[0]] = [cpu_total, core[4]]

	pids = [pid for pid in listdir('/proc') if pid.isnumeric()]
	uptime = get_uptime()		
	processes = list()	
	for pid in pids:
		try:	
			with open(f'/proc/{pid}/stat') as f:
				file = f.read().split()	
			with open(f'/proc/{pid}/status') as f_m:
				file_m = f_m.read()
		except:
			continue
		utime = int(file[13])
		stime = int(file[14])
		total_time = utime+stime
		cpu_usage = round(((total_time - process_prev.get(pid,0))/((uptime-uptime_prev)*12))*100,2) #12 do zmiany
		process_prev[pid] = total_time
		status = file[2]
		pri = int(file[17])
		ni = int(file[18])
		virt = int(file[22])/1024 # jednostki

		res = int(re.findall('VmRSS.*?([0-9]\S*)',file_m)[0])
		rss_file = int(re.findall('RssFile.*?([0-9]\S*)',file_m)[0])	
		rss_shmem = int(re.findall('RssShmem.*?([0-9]\S*)',file_m)[0])	
		shr = rss_file + rss_shmem 
		processes.append([pid,'ubuntu',pri,ni,virt,res,shr,status,cpu_usage])	
	
	uptime_prev = uptime
	time.sleep(1)