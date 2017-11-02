# coding=utf-8

from gs.Searcher import Searcher
from gs import TimeUtils
import json
from geetest_broker.GeetestBroker import GeetestBrokerOffline
from bs4 import BeautifulSoup
import platform
if platform.system() == 'Windows':
    import PyV8
else:
    from pyv8 import PyV8


class ShanDongSearcher(Searcher, GeetestBrokerOffline):

    xydm = None
    zch = None
    province = u'工商总局'
    csrf = None

    def __init__(self):
        super(ShanDongSearcher, self).__init__(use_proxy=True)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:45.0) Gecko/20100101 Firefox/45.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
        }

    def get_csrf(self):
        # self.session.proxies = None
        url_1 = "http://sd.gsxt.gov.cn"
        print url_1
        r_1 = self.get_request(url=url_1)
        print '-'*100
        print r_1.headers
        # print r_1.text
        soup_1 = BeautifulSoup(r_1.text, 'lxml')

        if len(soup_1.select('input[name=_csrf]')) == 0:
            self.set_cookie(r_1.text)
            print '+'*100
            _r = self.get_request('http://sd.gsxt.gov.cn/?ad_check=1')
            print '*'*100
            soup_1 = BeautifulSoup(_r.text, 'html5lib')
        self.csrf = soup_1.select('input[name=_csrf]')[0].attrs['value']
        # self.session.cookies.clear(domain='sd.gsxt.gov.cn', path='/', name='AD_VALUE')
        # if self.use_proxy:
        #     self.session.proxies = self.proxy_config.get_proxy()

    def get_gt_challenge(self):
        ts_1 = TimeUtils.get_cur_ts_mil()
        url_1 = "http://sd.gsxt.gov.cn/pub/geetest/register/%s?_=%s" % (TimeUtils.get_cur_ts_mil(), ts_1)
        r_1 = self.get_request(url_1)
        self.challenge = str(json.loads(r_1.text)['challenge'])

    def get_tag_a_from_page(self, keyword, flags=True):
        self.headers['Host'] = 'sd.gsxt.gov.cn'
        self.headers['Referer'] = 'http://www.gsxt.gov.cn/index.html'
        # url_1 = "http://sd.gsxt.gov.cn"
        # r_1 = self.get_request(url=url_1)
        # # print r_1.text
        # soup_1 = BeautifulSoup(r_1.text, 'lxml')
        # if len(soup_1.select('input[name=_csrf]')) == 0:
        #     self.set_cookie(r_1.text)
        #     _r = self.get_request('http://sd.gsxt.gov.cn/?ad_check=1')
        #     soup_1 = BeautifulSoup(_r.text, 'html5lib')
        #
        # _csrf = soup_1.select('input[name=_csrf]')[0].attrs['value']
        self.csrf = None
        print self.lock_id
        if not self.csrf:
            self.get_csrf()
        url_4 = "http://sd.gsxt.gov.cn/pub/query/"
        params_4 = {
            'isjyyc': 0,
            'isyzwf': 0,
            'keyword': keyword,
        }
        # print params_4
        self.headers['X-CSRF-TOKEN'] = self.csrf
        r_4 = self.post_request(url_4, params=params_4)
        print r_4.text
        print r_4.headers

    def set_cookie(self, html_text):
        ctxt = PyV8.JSContext()
        ctxt.enter()
        soup = BeautifulSoup(html_text, 'html5lib')
        js = soup.select('script')[0].text
        js = js.replace('eval', 'return')
        js = str("(function(){%s})" % js)
        f = ctxt.eval(js)
        res = f()
        a = res.split(';')[0].split('=')[1].strip('"')
        self.session.cookies.set(name='AD_VALUE', value=a, domain='sd.gsxt.gov.cn', path='/')

        # r = self.get_request('http://sd.gsxt.gov.cn/?ad_check=1')
        # print r.text

if __name__ == '__main__':
    searcher = ShanDongSearcher()
    searcher.get_lock_id()
    searcher.get_tag_a_from_page(u'烟台润畅商务咨询有限公司')
    searcher.release_lock_id()
    # searcher.get_tag_a_from_page(u'山东钢铁集团房地产有限公司')
    # searcher.get_tag_a_from_page(u'山东南融房地产开发有限公司')
    # searcher.get_tag_a_from_page(u'山东南兴房地产开发有限公司')
    # searcher.get_tag_a_from_page(u'山东永茂房地产开发有限公司')
