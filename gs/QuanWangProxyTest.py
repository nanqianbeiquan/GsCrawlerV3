# coding=utf-8

import requests
from QuanWangProxy import order_list
from QuanWangProxy import get_proxy
import time


def test1():
    for order in order_list:
        # url = "http://dynamic.goubanjia.com/dynamic/get/" + order + ".html?ttl"
        # r = requests.get(url)
        # proxy_info = r.text.split(',')
        # proxy = proxy_info[0]
        '''

[u'100.73.16.29:44852', u'59057\n']
更换代理
[u'144.255.123.248:58265', u'56718\n']
更换代理
[u'117.60.215.31:36368', u'59263\n']
更换代理
[u'139.201.255.49:55500', u'59430\n']
        '''
        session = requests.session()
        session.proxies = {'http': "100.73.16.29:44852"}
        r2 = session.get('http://1212.ip138.com/ic.asp')
        r2.encoding = 'gbk'
        print r2.text


def test2():
    for i in range(10000):
        if i % 40 == 0:
            print '%d -> %d' % (int(time.time()), i)
            get_proxy()


def test3():
    for i in range(30):
        proxy = get_proxy()
        print proxy
        session = requests.session()
        session.proxies = {'http': proxy}
        r2 = session.get('http://1212.ip138.com/ic.asp')
        r2.encoding = 'gbk'
        print r2.text

if __name__ == '__main__':
    test1()
    # print long(time.time()*1000)
