# coding=utf-8

import socket
import uuid
import time
import psutil
import subprocess
import Logger
import MySQL
import os


class CrawlerMonitor(object):

    def __init__(self):
        self.job_info_dict1 = {}  # 计划进程数
        self.job_info_dict2 = {}  # 实际进程数

    def run(self):
        while True:
            self.load_job_info()
            self.get_crawler_process_list()
            # print self.job_info_dict1
            # print self.job_info_dict2
            for job in self.job_info_dict1:
                n1 = self.job_info_dict1[job]
                n2 = self.job_info_dict2.get(job, 0)
                n3 = n1 - n2
                # print n1, n2, n3
                if n3 > 0:
                    # print (n1, n2, n3)
                    for i in range(n3):
                        Logger.write(u'启动任务 ' + job, print_msg=True)
                        # print "python "+job
                        # subprocess.Popen("python "+job, stdout=subprocess.PIPE)
                        subprocess.Popen("python " + job)
                        # subprocess.Popen()
                        # x = os.system("python "+job)
                        # print x.read()
                elif n3 < 0:
                    for i in range(-n3):
                        Logger.write(u'杀死任务 ' + job, print_msg=True)
                        kill_job(job)
            Logger.write(u'休眠5秒钟...', print_msg=True)
            time.sleep(5)

    def load_job_info(self):
        self.job_info_dict1.clear()
        host = get_localhost()
        sql = "select * from job.job_info where host='%s'" % host
        res = MySQL.execute_query(sql)
        if len(res) == 0:
            Logger.write(u'当前服务器（%s）未配置任何任务' % host, print_msg=True)
        for row in res:
            path = row[1].lower()
            job_status = row[4]
            # print '***', path, path == r'C:\Users\kai.li\pycharmprojects\GsClawlerV2\gs\UpdateNew.py'
            if job_status == 'on':
                process_nums = row[3]
            else:
                process_nums = 0
            self.job_info_dict1[path] = process_nums

    def get_crawler_process_list(self):
        self.job_info_dict2.clear()
        pids = psutil.pids()
        for pid in pids:
            try:
                p = psutil.Process(pid)
                if p.name() == 'python.exe':
                    if len(p.cmdline()) > 1:
                        script_file = p.cmdline()[1].lower()
                        # print '+++', script_file, script_file == r'C:\Users\kai.li\pycharmprojects\GsClawlerV2\gs\UpdateNew.py'
                        if script_file in self.job_info_dict1:
                            self.job_info_dict2[script_file] = self.job_info_dict2.get(script_file, 0) + 1
            except psutil.NoSuchProcess:
                pass


def kill_job(job):
    pids = psutil.pids()
    num = 0
    for pid in pids:
        try:
            p = psutil.Process(pid)
            if p.name() == 'python.exe':
                if len(p.cmdline()) > 1:
                    script_file = p.cmdline()[1].lower()
                    if script_file == job:
                        num += 1
                        p.kill()
                        break
        except psutil.NoSuchProcess:
            pass


def get_localhost():
    """
    获取内网ip
    :return:
    """
    return socket.gethostbyname(socket.gethostname())


def get_mac_addr():
    """
    获取mac地址
    :return:
    """
    return uuid.UUID(int=uuid.getnode()).hex[-12:]

if __name__ == '__main__':
    os.chdir(os.path.dirname(__file__))
    CrawlerMonitor().run()

