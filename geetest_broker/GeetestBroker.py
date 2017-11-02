# coding=utf-8

import requests
from gs import TimeUtils
import json
from gs.MyException import GeetestTrailException
import os
import uuid
from GeetestJS import get_validate_offline
import time
from PIL import Image
import BreakTrail
import GeetestParamsBroker
import random
from io import BytesIO
import GeetestDistanceV2


class GeetestBrokerRealTime(object):

    # 极验参数-临时变量
    # bg_path = os.path.join(os.path.dirname(__file__), '../temp/' + str(uuid.uuid1()) + '.jpg')
    # fullbg_path = None
    # slice_path = os.path.join(os.path.dirname(__file__), '../temp/' + str(uuid.uuid1()) + '.jpg')
    bg_url = None
    fullbg_url = None
    slice_url = None
    challenge = None
    gt = None
    token = None
    validate = None
    y_pos = None
    static_server = None
    use_proxy = True
    c = None
    s = None

    # 极验参数-配置变量
    geetest_js_path = None  #
    geetest_product = None  #
    geetest_referer = None  #

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:45.0) Gecko/20100101 Firefox/45.0'
        }
        self.set_geetest_config()
        if not self.session:
            self.session = requests.session()

    @staticmethod
    def info(msg):
        try:
            print TimeUtils.get_cur_time() + ' ->', msg
        except UnicodeEncodeError:
            pass

    def set_geetest_config(self):
        self.geetest_js_path = None
        self.geetest_product = None
        self.geetest_referer = None

    def get_gt_challenge(self):
        url_1 = "http://www.gsxt.gov.cn/SearchItemCaptcha?v=%s" % TimeUtils.get_cur_ts_mil()
        # print url_1
        self.info(u'**获取gt和challenge...')
        r_1 = self.get(url_1)
        json_1 = json.loads(r_1.text)
        self.gt = json_1['gt']
        self.challenge = json_1['challenge']

    def load_api(self):
        self.info(u'获取极验api...')
        ts = TimeUtils.get_cur_ts_mil()
        url_1 = 'http://api.geetest.com/gettype.php?gt=%s&callback=geetest_%s' % (self.gt, ts)
        # print 'url_1', url_1
        r_1 = self.get(url_1)
        # print r_1.text
        # print r_1.text[len('geetest_%s(' % ts):-1]
        if 'data' in json.loads(r_1.text[len('geetest_%s(' % ts):-1]):
            path = json.loads(r_1.text[len('geetest_%s(' % ts):-1])['data']['path']
        else:
            path = json.loads(r_1.text[len('geetest_%s(' % ts):-1])['path']
        url_2 = "http://api.geetest.com/get.php?" \
                "gt=%s" \
                "&challenge=%s" \
                "&product=%s" \
                "&offline=false" \
                "&protocol=" \
                "&type=slide" \
                "&path=%s" \
                "&callback=geetest_%s" % (self.gt, self.challenge, self.geetest_product, path, TimeUtils.get_cur_ts_mil())
        # print 'url_2', url_2
        r_2 = self.get(url_2, headers={})
        # print r_2.text
        json_2 = json.loads(r_2.text[r_2.text.find('{'):r_2.text.rfind('}') + 1])
        self.s = json_2['s']
        self.c = json_2['c']
        if 'staticservers' in json_2:
            self.static_server = json_2['staticservers'][0]
            self.bg_url = 'http://' + self.static_server + json_2['bg']
            self.fullbg_url = 'http://' + self.static_server + json_2['fullbg']
            self.slice_url = 'http://' + self.static_server + json_2['slice']
            self.challenge = json_2['challenge']
        elif 'static_servers' in json_2:
            self.static_server = json_2['static_servers'][0]
            self.bg_url = 'http://' + self.static_server + json_2['bg']
            self.fullbg_url = 'http://' + self.static_server + json_2['fullbg']
            self.slice_url = 'http://' + self.static_server + json_2['slice']
            self.challenge = json_2['challenge']
        else:
            self.session.cookies.clear(domain='api.geetest.com')
            self.get_gt_challenge()
            self.load_api()

    def refresh_api(self):
        self.info(u'轨迹有误，刷新极验api...')
        url_2 = "http://api.geetest.com/refresh.php?" \
                "challenge=%s" \
                "&gt=%s" \
                "&callback=geetest_%s" % (self.challenge, self.gt, TimeUtils.get_cur_ts_mil())
        r_2 = self.get(url_2)
        # print r_2.text
        json_2 = json.loads(r_2.text[r_2.text.find('{'):r_2.text.rfind('}') + 1])
        self.bg_url = 'http://' + self.static_server + json_2['bg']
        self.fullbg_url = 'http://' + self.static_server + json_2['fullbg']
        self.slice_url = 'http://' + self.static_server + json_2['slice']
        self.challenge = json_2['challenge']

    # def get(self, **kwargs):
    #     pass

    def break_params(self):
        bg_img = self.down_geetest_img(self.bg_url)
        slice_img = self.down_geetest_img(self.slice_url)
        fullbg_path = os.path.join(os.path.dirname(__file__), '../data/fullbg/' + self.fullbg_url.split('/')[-1])
        if not os.path.exists(fullbg_path):
            print u'New fullbg image'
            fullbg_img = self.down_geetest_img(self.fullbg_url)
            fullbg_img.save(fullbg_path)
        fullbg_img = Image.open(fullbg_path)
        distance = GeetestDistanceV2.get_distance(bg_img, fullbg_img, slice_img)
        # print 'distance->', distance
        trail_arr = BreakTrail.get_trali_arr(distance)
        # print 'distance:', distance
        pass_time = trail_arr[-1][-1]
        # print trail_arr
        params = {
            'challenge': str(self.challenge),
            'gt': str(self.gt),
            'userresponse': GeetestParamsBroker.imitate_userrespose(distance, self.challenge),
            'passtime': pass_time,
            'imgload': random.randint(70, 150),
            'aa': GeetestParamsBroker.imitate_aa(trail_arr, self.c, self.s),
            'callback': 'geetest_%s' % TimeUtils.get_cur_ts_mil(),
        }
        # print json.dumps(params, indent=4)
        return params, trail_arr[-1][2]

    def get_geetest_validate(self, t=1):
        if t == 1:
            self.get_gt_challenge()
            self.load_api()
        else:
            self.refresh_api()
        if t == 4:
            raise GeetestTrailException()
        ts1 = time.time()
        # gtb = GeetestBreak(bg_path=self.bg_path, full_bg_path=self.fullbg_path, slice_path=self.slice_path,
        #                    challenge=self.challenge, gt=self.gt)
        params, trail_time = self.break_params()
        img_load = params['imgload']
        ts2 = time.time()
        delta_ta = (trail_time + img_load) / 1000.0
        if ts2-ts1 < delta_ta:
            # print 'sleep', delta_ta - (ts2 - ts1)
            time.sleep(delta_ta - (ts2 - ts1) + .5)
        # time.sleep(0.5)
        url_3 = "http://api.geetest.com/ajax.php"
        self.info(u'获取validate...')
        # time.sleep(2)
        r_3 = self.get(url=url_3, params=params, headers={'Referer': self.geetest_referer})
        # print r_3.text
        json_3 = json.loads(r_3.text[r_3.text.find('{'):r_3.text.rfind('}')+1])
        if 'validate' in json_3:
            self.info(u'获取validate成功')
            return json_3['validate']
        else:
            self.info(u'验证码滑动轨迹有误，重试')
            return self.get_geetest_validate(t+1)

    def down_geetest_img(self, img_url):
        r = self.get(img_url)
        return Image.open(BytesIO(r.content))


class GeetestBrokerOffline(GeetestBrokerRealTime):

    def get_geetest_validate(self, t=1):
        self.get_gt_challenge()
        return get_validate_offline(self.challenge)


if __name__ == '__main__':
    # geetest = GeetestBrokerRealTime()
    # print geetest.get_geetest_validate()
    geetest2 = GeetestBrokerOffline()
    # geetest2.load_offline_js()
