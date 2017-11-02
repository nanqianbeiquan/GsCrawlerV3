# coding=utf-8

import socket
import requests
import time
import Logger

host = '172.16.0.26'
port = 54321


class AppLock(object):
    max_lock_seconds = 30

    status_list = [set(), set()]
    lock_ts_dict = {}

    def __init__(self, lock_nums):
        for i in range(1, lock_nums+1):
            lock_id = str(i)
            self.status_list[0].add(lock_id)
            self.lock_ts_dict[lock_id] = 0

    def get_lock_id(self):
        # print '<', self.lock_ts_dict
        # print '<', self.status_list
        for i in self.lock_ts_dict:
            lock_id = str(i)
            if long(time.time()) - self.lock_ts_dict[lock_id] > self.max_lock_seconds:
                self.lock_ts_dict[lock_id] = 0
                self.status_list[0].add(lock_id)
                if lock_id in self.status_list[1]:
                    self.status_list[1].remove(lock_id)
        if len(self.status_list[0]) > 0:
            lock_id = self.status_list[0].pop()
            self.status_list[1].add(lock_id)
            self.lock_ts_dict[lock_id] = long(time.time())
            # print '>', self.lock_ts_dict
            # print '>', self.status_list
            return lock_id
        else:
            return 0

    def release_lock_id(self, lock_id):
        if lock_id in self.lock_ts_dict:
            lock_ts = self.lock_ts_dict[lock_id]
            if long(time.time()) - lock_ts < self.max_lock_seconds:
                self.status_list[0].add(lock_id)
                if lock_id in self.status_list[1]:
                    self.status_list[1].remove(lock_id)
                    self.lock_ts_dict[lock_id] = 0


class MaYiLockId(object):

    app_lock_dict = {
        '170284467': AppLock(15),
        '151075879': AppLock(0),
    }

    print_msg = True
    log_name = 'MaYiLockId'

    def get_lock_id(self, app_key):
        return self.app_lock_dict[app_key].get_lock_id()

    def release_lock_id(self, app_key, lock_id):
        return self.app_lock_dict[app_key].release_lock_id(lock_id)

    def info(self, msg):
        Logger.write(msg, name=self.log_name, print_msg=self.print_msg)

    def start_server(self):
        """
        启动代理分发服务
        :return:
        """
        global host, port
        s = socket.socket()
        s.bind((host, port))
        s.listen(10)
        while True:
            c, addr = s.accept()
            try:
                msg = c.recv(1024)
                # print c, addr, msg
                if msg.startswith('get'):
                    app_key = msg.split('|')[1]
                    lock_id = self.get_lock_id(app_key)
                    res = str(lock_id)
                else:
                    app_key = msg.split('|')[1]
                    lock_id = msg.split('|')[2]
                    self.release_lock_id(app_key, lock_id)
                    res = 'release succeed'
                self.info('addr:%s, msg:%s, res:%s\n' % (str(addr), msg, res))
                c.send(res)
                c.close()
            except socket.error:
                del c, addr


def get_lock_id(app_key):
    global host, port
    s = socket.socket()
    s.connect((host, port))
    s.send('get|%s' % app_key)
    proxy = s.recv(1024)
    return proxy


def release_lock_id(app_key, lock_id):
    global host, port
    s = socket.socket()
    s.connect((host, port))
    s.send('release|%s|%s' % (app_key, lock_id))
    res = s.recv(1024)
    return res

if __name__ == '__main__':
    # server = MaYiLockId()
    # server.start_server()
    print get_lock_id('170284467')



