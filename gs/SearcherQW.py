# coding=utf-8

from Searcher import Searcher
from requests.exceptions import ReadTimeout
from requests.exceptions import ConnectTimeout
from requests.exceptions import ProxyError
from requests.exceptions import ConnectionError
import requests
from QuanWangProxy import get_proxy
from MyException import StatusCodeException
import time

requests.adapters.DEFAULT_RETRIES = 2


class SearcherQW(Searcher):

    proxy_last_update_ts = 0  # 上次更换代理的时间

    def __init__(self):
        super(SearcherQW, self).__init__(False, False)
        self.timeout = 10
        # proxy = get_proxy()
        # self.session.proxies = {'http': proxy, 'https': proxy}

    def get_request(self, url, t=0, **kwargs):
        try:
            r = self.session.get(url=url, headers=self.headers, timeout=self.timeout, **kwargs)
            if r.status_code != 200:
                if self.province == u'浙江省' and r.status_code == 504:
                    # print '**504\n', r.text
                    del self.session
                    self.session = requests.session()
                    raise ReadTimeout()
                # print u'错误的响应代码 -> %d' % r.status_code
                if r.status_code == 403:
                    raise ReadTimeout()
                raise StatusCodeException(u'错误的响应代码 -> %d' % r.status_code)
            else:
                return r
        except StatusCodeException, e:
            print e
            if t == 15:
                raise e
            else:
                return self.get_request(url, t+1, **kwargs)
        except (ReadTimeout, ConnectTimeout, ProxyError, ConnectionError) as e:
            # traceback.print_exc(e)
            # print e
            if t == 15:
                raise e
            else:
                self.set_proxy()
                return self.get_request(url, t+1, **kwargs)

    def post_request(self, url, t=0, **kwargs):
        try:
            r = self.session.post(url=url, headers=self.headers, timeout=self.timeout, **kwargs)
            if r.status_code != 200:
                if self.province == u'浙江省' and r.status_code == 504:
                    # print '**504\n', r.text
                    del self.session
                    self.session = requests.session()
                    raise ReadTimeout()
                if r.status_code == 403:
                    raise ReadTimeout()
                raise StatusCodeException(u'错误的响应代码 -> %d' % r.status_code)
            else:
                return r
        except StatusCodeException, e:
            print e
            if t == 15:
                raise e
            else:
                return self.get_request(url, t+1, **kwargs)
        except (ReadTimeout, ConnectTimeout, ProxyError, ConnectionError) as e:
            # traceback.print_exc(e)
            # print e
            if t == 15:
                raise e
            else:
                self.set_proxy()
                return self.post_request(url, t+1, **kwargs)

    def set_proxy(self, force_change=True):
        ts = long(time.time())
        if ts - self.proxy_last_update_ts > 45 or force_change:
            print u'更换代理'
            proxy = get_proxy()
            self.session.proxies = {'http': proxy, 'https': proxy}
            self.proxy_last_update_ts = long(time.time())
        else:
            print u'不更换代理'