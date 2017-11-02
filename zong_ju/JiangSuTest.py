# coding=utf-8

from gs.Searcher import Searcher
from gs import TimeUtils
import json
import random
from geetest_broker.GeetestBroker import GeetestBrokerRealTime
import os
from geetest_broker.GeetestDistance import GeetestDistance
from geetest_broker.GeetestBreak import GeetestBreak
from gs.MyException import GeetestTrailException
'''
create table enterprise_credit_info.tag_a_zj
(mc varchar(255) primary key
,xydm varchar(50)
,zch varchar(50)
,tag_a varchar(255)
);
create index xydm_idx on tag_a_zj(xydm);
'''


class JiangSuSearcher(Searcher, GeetestBrokerRealTime):

    xydm = None
    zch = None
    province = u'江苏省'

    def __init__(self):
        super(JiangSuSearcher, self).__init__(use_proxy=True)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:45.0) Gecko/20100101 Firefox/45.0',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest',
        }
        self.set_geetest_config()

    def set_geetest_config(self):
        self.geetest_product = 'popup'
        self.geetest_referer = 'http://www.jsgsj.gov.cn:58888/province/'

    def get_gt_challenge(self):
        url_1 = "http://www.jsgsj.gov.cn:58888/province/geetestViladateServlet.json?register=true&t=%s" % TimeUtils.get_cur_ts_mil()
        self.info(u'获取gt和challenge...')
        r_1 = self.get_request(url_1)
        json_1 = json.loads(r_1.text)
        self.gt = json_1['gt']
        self.challenge = json_1['challenge']

    def get_token(self):
        self
        return str(random.randint(50000000, 60000000))

    def get_tag_a_from_page(self, mc, xydm):

        if mc:
            keyword = mc
        else:
            keyword = xydm

        validate = self.get_geetest_validate()
        self.headers['Host'] = 'www.jsgsj.gov.cn:58888'

        print validate
        url = "http://www.jsgsj.gov.cn:58888/province/geetestViladateServlet.json?validate=true"
        params = {
            'geetest_challenge': self.challenge,
            'geetest_seccode': '%s|jordan' % validate,
            'geetest_validate': validate,
            'name': keyword,
            'type': 'search',
        }
        print url
        r = self.post_request(url=url, data=params)
        name = json.loads(r.text)['name']

        url_3 = "http://www.jsgsj.gov.cn:58888/province/infoQueryServlet.json?queryCinfo=true"
        params_3 = {'name': str(name),
                    'pageNo': 1,
                    "pageSize": 10,
                    'searchType': 'qyxx'
                    }
        # print params_3
        # self.session.cookies.set(name='JSESSIONID', value=session_gsxt)
        self.headers['Referer'] = 'http://www.jsgsj.gov.cn:58888/province/jiangsu.jsp?typeName=%s&searchType=qyxx' % name
        r_3 = self.post_request(url=url_3, data=params_3)
        print r_3.text


if __name__ == '__main__':
    # test()
    searcher = JiangSuSearcher()
    searcher.get_tag_a_from_page(u'苏州博航房地产投资管理有限公司', '')
    # params_2 = {'typeName': '77998AFEF0F9E3F1A8733A619FBE1847E8B45B828A896A390C49B4E3DA699E5B',
    #             'pageNo': 1,
    #             'pageSize': 10,
    #             'searchType': 'qyxx'
    #             }                                             /
    # # searcher.get_request(url='http://www.jsgsj.gov.cn:58888/province/geetestViladateServlet.json?register=true&t=1484234584439')
    # r = searcher.post_request('http://www.jsgsj.gov.cn:58888/province/infoQueryServlet.json?queryCinfo=true', data=params_2)
    # print r.text
