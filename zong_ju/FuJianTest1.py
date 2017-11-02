# coding=utf-8

from gs.Searcher import Searcher
from gs import TimeUtils
import json
from geetest_broker.GeetestBroker import GeetestBrokerOffline
import re


class FuJianSearcher(Searcher, GeetestBrokerOffline):

    xydm = None
    zch = None
    province = u'工商总局'
    token = None

    def __init__(self):
        super(FuJianSearcher, self).__init__(use_proxy=False)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:45.0) Gecko/20100101 Firefox/45.0',
        }

    def get_token(self):
        url = 'http://fj.gsxt.gov.cn/notice'
        r = self.get_request(url)
        print '#'*10, r.text
        # token_pattern = re.compile(r'"session.token": "[\w-]{36}"')
        # self.token = json.loads('{'+token_pattern.search(r.text).group()+'}')['session.token']
        # print '#'*10, self.token

    def get_gt_challenge(self):
        url_1 = 'http://fj.gsxt.gov.cn/notice/pc-geetest/register?t=%s' % TimeUtils.get_cur_ts_mil()
        r_1 = self.get_request(url_1)
        self.challenge = str(json.loads(r_1.text)['challenge'])
        self.gt = str(json.loads(r_1.text)['gt'])

    def get_tag_a_from_page(self, keyword, flags=True):
        validate = self.get_geetest_validate()

        # url_1 = "http://sh.gsxt.gov.cn/notice/security/verify_ip"
        # r_1 = self.post_request(url_1)
        # print r_1.text
        #
        # url_2 = "http://sh.gsxt.gov.cn/notice/security/verify_keyword"
        # params_2 = {
        #     'keyword': keyword
        # }
        # r_2 = self.post_request(url_2, params=params_2)
        # print r_2.text

        url_3 = "http://fj.gsxt.gov.cn/notice/pc-geetest/validate"
        params_3 = {
            'geetest_challenge': self.challenge,
            'geetest_validate': validate,
            'geetest_seccode': '%s|jordan' % validate,
        }
        # print '@'*10, params_3
        self.headers['Referer'] = 'http://sh.gsxt.gov.cn/notice/home'
        r_3 = self.post_request(url_3, params=params_3)
        print '@'*10, r_3.text

        url_4 = "http://fj.gsxt.gov.cn/notice/search/ent_info_list"
        params_4 = {
            'condition.searchType': '1',
            'captcha': '',
            'geetest_challenge': self.challenge,
            'geetest_validate': validate,
            'geetest_seccode': '%s|jordan' % validate,
            'session.token': self.token,
            'condition.keyword': keyword,
        }
        r_4 = self.post_request(url=url_4, params=params_4)
        print '&'*10, r_4.text

if __name__ == '__main__':
    searcher = FuJianSearcher()
    searcher.get_token()
    searcher.get_tag_a_from_page(u'百威英博雪津啤酒有限公司')