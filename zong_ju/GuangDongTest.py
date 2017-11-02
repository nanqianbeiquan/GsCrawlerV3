# coding=utf-8

from gs.Searcher import Searcher
from gs import TimeUtils
import json
from geetest_broker.GeetestBroker import GeetestBrokerOffline


class GuangDongSearcher(Searcher, GeetestBrokerOffline):

    xydm = None
    zch = None
    province = u'工商总局'

    def __init__(self):
        super(GuangDongSearcher, self).__init__(use_proxy=True)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:45.0) Gecko/20100101 Firefox/45.0',
        }

    def get_gt_challenge(self):
        url_1 = 'http://gd.gsxt.gov.cn/aiccips//verify/start.html?t=%s' % TimeUtils.get_cur_ts_mil()
        r_1 = self.get_request(url_1)
        self.challenge = str(json.loads(r_1.text)['challenge'])

    def get_tag_a_from_page(self, keyword, flags=True):
        validate = self.get_geetest_validate()
        url_1 = "http://gd.gsxt.gov.cn/aiccips/verify/sec.html"
        params_1 = {
            'textfield': keyword,
            'geetest_challenge': self.challenge,
            'geetest_validate': validate,
            'geetest_seccode': '%s|jordan' % validate
        }
        r_1 = self.post_request(url=url_1, params=params_1)
        textfield = json.loads(r_1.text)['textfield']
        print r_1.text
        url_2 = "http://gd.gsxt.gov.cn/aiccips/CheckEntContext/showCheck.html"
        params_2 = {
            'textfield': textfield,
            'type': 'nomal',
        }
        print params_2
        r_2 = self.post_request(url_2, params=params_2)
        print r_2.text

if __name__ == '__main__':
    searcher = GuangDongSearcher()
    searcher.get_tag_a_from_page(u'华为技术有限公司')
