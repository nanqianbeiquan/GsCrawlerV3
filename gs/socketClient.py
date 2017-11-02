# coding=utf-8

from socket import *
import threading

"""
hosts 表示所有服务器ip列表
"""
# hosts = ['172.16.0.31','172.16.0.32','172.16.0.33','172.16.0.34','172.16.0.35','172.16.0.36','172.16.0.37','172.16.0.38','172.16.0.39','172.16.0.40',
#          '172.16.0.41','172.16.0.42','172.16.0.43','172.16.0.44','172.16.0.45','172.16.0.46','172.16.0.47','172.16.0.48','172.16.0.49','172.16.0.50']
hosts = ['172.16.0.46']
port = 54321
bufsize = 1024

addr_list = [(host, port) for host in hosts]

def client(addr, commands):
	print 'trying to connect....', addr
	command_client = socket(AF_INET,SOCK_STREAM)
	command_client.connect(addr)
	command_client.send(commands)
	while True:
		data = command_client.recv(bufsize)
		if not data:
			break
		if 'finished' in data:
			break
	command_client.close()
	print '%s connection over' % addr[0]

def main():
	"""
	taskkill /im python.exe  杀死所有python进程
	set path=%PATH%;D:\git\Git\\bin...cd \...cd GsClawlerV2...git pull origin master 同步git(连续连续四个命令)
	start python D:\\GsClawlerV2\\gs\\CrawlerMonitor.py  根据程序路径启动python程序
	'taskkill /im python.exe -f...set path=%PATH%;D:\git\Git\\bin...cd \...cd GsClawlerV2...git pull origin master...start '
		                                                    'python D:\\GsClawlerV2\\gs\\CrawlerMonitor.py'
	"""
	threads_list = list()
	for add in addr_list:
		threads = threading.Thread(target=client, args=(add,'taskkill /im python.exe -f...set path=%PATH%;D:\git\Git\\bin...cd \...cd GsClawlerV2...git pull origin master...start '
		                                                    'python D:\\GsClawlerV2\\gs\\CrawlerMonitor.py'))  #服务器批处理命令
		threads_list.append(threads)
	for threads in threads_list:
		threads.start()
	print 'task finished'

if __name__ == '__main__':
	main()
