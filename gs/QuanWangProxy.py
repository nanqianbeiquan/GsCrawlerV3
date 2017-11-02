# coding=utf-8

import socket
import requests
import time
# from codecs import open
import Logger
import MyException
import copy
import random
import thread
from TimeUtils import get_time, get_cur_time

# host = '127.0.0.1'
host = '172.16.0.26'
port = 12345


class QuanWangProxy(object):
    # host = '172.16.0.26'
    global host, port
    order = '2f28510b6108968e731f1b1036d47903'
    sub_order_list = ['%s,%d' % (order, i) for i in range(5)]
    sub_order_ts_dict = dict.fromkeys(sub_order_list, -1)
    # url_list = {'BeiJing': 'http://qyxy.baic.gov.cn/CheckCodeYunSuan'}
    proxy_pool = {}
    session = requests.session()

    def __init__(self):
        thread.start_new_thread(self.fill_proxy_pool, ())

    def fill_proxy_pool(self):
        while True:
            # print self.proxy_pool
            tmp_list = copy.deepcopy(self.proxy_pool)
            for proxy in tmp_list:
                exp_ts = self.proxy_pool[proxy]
                if long(time.time()*1000) + 2*1000 > exp_ts:
                    self.proxy_pool.pop(proxy)
            print len(self.proxy_pool)
            url = "http://dynamic.goubanjia.com/dynamic/get/" + self.order + ".html?ttl"
            r = requests.get(url)
            if r.status_code == 200:
                proxy_info_list = r.text.strip().split('\n')
                for proxy_info in proxy_info_list:
                    # print proxy_info
                    if len(proxy_info.split(',')) > 1:
                        proxy = proxy_info.split(',')[0]
                        val_ts = long(proxy_info.split(',')[1])
                        fetch_ts = long(time.time()*1000)
                        exp_ts = fetch_ts + val_ts
                        # self.proxy_pool[proxy] = exp_ts
                        # print '->', get_time(fetch_ts), val_ts, get_time(exp_ts)

                        # url = 'http://gsxt.zjaic.gov.cn/zhejiang.jsp'
                        if self.check_proxy(proxy):
                            self.proxy_pool[proxy] = exp_ts
                        else:
                            if proxy in self.proxy_pool:
                                self.proxy_pool.pop(proxy)
                    else:
                        print 't.text ->', r.text
            else:
                continue
            time.sleep(5)

    def check_proxy(self, proxy):
        self.session.proxies = {'http': proxy}
        try:

            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0",
                       "Host": "www.pss-system.gov.cn",
                       "Accept": "*/*",
                       "Accept-Encoding": "gzip, deflate",
                       "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
                       "Referer": "http://www.pss-system.gov.cn/sipopublicsearch/patentsearch/tableSearch-showTableSearchIndex.shtml",
                       "Connection": "keep-alive"
                       }
            url = "http://www.pss-system.gov.cn/sipopublicsearch/patentsearch/searchHomeIndex-searchHomeIndex.shtml"
            r = self.session.get(url, headers=headers, timeout=3)
            if r.status_code == 200:
                # r.encoding = 'utf-8'
                print proxy, '+'
                # print r.text
                return True
            else:
                raise MyException.StatusCodeException(u'错误的返回状态: '+str(r.status_code))
        except Exception, e:
            print proxy, '-', e
            return False

    def get_proxy(self):

        while True:
            tmp_list = copy.deepcopy(self.proxy_pool.keys())
            while len(tmp_list) > 0:
                rand_idx = random.randint(0, len(tmp_list) - 1)
                proxy = tmp_list.pop(rand_idx)
                exp_ts = self.proxy_pool.get(proxy)
                # print '> ', get_time(exp_ts), get_cur_time()
                if long(time.time() * 1000) + 2 * 1000 > exp_ts:
                    # print u'不满足条件'
                    continue
                else:
                    return proxy
            print u'暂无可用代理,休眠1秒钟...'
            raise ValueError('No proxy available!')

    def start_server(self):
        """
        启动代理分发服务
        :return:
        """
        requests.adapters.DEFAULT_RETRIES = 1
        global host, port
        s = socket.socket()
        s.bind((host, port))
        s.listen(10)
        while True:
            c, addr = s.accept()
            # print addr
            try:
                proxy = self.get_proxy()
                c.send(proxy)
                c.close()
                Logger.write(str(addr) + ", " + proxy)
            except socket.error:
                del c, addr
                # s.close()
                pass


def get_proxy():
    """
    通过代理分发服务获取代理
    :return:
    """
    global host, port
    s = socket.socket()
    s.connect((host, port))
    proxy = s.recv(1024)
    return proxy


def remove_proxy(proxy):
    global host, port
    s = socket.socket()
    s.connect((host, port))
    s.send('remove|'+proxy)
    s.close()

if __name__ == '__main__':
    while True:
        try:
            server = QuanWangProxy()
            server.start_server()
        except ValueError:
            print 'ValueError'
            time.sleep(10)
            pass
    # server.get_proxy()
    # for i in range(1000):
    #     print i, get_proxy()
    # thread.start_new_thread(test1(),())
    # thread.start_new_thread(test2(),())


