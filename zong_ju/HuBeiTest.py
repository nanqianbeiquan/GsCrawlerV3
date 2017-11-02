# coding=utf-8

from gs.Searcher import Searcher
from gs import TimeUtils
import json
from geetest_broker.GeetestBroker import GeetestBrokerOffline
import re
import urllib
import time
from gs import SpiderMan
from selenium import webdriver


class HuBeiSearcher(SpiderMan.SpiderMan, GeetestBrokerOffline):
    xydm = None
    zch = None
    province = u'湖北省'
    token = None

    def __init__(self):
        super(HuBeiSearcher, self).__init__(keep_session=True, keep_ip=True)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:45.0) Gecko/20100101 Firefox/45.0',
        }
        self.set_geetest_config()

    def set_geetest_config(self):
        self.geetest_referer = "http://hb.gsxt.gov.cn/index.jspx"
        self.geetest_product = "popup"

    def get_gt_challenge(self, t=0):
        if t == 15:
            raise Exception(u'获取gt和challenge失败')
        url_1 = 'http://hb.gsxt.gov.cn/registerValidate.jspx?t=%s' % TimeUtils.get_cur_ts_mil()
        r_1 = self.get_request(url_1)

        # print r_1.text, r_1.text.strip().startswith('{'), r_1.text.strip().endswith('}')
        if r_1.text.strip().startswith('{') and r_1.text.strip().endswith('}'):
            self.challenge = str(json.loads(r_1.text)['challenge'])
            self.gt = str(json.loads(r_1.text)['gt'])
            print self.challenge, self.gt
        else:
            time.sleep(1)
            self.reset_session()
            self.get_gt_challenge(t + 1)

    def get_tag_a_from_page(self, keyword):
        # r1 = self.get('http://hb.gsxt.gov.cn/index.jspx')
        # print r1.text
        self.session.cookies.set('BSFIT_EXPIRATION', '1505775296463', path='hb.gsxt.gov.cn/')
        self.session.cookies.set('BSFIT_4im02', '', path='hb.gsxt.gov.cn/')
        self.session.cookies.set('fp_ver', '', path='hb.gsxt.gov.cn/')
        self.session.cookies.set('BSFIT_OkLJUJ', 'FDL6QcHfvpXtcSqZV9S88012Uf_vZ8G1', path='hb.gsxt.gov.cn/')
        self.session.cookies.set('BSFIT_DEVICEID', 'L9KOcSYOmJRZzkrHS7o9agdrEcMYUbQPA6e-fMzkX88rbqNBZKf4NrjxWR4Tx-ewur-YTOTpO'
                                                   '6fB-Tk2qXiQDvVZv5mlqOYiHi8ssWtHfog3Q44rDkt3EuceNAD3ksy7q_lrk'
                                                   'xqQAXc0dEeenwaREZPsIc_efGj', path='hb.gsxt.gov.cn/')

        validate = self.get_geetest_validate()
        print validate
        url_3 = "http://hb.gsxt.gov.cn/validateSecond.jspx"
        params_3 = {
            'geetest_challenge': self.challenge,
            'geetest_validate': validate,
            'geetest_seccode': '%s|jordan' % validate,
            'searchText': keyword
        }
        r_3 = self.post_request(url_3, params=params_3)
        print r_3.text
        obj = json.loads(r_3.text)['obj']
        url_4 = 'http://hb.gsxt.gov.cn/' + obj +'&searchType=1&entName=' + urllib.quote(urllib.quote(keyword.encode('utf-8')))
        print url_4
        print self.session.cookies
        r_4 = self.get(url_4, headers={
            'Host': 'hb.gsxt.gov.cn',
            'Referer': 'http://hb.gsxt.gov.cn/index.jspx',
        })
        r_4.encoding = 'utf-8'
        print r_4.text


if __name__ == '__main__':
    # searcher = HuBeiSearcher()
    # searcher.get_tag_a_from_page(u'武汉房地产')
    driver = webdriver.Firefox()
    driver.get('http://dfp2.bangruitech.com/public/downloads/frms-fingerprint.js?custID=51&version=4.3.2&include=rd&include=ajaxInject&timestamp=1505692800')
    time.sleep(10)
    print driver.get_cookies()
    driver.close()