# coding=utf-8

from gs.Searcher import Searcher
from gs import TimeUtils
from geetest_broker.GeetestBroker import GeetestBrokerRealTime
import json
import random
from geetest_broker import ZheJiangKeywordEncoder
import os
from geetest_broker.GeetestBreak import GeetestBreak
'''
create table enterprise_credit_info.tag_a_zj
(mc varchar(255) primary key
,xydm varchar(50)
,zch varchar(50)
,tag_a varchar(255)
);
create index xydm_idx on tag_a_zj(xydm);
'''


class ZongJuSearcher(Searcher, GeetestBrokerRealTime):

    xydm = None
    zch = None
    province = u'浙江省'

    def __init__(self):
        super(ZongJuSearcher, self).__init__(use_proxy=True)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:45.0) Gecko/20100101 Firefox/45.0'
        }
        self.set_geetest_config()

    def set_geetest_config(self):
        self.geetest_product = 'popup'
        self.geetest_referer = 'http://zj.gsxt.gov.cn/client/entsearch/toEntSearch'

    def get_gt_challenge(self):
        url_1 = "http://zj.gsxt.gov.cn/pc-geetest/register?t=%s" % TimeUtils.get_cur_ts_mil()
        self.info(u'获取gt和challenge...')
        r_1 = self.get_request(url_1)
        json_1 = json.loads(r_1.text)
        self.gt = json_1['gt']
        self.challenge = json_1['challenge']

    def get_token(self):
        self
        return str(random.randint(50000000, 60000000))

    def get_tag_a_from_page(self, mc='', xydm=''):
        if mc:
            keyword = mc
        else:
            keyword = xydm
        if type(keyword) == unicode:
            keyword = keyword.encode('utf-8')
        self.headers['Referer'] = self.geetest_referer
        url_2 = 'http://zj.gsxt.gov.cn/client/entsearch/list?isOpanomaly=&pubType=1&searchKeyWord=%s' % ZheJiangKeywordEncoder.encode_keywoed(keyword)
        r_2 = self.get_request(url_2)
        print r_2.text


if __name__ == '__main__':
    # test()
    searcher = ZongJuSearcher()
    searcher.get_tag_a_from_page(u'阿里巴巴（中国）有限公司')