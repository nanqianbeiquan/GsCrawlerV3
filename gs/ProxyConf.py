# coding=utf-8

import requests
import hashlib
import time
import random
from MaYiLockId import get_lock_id, release_lock_id


key1 = {'app_key': '170284467',
        'secret': 'a9162d3d1fbb984f99564a29a469ada8',
        'host': 's2.proxy.mayidaili.com',
        'port': '8123',
        'concurrent_num': 20,
        'lock_num': 15
        }

key2 = {'app_key': '151075879',
        'secret': '32ebc7fc46978aeafd5d9c012fa9a037',
        'host': 's2.proxy.mayidaili.com',
        'port': '8123',
        'concurrent_num': 40,
        'lock_num': 0
        }

key3 = {'app_key': '137896159',
        'secret': '648a0531abc57e0fd395cefae9961089',
        'host': 's3.proxy.mayidaili.com',
        'port': '8123',
        'concurrent_num': 20,
        'lock_num': 0
        }


key4 = {'app_key': '60719893',
        'secret': '23aaf8a59bb7b3188333cc44ee3d53e1',
        'host': 's1.proxy.mayidaili.com',
        'port': '8123',
        'concurrent_num': 5,
        'lock_num': 0
        }


class ProxyConf(object):

    def __init__(self, key):
        self.app_key = key['app_key']
        self.secret = key['secret']
        self.host = key['host']
        self.port = key['port']
        self.concurrent_num = key['concurrent_num']
        self.lock_num = key['lock_num']

    def get_proxy(self):
        return {'http': '%s:%s' % (self.host, self.port), 'https': '%s:%s' % (self.host, self.port)}

    def get_auth_header(self, lock_id='0', release_id='0'):
        # print 'self.app_key', self.app_key
        # print 'lock_id', lock_id
        param_map = {
            "app_key": self.app_key,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),  # 如果你的程序在国外，请进行时区处理
            "retrypost": "true",
            "timeout": 100*1000
            #  ,"with-transaction": '1'
        }
        # print 'param_map', param_map
        if lock_id != '0':
            param_map['with-transaction'] = lock_id
        if release_id != '0':
            param_map['release-transaction'] = release_id
        # 排序
        keys = param_map.keys()
        keys.sort()
        codes = "%s%s%s" % (self.secret, str().join('%s%s' % (key, param_map[key]) for key in keys), self.secret)
        # 计算签名
        sign = hashlib.md5(codes).hexdigest().upper()
        param_map["sign"] = sign

        # 拼装请求头Proxy-Authorization的值
        keys = param_map.keys()
        auth_header = "MYH-AUTH-MD5 " + str('&').join('%s=%s' % (key, param_map[key]) for key in keys)
        return auth_header

    # def get_lock_id(self):
    #     return random.randint(1, self.lock_num)

    def get_lock_id(self):
        # print self.app_key
        lock_id = get_lock_id(self.app_key)
        if lock_id != '0':
            return lock_id
        else:
            print u'没有可用lock_id,休眠3秒后重试...'
            time.sleep(3)
            return self.get_lock_id()

    def release_lock_id(self, lock_id):
        release_lock_id(self.app_key, lock_id)

if __name__ == '__main__':

    conf = ProxyConf(key1)
    session = requests.session()
    session.proxies = conf.get_proxy()
    print session.proxies
    headers = {'Proxy-Authorization': conf.get_auth_header()}

    rt = session.get('http://www.sina.com/',
                     headers=headers,
                     # verify=False
                     )
    # rt.encoding = 'gb2312'
    print rt.text.strip()
    print rt
    # print rt.headers
