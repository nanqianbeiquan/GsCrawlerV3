# coding=utf-8

from gs.Crawler import Crawler
import re
import os
import json
import TimeUtils
from GeetestBreak import GeetestBreak
import time


class Geetest(Crawler):

    api_json = {}
    static_url = None
    slice_url = None
    bg_url = None
    fullbg_url = None
    fullbg_path = None
    fullbg_recovery_path = None
    slice_path = None
    bg_path = None
    bg_recovery_path = None
    gid = None
    log_name = 'BreakTest'
    province = u'工商总局'

    def __init__(self, api_url):
        self.headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:45.0) Gecko/20100101 Firefox/45.0',
            # 'Host': 'api.geetest_broker.com',
        }
        super(Geetest, self).__init__(use_proxy=False)
        self.api_url = api_url
        self.ts = re.compile('t=[^&]+').search(self.api_url).group()[2:]
        r = self.get(api_url)
        gt_dict = json.loads(r.text)
        self.gt = gt_dict['gt']
        self.challenge = gt_dict['challenge']
        print r.text
        self.get('http://api.geetest_broker.com/gettype.php?gt=%s&callback=geetest_1483521053837' % self.gt)

    def get_api(self):
        # url = "http://api.geetest.com/get.php?" \
        #       "gt=%s" \
        #       "&challenge=%s" \
        #       "&product=popup" \
        #       "&offline=false" \
        #       "&protocol=" \
        #       "&type=slide" \
        #       "&path=/static/js/geetest_broker.5.6.1.js" \
        #       "&callback=geetest_%s" % (self.gt, self.challenge, self.ts)
        url = "http://api.geetest_broker.com/get.php?" \
              "gt=%s" \
              "&challenge=%s" \
              "&product=embed" \
              "&offline=false" \
              "&protocol=" \
              "&type=slide" \
              "&path=/static/js/geetest_broker.5.7.0.js" \
              "&callback=geetest_%s" % (self.gt, self.challenge, self.ts)
        r = self.get(url)
        self.api_json = json.loads(r.text[r.text.find('{'):r.text.rfind('}')+1])
        self.challenge = self.api_json['challenge']
        print self.api_json

    def download_image(self):
        self.headers['Host'] = 'static.geetest_broker.com'
        self.static_url = self.api_json['staticservers'][0]
        self.slice_url = 'http://'+self.static_url + self.api_json['slice']
        self.bg_url = 'http://'+self.static_url + self.api_json['bg']
        self.fullbg_url = 'http://'+self.static_url + self.api_json['fullbg']
        self.bg_path = os.path.join(os.path.dirname(__file__), '../temp/bg.jpg')
        self.slice_path = os.path.join(os.path.dirname(__file__), '../temp/slice.jpg')
        self.fullbg_path = os.path.join(os.path.dirname(__file__), '../temp/fullbg.jpg')
        self.download_yzm(self.fullbg_url, self.fullbg_path)
        self.download_yzm(self.bg_url, self.bg_path)
        self.download_yzm(self.slice_url, self.slice_path)
        # self.recovery_image(self.bg_path)
        # self.recovery_image(fullbg_path)

if __name__ == '__main__':
    # geetest_broker = Geetest('http://www.gsxt.gov.cn/SearchItemCaptcha?v=%s' % TimeUtils.get_cur_ts_mil())
    geetest = Geetest('http://localhost:8000/pc-geetest_broker/register?t=1483521044641')
    geetest.get_api()
    geetest.download_image()
    # print 'geetest_broker.bg_path', geetest_broker.bg_path
    # print 'geetest_broker.fullbg_path', geetest_broker.fullbg_path
    # print 'geetest_broker.slice_path', geetest_broker.slice_path
    # print 'geetest_broker.challenge', geetest_broker.challenge
    # print 'geetest_broker.gt', geetest_broker.gt
    gtb = GeetestBreak(bg_path=geetest.bg_path, full_bg_path=geetest.fullbg_path, slice_path=geetest.slice_path,
                       challenge=geetest.challenge, gt=geetest.gt)
    params = gtb.get_break_params()
    print params
    geetest.headers['Host'] = 'api.geetest_broker.com'
    geetest.headers['Referer'] = 'http://localhost:8000/'
    time.sleep(2)
    r = geetest.get(url='http://api.geetest_broker.com/ajax.php', params=params)
    print r.text

