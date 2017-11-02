# coding=utf-8

import requests

order1 = '2f28510b6108968e731f1b1036d47903'


def get_proxy(order):
    url = "http://dynamic.goubanjia.com/dynamic/get/" + order + ".html?ttl"
    r = requests.get(url)
    print r.text
    proxy_info = r.text.split(',')
    return proxy_info[0]


if __name__ == '__main__':
    proxy = get_proxy(order1)
    # proxy = '182.45.48.90:33087'
    session = requests.session()
    session.proxies = {'http': proxy, 'https': proxy, }
    for _ in range(15):
        # proxy = get_proxy(order1)
        print _
        try:
            r = session.get('http://1212.ip138.com/ic.asp', timeout=5)
            r.encoding = 'gbk'
            print r.text
        except Exception,e:
            print "*********"
