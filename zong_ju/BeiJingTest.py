# coding=utf-8

from gs.SpiderMan import SpiderMan
from gs import TimeUtils
import json
from geetest_broker.GeetestBroker import GeetestBrokerRealTime


class BeiJingSearcher(SpiderMan, GeetestBrokerRealTime):

    xydm = None
    zch = None
    province = u'北京市'

    def __init__(self):
        super(BeiJingSearcher, self).__init__(keep_session=True, keep_ip=True)
        self.set_geetest_config()

    def set_geetest_config(self):
        self.geetest_product = 'popup'
        self.geetest_referer = 'http://bj.gsxt.gov.cn/sydq/loginSydqAction!sydq.dhtml'

    def get_gt_challenge(self):
        url_1 = 'http://bj.gsxt.gov.cn/pc-geetest/register?t=%s' % TimeUtils.get_cur_ts_mil()
        # print url_1
        r_1 = self.get_request(url_1)
        self.challenge = str(json.loads(r_1.text)['challenge'])
        self.gt = str(json.loads(r_1.text)['gt'])
        # print 'self.challenge', self.challenge

    def get_tag_a_from_page(self, keyword, flags=True):
        self.get_request('http://bj.gsxt.gov.cn/sydq/loginSydqAction!sydq.dhtml')
        validate = self.get_geetest_validate()
        print 'validate', validate

        # self.headers['Host'] = 'bj.gsxt.gov.cn'
        # self.headers['Referer'] = 'http://bj.gsxt.gov.cn/sydq/loginSydqAction!sydq.dhtml'
        # self.headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        # self.headers['Accept-Language'] = 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3'
        # self.headers['Accept-Encoding'] = 'gzip, deflate'
        # self.headers['Connection'] = 'keep-alive'

        url_1 = "http://bj.gsxt.gov.cn/pc-geetest/validate"
        params_1 = {
            'geetest_challenge': self.challenge,
            'geetest_validate': validate,
            'geetest_seccode': '%s|jordan' % validate,
        }
        r_1 = self.post_request(url=url_1, params=params_1,
                                headers={'Host': 'bj.gsxt.gov.cn',
                                         'Referer': 'http://bj.gsxt.gov.cn/sydq/loginSydqAction!sydq.dhtml',
                                })
        print r_1.text
        print 'self.challenge', self.challenge
        url_2 = "http://bj.gsxt.gov.cn/es/esAction!entlist.dhtml?urlflag=0&challenge="+self.challenge
        print url_2
        data_2 = {
            'keyword': keyword,
            'nowNum': '',
            'clear': '请输入企业名称、统一社会信用代码或注册号',
            'urlflag': '0',
        }
        r_2 = self.post_request(url_2, params=data_2)
        r_2.encoding = 'utf-8'
        print r_2.text
        print r_2.headers

if __name__ == '__main__':
    searcher = BeiJingSearcher()
    # searcher.get_lock_id()
    searcher.get_tag_a_from_page(u'联想（北京）有限公司'.encode('utf-8'))
