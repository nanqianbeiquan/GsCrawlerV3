# coding=utf-8

from gs.SpiderMan import SpiderMan
from gs import TimeUtils
import os
from PIL import Image
import uuid
import random
from bs4 import BeautifulSoup
import re


class BJQYXY(SpiderMan):

    tmp_ts = None
    credit_ticket = None

    def __init__(self):
        super(BJQYXY, self).__init__(keep_ip=True, keep_session=True)
        self.init_cookie()

    def init_cookie(self):
        # self.get_request('http://qyxy.baic.gov.cn/')
        url = "http://qyxy.baic.gov.cn/simple/dealSimpleAction!transport_ww.dhtml?fourth=fourth&sysid=0150008788304366b7d3903b5067bb8c&module=wzsy&styleFlag=sy"
        r = self.get_request(url, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:52.0) Gecko/20100101 Firefox/52.0",
            "Host": "qyxy.baic.gov.cn",
            "Referer": "http://qyxy.baic.gov.cn/"
        })
        # print r.text
        self.credit_ticket = re.search('var credit_ticket = ".*?"', r.text).group().split('"')[1]
        print self.credit_ticket
        # print r.headers

    def submit_search_request(self):
        pass

    def get_tag_a_from_page(self, keyword):
        cur_ts_mil = TimeUtils.get_cur_ts_mil()
        yzm_url = "http://qyxy.baic.gov.cn/CheckCodeYunSuan?currentTimeMillis=%s" % cur_ts_mil
        yzm = self.get_yzm(yzm_url)
        print 'yzm', yzm
        check_url = "http://qyxy.baic.gov.cn/login/loginAction!checkCode.dhtml?check_code=%s&currentTimeMillis=%s&random=%s" \
                    % (yzm, cur_ts_mil, random.randint(10000, 100000))
        print check_url
        r = self.post_request(check_url, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:52.0) Gecko/20100101 Firefox/52.0",
            "Host": "qyxy.baic.gov.cn",
        })
        print r.text

        search_url = "http://qyxy.baic.gov.cn/es/esAction!entlist.dhtml?currentTimeMillis=%s&credit_ticket=%s&check_code=%s" % (cur_ts_mil, self.credit_ticket, yzm)
        print search_url
        params = {
            'idFlag': 'qyxy',
            'module': '',
            'queryStr': keyword,
            'currentTimeMillis': cur_ts_mil,
            'credit_ticket': self.credit_ticket,
            'check_code': yzm
        }
        print params
        search_url = "http://qyxy.baic.gov.cn/es/esAction!entlist.dhtml?currentTimeMillis="+cur_ts_mil+"&credit_ticket="+self.credit_ticket+"&check_code="+yzm+"&idFlag=qyxy&module=&queryStr=%E9%94%A4%E5%AD%90%E7%A7%91%E6%8A%80"
        print search_url
        r = self.post_request(search_url, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:52.0) Gecko/20100101 Firefox/52.0",
            "Host": "qyxy.baic.gov.cn",
            # "Content-Length": "0",
            # "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            # "Accept-Encoding": "gzip, deflate",
            # "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
            # "Connection": "keep-alive",
            # "Upgrade-Insecure-Requests": "1",
            # "Referer": "http://qyxy.baic.gov.cn/simple/dealSimpleAction!transport_ww.dhtml?fourth=fourth&sysid=0150008788304366b7d3903b5067bb8c&module=wzsy&styleFlag=sy",
        })
        r.encoding = 'utf-8'
        print r.text
        print self.session.cookies

    def get_yzm(self, yzm_url):
        # self.get_captchaid()
        yzm_path = self.download_yzm(yzm_url)
        yzm = self.recognize_yzm(yzm_path)
        os.remove(yzm_path)
        # print yzm_path
        # print 'yzm', yzm
        return yzm

    def get_captchaid(self):
        pass

    @staticmethod
    def recognize_yzm(yzm_path):
        """
            输入验证码保存路径,识别验证码
            :param yzm_path: 验证码路径
            :return: 验证码识别结果
            """
        image = Image.open(yzm_path)
        image.show()
        print '请输入验证码:'
        yzm = raw_input()
        image.close()
        # os.remove(path)
        return yzm

    def download_yzm(self, image_url, yzm_path=None):
        r = self.get_request(url=image_url)
        if not yzm_path:
            yzm_path = self.get_yzm_path()
        with open(yzm_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
                    f.flush()
            f.close()
        return yzm_path

    @staticmethod
    def get_yzm_path():
        return os.path.join(os.path.dirname(__file__), '../temp/' + str(uuid.uuid1()) + '.jpg')


if __name__ == "__main__":
    bj = BJQYXY()
    bj.get_tag_a_from_page(u"锤子科技")

