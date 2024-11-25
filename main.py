import time
import os
import re
import subprocess
import time
import pwd
from os import listdir


def get_cpu_usage():
	with open('/proc/stat','r') as f_cpu:
		file_cpu = f_cpu.readlines()
	cores = [core for core in file_cpu if core.startswith('cpu')]	
	return cores

def get_mem_usage():
	free_result = subprocess.run(['free'], shell=True, capture_output=True, text=True)
	total, *rest, shared, buff_cache, available = [int(i) for i in free_result.stdout.split()[7:13]]
	swap_total, swap_used, swap_free = [int(i) for i in free_result.stdout.split()[14:]]
	mem_used = total - available - shared - buff_cache 
	swap_used = swap_total - swap_free
	return [total, mem_used, swap_total, swap_used]

def get_uptime():
	with open(f'/proc/uptime') as f_uptime:
		file_uptime = f_uptime.read().split()
	uptime = float(file_uptime[1])	
	return uptime

def get_clock_ticks():
	getconf_result = subprocess.run(["getconf CLK_TCK"], shell=True, capture_output=True, text=True) # TODO search for info about getting this data
	return int(getconf_result.stdout)

def get_cores_number():
	with open('/proc/cpuinfo','r') as f:
		file = f.read()
	cores_counter = len(re.findall('processor',file))
	return cores_counter

def get_process_user(pid):
	stat_info = os.stat(f'/proc/{pid}')
	uid = stat_info.st_uid
	user = pwd.getpwuid(uid)[0]
	return user

uptime_prev = 0
cores_prev = dict()
process_prev = dict()
cores_number = get_cores_number()
clk_tck = get_clock_ticks()

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
				file_stat = f.read().split()	
			with open(f'/proc/{pid}/cmdline','r') as f:
				file_cmd = f.read().strip().replace("\x00","")
			with open(f'/proc/{pid}/status') as f:
				file_m = f.read()
			owner = get_process_user(pid)	
		except:
			continue
		status = file_stat[2]
		utime = int(file_stat[13])
		stime = int(file_stat[14])
		pri = int(file_stat[17])
		ni = int(file_stat[18])
		virt = int(file_stat[22])
		
		total_time = utime+stime
		cpu_usage = round(((total_time - process_prev.get(pid,0))/((uptime-uptime_prev)*cores_number))*100,1) 
		process_prev[pid] = total_time 
		vm_size = int(re.findall('VmSize.*?([0-9]\S*)',file_m)[0]) 
		res = int(re.findall('VmRSS.*?([0-9]\S*)',file_m)[0])
		rss_file = int(re.findall('RssFile.*?([0-9]\S*)',file_m)[0])	
		rss_shmem = int(re.findall('RssShmem.*?([0-9]\S*)',file_m)[0])
		
		time_plus = total_time/clk_tck
		mem_usage = round((res/mem_output[0])*100,1) 
		shr = rss_file + rss_shmem 
		processes.append([pid,owner, pri, ni, virt, res, shr, status, cpu_usage, mem_usage ,time_plus, file_cmd])
	uptime_prev = uptime
	print(processes[0])
	print(processes[1])
	print(processes[2])
	time.sleep(1)
	 