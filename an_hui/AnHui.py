# coding=utf-8

import requests
import os
import uuid
import urllib
from urllib import quote
from PIL import Image
from bs4 import BeautifulSoup
import json
import re
from gs.KafkaAPI import KafkaAPI
import datetime
from requests.exceptions import RequestException
import sys
import platform
if platform.system() == 'Windows':
    import PyV8
else:
    from pyv8 import PyV8

import random
import subprocess
import time
from Tables_dict import *
from gs.Searcher import Searcher
from gs.Searcher import get_args
from gs.ProxyConf import *
from gs.TimeUtils import *
from gs.ProxyConf import ProxyConf, key1 as app_key
from requests.exceptions import ReadTimeout
from requests.exceptions import ConnectTimeout
from requests.exceptions import ProxyError
from requests.exceptions import ConnectionError
from requests.exceptions import ChunkedEncodingError
from gs.MyException import StatusCodeException
from geetest_broker.GeetestBroker import GeetestBrokerRealTime

class AnHui(Searcher, GeetestBrokerRealTime):
    """
    初始化参数
    :param json_result: 最终查询结果的json结果
    :param save_tag_a: 有查询结果时，对应公司信息的url地址，存入数据库里，有的省份用到
    :param flag: 查询内容为公司名称True或公司信用代码False
    :param lock_id: 查询过程可能需要锁定ip，分全程锁定和有查询结果锁定，0为不锁定IP，1为锁定
    :param cur_time: 部分查询内容可能用到的时间戳，查询一次有时间限制
    :param cur_mc: 查询结果名称
    :param cur_zch: 查询结果注册号
    :param entName: 企业名称
    :param entId: 企业信用代码
    :param entNo: 企业注册号
    :param creditt: 查询过程用到的通行证credit
    :param credit_ticket: 查询过程中需要用到的通行证credit，仅对单次查询有效
    :param iframe_src: 查询内容可能涉及异步ajax查询用的的iframe地址集合
    :param status_dict: 状态表，针对企业的查询结果的状态
    """

    json_result = {}
    pattern = re.compile("\s")
    save_tag_a = True
    flag = True
    lock_id = 0
    cur_time = None

    cur_mc = None
    cur_zch = None
    entName = None
    entId = None
    entNo = None
    creditt = None
    credit_ticket = None
    iframe_src = {}
    status_dict = {
    u'存续': 1, u'存续（在营、开业、在册）': 1, u'在业': 1, u'开业': 1,u'已开业': 1, u'在营':1, u'在营（开业）': 1,\
    u'在营（开业）企业': 1, u'吊销，未注销':2, u'吊销未注销': 2,u'吊销,未注销':2,u'吊销':3, u'吊销企业': 3,u'已吊销': 3,\
     u'拟注销': 4, u'注销': 5, u'已注销':5, u'注销企业': 5, u'吊销,已注销': 6,u'吊销，已注销': 6,u'注吊销': 6,\
    u'吊销后注销': 6,u'清算中': 7,u'其他': 8, u'个体转企业': 9, u'迁出': 10,u'迁移异地': 10, u'市外迁出': 10,u'已迁出企业': 10,\
    u'停业': 11,u'停业（个体工商户使用': 11,u'撤销登记': 12, u'撤消登记': 12, u'撤销': 12, u'待迁入': 13, \
    u'经营期限届满': 14,u'不明': 15,u'登记成立': 16,u'正常': 17,u'非正常户': 18,'2': 19,}

    def __init__(self, dst_topic=None):
        """
        设置查询结果存放的kafka的topic
        :param dst_topic: 调用kafka程序的目标topic，topic分测试环境和正式环境
        :return:
        """
        super(AnHui, self).__init__(use_proxy=True, dst_topic=dst_topic)
        # self.session = requests.session()
        # self.session.proxies = {'http': '123.56.238.200:8123', 'https': '123.56.238.200:8123'}
        # self.session.proxies = {'http': '121.28.134.29:80'}

        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:46.0) Gecko/20100101 Firefox/46.0',
        }
        # self.cur_time = '%d' % (time.time() * 1000)
        self.get_credit_ticket()
        self.json_result = {}  # json输出结果
        self.iframe_name = {'qyjbqk': u'基本信息', 'tzrczxx': u'股东信息', 'qybgxx': u'变更信息',
                           'qybaxxzyryxx': u'主要人员信息', 'qybaxxfgsxx': u'分支机构信息', 'qybaxxqsxx': u'清算信息',
                            'gqczxx': u'股权出质登记信息', 'dcdyxx': u'动产抵押登记信息', 'jyycxx':u'经营异常信息',
                            'yzwfxx': u'严重违法信息', 'xzcfxx': u'行政处罚信息', 'ccjcxx':u'抽查检查信息'}
        self.domain = 'http://ah.gsxt.gov.cn'
        # self.add_proxy(app_key)
        self.set_config()
        # self.log_name = self.topic + "_" + str(uuid.uuid1())
        self.set_geetest_config()

    def set_config(self):
        """
        参数配置
        :param self.province 查询结果的省份归类参数
        :return:
        """
        # headers = {}
        # rt = self.get_request('http://1212.ip138.com/ic.asp', headers=headers)
        # rt.encoding = 'gb2312'
        # print rt.text
        # self.plugin_path = sys.path[0] + r'\..\an_hui\ocr\pinyin.bat'
        # self.group = 'Crawler'  # 正式
        # self.kafka = KafkaAPI("GSCrawlerResult")  # 正式
        # self.group = 'CrawlerTest'  # 测试
        # self.kafka = KafkaAPI("GSCrawlerTest")  # 测试
        # self.topic = 'GsSrc34'

        self.province = u'安徽省'
        # self.kafka.init_producer()
        # try:
        #     self.go_cookies()
        # except AttributeError:
        #     pass

    def download_yzm(self):
        """
        下载验证码方法
        :return:
        """
        pass
        # self.lock_id = self.proxy_config.get_lock_id()
        # self.cur_time = '%d' % (time.time() * 1000)
        # params = {'currentTimeMillis': self.cur_time}
        # image_url = 'http://ah.gsxt.gov.cn/validateCode.jspx?type=2'
        # r = self.get_request(url=image_url, params={})
        # # print r.headers
        # # print r.status_code,r.text
        # yzm_path = os.path.join(sys.path[0], str(random.random())[2:]+'.jpg')
        # with open(yzm_path, 'wb') as f:
        #     for chunk in r.iter_content(chunk_size=1024):
        #         if chunk:  # filter out keep-alive new chunks
        #             f.write(chunk)
        #             f.flush()
        #     f.close()
        # return yzm_path

    def get_credit_ticket(self):
        """
        获取查询通行证credit方法
        :return:
        """
        # r = self.get_request('http://qyxy.baic.gov.cn/gjjbj/gjjQueryCreditAction!toIndex.dhtml')
        # print 'credit_headers',r.headers
        # soup = BeautifulSoup(r.text, 'lxml')
        # # print soup
        # self.credit_ticket = soup.select('input#credit_ticket')[0].attrs['value']
        pass

    def go_cookies(self):
        """
        获取查询请求cookie的方法，部分省份cookie进行了JS加密，用PyV8模块加载执行相应的JS代码得到结果
        :return:
        """
        url = 'http://ah.gsxt.gov.cn/search.jspx#'
        r = self.get_request(url=url)
        r.encoding = 'utf-8'
        set_cookie = [r.headers['Set-Cookie']]
        soup = BeautifulSoup(r.text, 'lxml')
        script = soup.select('script')[0].text
        script = script[len('eval(')+1:-1]
        # print 'script', script
        ctxt = PyV8.JSContext()
        ctxt.enter()
        res = ctxt.eval(script)
        # print 'eval_after', res
        res = res.replace('if(findDimensions()) {} else ', '')
        res = res.replace('window.location=dynamicurl', '')
        res = res.replace('document.cookie = cookieString;	var confirm = QWERTASDFGXYSF()', 'res=cookieString;	var confirm = QWERTASDFGXYSF()')
        res = res.replace("document.cookie = cookieString;", "res = res+', '+cookieString;return res")
        # print 'res', res
        js_res_text = ctxt.eval(res)
        # print 'dealt_JSresult', js_res_text
        set_cookie.extend(js_res_text.split(', '))
        # print set_cookie
        for x in set_cookie:
            y = x.split(';')[0]
            idx_1 = y.index('=')
            name = y[:idx_1]
            value = y[idx_1+1:]
            self.session.cookies.set(name=name, value=value, domain='ah.gsxt.gov.cn', path='/')

    def set_geetest_config(self):
        """
        极客滑动验证码参数的设置
        :return:
        """
        self.geetest_product = 'popup'
        self.geetest_referer = 'http://ah.gsxt.gov.cn/index.jspx'

    def get_gt_challenge(self):
        """
        极客验证码参数gt和challenge的获取方法，定位某次查询
        :return:
        """
        url_1 = 'http://ah.gsxt.gov.cn/registerValidate.jspx?t=%s' % get_cur_ts_mil()
        print url_1
        r_1 = self.get_request_302(url_1)
        # print r_1.text
        r_1.encoding = 'gbk'
        soup = BeautifulSoup(r_1.text,'html5lib')
        # print 'challenge_soup', soup
        if u'访问本页面，您的浏览器需要支持JavaScript' in soup.text:
            url = self.get_the_js_url(soup)
            r_1 = self.get_request(url)
            # print 'coco',r_1.text
        self.challenge = str(json.loads(r_1.text)['challenge'])
        self.gt = str(json.loads(r_1.text)['gt'])
        print 'self.challenge', self.challenge, 'gt', self.gt

    def get_the_js_url(self,soup):
            """
            cookie加密的js代码的提取，执行
            :param soup:  js代码返回内容
            :return: JS解密后的url
            """
            print '*'*10
            js = soup.find('script').text
            # print 'js', js
            jw = re.search(u',(\w{2});', js).group(1)
            try:
                tx = re.search(u'(?<=\);).{5,18}(?=;}%s)' %jw, js).group()
            except:
                tx = re.search(r'(?<=\);e).{5,18}(?=;}%s)' %jw, js).group()
            print 'jw', jw
            print 'tx', tx
            js = js.replace(tx, u'return %s;%s' %(jw, tx))
            # print 'jx', js
            jse = PyV8.JSContext()
            jse.enter()
            h = jse.eval(js)
            # h = jse.eval(mj)
            # print 'h', h
            if u'open' in h:
                h = h[h.index('(')+1:-9]
            elif u'location' in h:
                h = h[h.index('=')+1:]
            else:
                h = h
            # print 'h_', h
            cod = jse.eval(h)
            # print 'cod', cod
            url = self.domain + cod
            print 'rv_url', url
            return url

    def get_tag_a_from_db(self, keyword):
        """
        获取查询结果对应的标签内容
        :param keyword: 查询的内容
        :return:
        """
        return None

    def save_tag_a_to_db(self, keyword):
        """
        查询结果标签存入数据库的方法
        :param keyword: 查询的内容
        :return:
        """
        pass

    def get_the_mc_or_code(self, keyword):
        """
        判断keyword为企业名称或信用代码的简易方法
        :param keyword:
        :return: True为企业名称，False为信用代码或注册号
        """
        if keyword:
            if len(keyword) == 15 or len(keyword) == 18:
                cnt = 0
                for i in keyword:
                    if i in 'abcdefghijklmnopqrstuvwxyz1234567890':
                        cnt += 1
                if cnt > 10:
                    return False
            else:
                return True
        else:
            self.info(u'输入keyword有误')
            return True

    # def get_tag_a_from_page(self, keyword, ac=0):
    #     return self.get_tag_a_from_page0(keyword)

    # def get_tag_a_from_page0(self, keyword):
    #     self.flag = self.get_the_mc_or_code(keyword)
    #     for t in range(5):
    #         # time.sleep(3)
    #         # print u'验证码识别中...第%s次' %(t+1)
    #         self.info(u'验证码识别中...第%s次' %(t+1))
    #         self.today = str(datetime.date.today()).replace('-', '')
    #         # yzm = self.get_yzm()
    #         # print 'yzm', yzm
    #         # url = 'http://ah.gsxt.gov.cn/searchList.jspx'
    #         # params = {'checkNo': yzm, 'entName': keyword}
    #         url = 'http://ah.gsxt.gov.cn/queryListData.jspx'
    #         params = {'currentPageIndex': 1, 'entName': keyword, 'searchType': 1, }
    #         # print 'params:', params
    #         # r = self.post_request(url=url, params=params)
    #         # print 'r.headers',r.headers
    #         r = self.post_request(url=url, params=params)
    #         r.encoding = 'utf-8'
    #         # print '**************************', r.text
    #         soup = BeautifulSoup(r.text, 'html5lib')
    #         # print 'soup:', soup, r.status_code
    #         # print '*******cpn_request_ok?:', soup.select('.list')[0], 'next_siblings', soup.select('.list')[0].find_next_sibling()
    #         # tgr = soup.find(id='alert_win').find(id='MzImgExpPwd').get('alt')
    #         # print '*************', soup.select('#gggscpnametext')[0]
    #         # if u'请开启JavaScript并刷新该页' in soup.text:
    #         #     print u'cookie失效，更新cookie'  # 安徽360特色
    #         #     self.go_cookies()
    #         #
    #         if r.status_code == 200:
    #             # print '*'*100
    #             if not soup.text.strip():
    #                 # print u'***验证码识别通过***no_result***'
    #                 self.info(u'***验证码识别通过***no_result***')
    #                 return None
    #             if soup.find(id='gggscpnametext'):
    #                 # print 'r.headers', r.headers
    #                 # print u'**********验证码识别通过***安徽*********'  #, soup.find(class_='list')
    #                 self.info(u'**********验证码识别通过***安徽*********')
    #                 if soup.find(id='gggscpnametext').text.strip() != u'':
    #                     return soup.select('#gggscpnametext')
    #                 break
    #     self.info(u'验证码识别失败')
    #     raise

    def get_tag_a_from_page(self, keyword, flags=True):
        """
        获取查询结果页面
        :param keyword: 查询输入关键字
        :param flags:  查询内容为企业名称或信用代码
        :return:
        """
        self.flag = self.get_the_mc_or_code(keyword)
        print self.flag
        self.flag = flags
        # url = 'http://ah.gsxt.gov.cn/index.jspx'
        self.get_lock_id()
        url = 'http://ah.gsxt.gov.cn/index.jspx'
        self.get_request(url)
        validate = self.get_geetest_validate()
        # print 'validate', validate

        # self.headers['Host'] = 'ah.gsxt.gov.cn'
        self.headers['Referer'] = 'http://ah.gsxt.gov.cn/index.jspx'
        self.headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        self.headers['Accept-Language'] = 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3'
        self.headers['Accept-Encoding'] = 'gzip, deflate'
        self.headers['Connection'] = 'keep-alive'

        url_1 = "http://ah.gsxt.gov.cn/validateSecond.jspx"
        params_1 = {
            'geetest_challenge': self.challenge,
            'geetest_validate': validate,
            'geetest_seccode': '%s|jordan' % validate,
            'searchText': keyword
        }
        r_1 = self.post_request(url=url_1, params=params_1)
        # print r_1.text

        keyword = quote(keyword.encode('utf8'))
        keyword = quote(keyword.encode('utf8'))
        url_2 = 'http://ah.gsxt.gov.cn/searchList.jspx?top=top&checkNo=%s&searchType=1&entName=%s' %(validate, keyword)
        # print url_2
        # data_2 = {
        #     'keyword': keyword,
        #     'nowNum': '',
        #     'clear': '请输入企业名称、统一社会信用代码或注册号',
        #     'urlflag': '0',
        # }
        # print 'keyword', keyword

        r_2 = self.post_request(url_2)
        # print '*'*50
        # print r_2.text
        # print 'r2h', r_2.headers
        r_2.encoding = 'gbk'
        soup = BeautifulSoup(r_2.text, 'html5lib')
        # print 'r_2soup', soup
        self.release_lock_id()
        if u'访问本页面，您的浏览器需要支持JavaScript' in soup.text:
            print u'r_2出现js'
            raise
            url = self.get_the_js_url(soup)
            # print 'new_url2', url
            r_2 = self.get_request_302(url)

            r_2.encoding = 'gbk'
            soup = BeautifulSoup(r_2.text, 'html5lib')
            # print 'im', soup
        # print '+'*50
        # print r_2.text
        # print r_2.headers
        # 结果页面
        r_2.encoding='utf8'
        soup = BeautifulSoup(r_2.text, 'html5lib')
        # print 'soup:', soup
        if not soup.text.strip():
            # print u'***验证码识别通过***no_result***'
            self.info(u'***验证码识别通过***no_result***')
            return None
        if soup.find(id='gggscpnametext'):
            # print 'r.headers', r.headers
            # print u'**********验证码识别通过***安徽*********'  #, soup.find(class_='list')
            self.info(u'**********验证码识别通过***安徽*********')
            if soup.find(id='gggscpnametext').text.strip() != u'':
                return soup.select('#gggscpnametext')
            else:
                self.info(u'查询无结果')
                return None

    def get_search_args(self, tag_a, keyword):
        """
        查询结果解析的参数的方法
        :param tag_a:  查询结果对应的soup内容
        :param keyword:  查询输入的关键字内容

        :return: 查询结果是否与输入一致，1为一致，继续下一步；0为不一致，返回查询无结果
        """
        # print 'tag_a', tag_a  # 不是连接地址tagA
        gs_list = []    # 查询结果中的所有公司名称列表
        zt_list = []    # 查询结果中所有公司经营状态的列表
        rq_list = []    # 查询结果中所有公司信息日期列表
        if len(tag_a) > 1:
            for ta in tag_a:
                cm = ta.find_all('p')[0].text.strip().split('\n')[0].strip()    # 获取公司名称
                # print 'cmpame', cm
                zt = ta.find(class_='qiyezhuangtai').text.strip()    # 获取公司状态
                # print 'zt-mc', zt
                try:
                    rq = ta.find(class_='riqi').text.strip().split(u'：')[1].strip()    # 获取公司日期，标签位置可能有变化
                except Exception as e:
                    rq = ta.find(class_='riqi').text.strip().split(u':')[1].strip()    # 获取公司日期
                # print 'rq_time', rq
                gs_list.append(cm)
                zt_list.append(zt)
                rq_list.append(rq)
                self.save_company_name_to_db(cm)
        # print gs_list
        try:
            ct = gs_list.count(keyword)    # 判断查询结果是否有重复的统计
        except Exception as e:
            ct = 0
        if ct <= 1:
            try:
                n = gs_list.index(keyword)
            except Exception as e:
                print e
                n = 0
        else:
            print u'查询结果出现相同公司名'
            # k为公司名列表index序号
            try:
                cnt = [k for k, vn in enumerate(gs_list) if vn == keyword]
                ztm = [self.status_dict[zt_list[t]] for t in cnt]
                n = cnt[ztm.index(min(ztm))]    # n为查询结果列表中的索引
            except Exception as e:
                try:
                    n = gs_list.index(keyword)
                except:
                    n = 0

        # print 'name_n', n
        tag_a = tag_a[n]
        # print 'tag_a', tag_a
        name = tag_a.find_all('p')[0].text.strip().split('\n')[0]   # name为公司查询结果名；keyword为查询前数据库公司名
        # name_link = tag_a.find('a').get('href')
        # mainID = re.search(r'(?<=id=).*',name_link).group()
        mainID = tag_a.find_all('p')[0].find_all('span')[-1].get('id')    # 有分页情况可能用到的参数
        try:
            code = tag_a.find_all('p')[1].find_all('span')[0].text.strip().replace(' ', '').split(u'：')[1]    # 注册号
        except:
            code = tag_a.find_all('p')[1].find_all('span')[0].text.strip().replace(' ', '').split(u':')[1]    # 注册号
        # tagA = self.domain + name_link  # 验证码通过后链接地址
        # print '+++++++', name, '##', code, 'mainID:', mainID
        self.mainID = mainID  # 安徽有分页情况可能用到
        self.cur_mc = name.replace('(', u'（').replace(')', u'）').strip()
        self.cur_zch = code
        # self.tagA = tagA  # 安徽三大参数，公司名称name，注册号code， 跳过验证码的地址tagA

        self.xydm_if = ''    # 信用代码
        self.zch_if = ''    # 注册号
        if len(code) == 18:
            self.xydm_if = code
        else:
            self.zch_if = code
        print u'公司名(name)cur_mc: %s, 注册号(code)cur_zch: %s' % (name, code), 'mainID:', mainID
        if self.flag:
            if self.cur_mc == keyword:
                # print 'same'
                self.info(u'查询结果一致')
                return 1
            else:
                # print 'insane'
                self.info(u'查询结果不一致')
                self.save_company_name_to_db(self.cur_mc)
                return 0
        else:
            self.info(self.cur_mc)
            return 1

    def parse_detail(self):
        """
        解析公司详情信息
        :param kwargs:
        :return:
        """
        print '****************HIHI************************'
        url = 'http://ah.gsxt.gov.cn/business/JCXX.jspx?id='+self.mainID    # 详情页url
        r = self.get_request(url)
        # print r.text
        bs = BeautifulSoup(r.text, 'html5lib')
        bd_list = bs.find_all(class_='baseinfo')    # 获取详情内容soup中所有的表格
        # print '#hei_long_soup',  bd, '**'
        for bd in bd_list:
            try:
                divname = bd.find_all('span')[0].text.strip()    # div标签对应的表格内容
            except:
                divname = bd
                # print 'oucherror', divname
                continue
            # print '**', divname
            # print '*'*100
            # continue
            if divname == u'营业执照信息':
                self.get_ji_ben(bd)
            elif divname == u'股东及出资信息':
                self.get_gu_dong(bd)
            elif divname == u'变更信息':
                self.get_bian_geng(bd)
            elif divname == u'主要人员信息':
                self.get_zhu_yao_ren_yuan(bd)

            elif divname == u'成员名册信息':
                self.get_cheng_yuan_ming_ce(bd)
            elif u'主管部门（出资人）信息' in divname:
                self.info(u'解析主管部门出资人信息')
                self.get_gu_dong(bd)
            elif u'投资人信息' in divname:
                self.info(u'投资人信息')
                self.get_gu_dong(bd)
            elif u'合伙人信息' in divname:
                self.info(u'合伙人')
                self.get_gu_dong(bd)
            elif u'发起人及出资信息' in divname:
                self.info(u'发起人')
                self.get_gu_dong(bd)

        #     elif divname == u'分支机构信息':
        #         self.get_fen_zhi_ji_gou(bd)
        #     elif divname == u'清算信息':
        #         self.get_qing_suan(bd)
        #     elif divname == u'动产抵押登记信息':
        #         self.get_dong_chan_di_ya(bd)
        #     elif divname == u'股权出质登记信息':
        #         self.get_gu_quan_chu_zhi(bd)
        #     elif divname == u'抽查检查结果信息':
        #         self.get_chou_cha_jian_cha(bd)
        # self.get_xing_zheng_chu_fa()
        # self.get_jing_ying_yi_chang()
        # self.get_yan_zhong_wei_fa()
        return None
        
        self.get_ji_ben()
        # print 'jb_step_json', self.json_result
        self.get_gu_dong()
        # print 'gd_step_json', self.json_result
        self.get_bian_geng()
        # print 'bg_step_json', self.json_result
        self.get_zhu_yao_ren_yuan()
        self.get_fen_zhi_ji_gou()
        self.get_qing_suan()
        self.get_dong_chan_di_ya()
        self.get_gu_quan_chu_zhi()
        self.get_xing_zheng_chu_fa()
        self.get_jing_ying_yi_chang()
        self.get_yan_zhong_wei_fa()
        self.get_chou_cha_jian_cha()
        # self.get_nian_bao()
        # print 'the_last_json_result', len(self.json_result), self.json_result

        json_go = json.dumps(self.json_result, ensure_ascii=False)
        # print 'the_last_json_result:', len(self.json_result), get_cur_time(),  json_go

    def get_ji_ben(self, bd):
        """
        查询基本信息
        :return: 基本信息结果
        """
        json_list = []
        family = 'Registered_Info'
        table_id = '01'
        self.json_result[family] = []

        # url = 'http://ah.gsxt.gov.cn/business/YYZZ.jspx?id='+self.mainID
        # url = 'http://ah.gsxt.gov.cn/business/JCXX.jspx?id='+self.mainID
        # # print 'jiben_url', url
        # r = self.get_request(url=url, params={})
        # # r.encoding = 'gbk'
        # r.encoding = 'utf-8'
        # soup = BeautifulSoup(r.text, 'html5lib')
        soup = bd
        # print '*******ji_ben*******', soup
        tr_element_list = soup.find_all('tr')#(".//*[@id='jbxx']/table/tbody/tr")
        values = {}
        for tr_element in tr_element_list:
            # th_element_list = tr_element.find_all('th')
            td_element_list = tr_element.find_all('td')
            for td in td_element_list:
                if td.text.strip():
                    td_list = td.text.replace(u'·', '').replace(u' ', '').strip().replace(u' ', '').split(u'：',1)
                    col = td_list[0].strip()
                    val = td_list[1].strip()
                    # print col, val
                    col = jiben_column_dict[col]
                    values[col] = val

            # if len(th_element_list) == len(td_element_list):
            #     col_nums = len(th_element_list)
            #     for i in range(col_nums):
            #         col_dec = th_element_list[i].text.strip()
            #         val = td_element_list[i].text.strip()
            #         if col_dec != u'':
            #             col = jiben_column_dict[col_dec]
            #             values[col] = val
        values['rowkey'] = '%s_%s_%s_' % (self.cur_mc, table_id, self.cur_zch)
        values[family + ':registrationno'] = self.cur_zch
        values[family + ':enterprisename'] = self.cur_mc
        values[family + ':tyshxy_code'] = self.xydm_if
        values[family + ':zch'] = self.zch_if
        values[family + ':lastupdatetime'] = get_cur_time()
        values[family + ':province'] = u'安徽省'
        json_list.append(values)
        self.json_result[family] = json_list
        # print 'jiben_values', values

    def get_gu_dong(self, bd):
        """
        查询股东信息
        :param param_pripid: 有的省份可能用到的股东表查询id
        :param param_type: 有的省份可能用到的股东表查询类型
        :return: 股东信息查询结果，先放入self.json_result字典参数中
        """
        family = 'Shareholder_Info'
        table_id = '04'
        # self.json_result[family] = []
        json_list = []
        json_dict = {}
        # url = 'http://ah.gsxt.gov.cn/business/GDCZ.jspx?id='+self.mainID
        # # print 'gudongurl', url
        # r = self.get_request(url=url)
        # soup = BeautifulSoup(r.text, 'html5lib')
        soup = bd
        # try:
        #     url = soup.find(id='invDiv').text  # 此处url不是连接地址，是判断内容是否为空的参数
        # except:
        #     url = ''
        # print 'gudong_url', self.cur_time, url
        # print '******gudong_soup******', soup
        if soup.text.strip():
            try:
                title = soup.find('span').text.strip()
            except:
                title = ''
                return
            # print 'title:', title
            soup = soup.find(id='paging')
            # print '*******gudong*******', soup
            # print 'gu_dong_turn_page', turn_page
            # print 'body_tr',len(soup.select('#table2 tr a')),soup.select('#table2 tr a')
            # print 'gd_tr1',soup.select('#tr1')
            tr_num = soup.find(class_='detailsListGDCZ').find_all('tr')
            if len(tr_num) >= 1:
                gd_th = soup.find_all(class_='detailsList')[0].find_all('tr')[0].find_all('th')
                iftr = soup.find(class_='detailsListGDCZ').find_all('tr')
                if u'暂无股东及出资信息' in soup.find(class_='detailsListGDCZ').text:
                    self.info(u'暂无股东及出资信息')
                    return
                if u'暂无主管部门（出资人）信息' in soup.find(class_='detailsListGDCZ').text:
                    self.info(u'暂无主管部门（出资人）信息')
                    return

            # if len(iftr) > 0:
                cnt = 1
                thn = len(gd_th)
                family = 'Shareholder_Info'
                # print 'len(th):', thn
                for i in range(len(iftr)):
                    gd_td = iftr[i].find_all('td')
                    for j in range(len(gd_th)):
                        th = gd_th[j].text.strip()
                        if th == u'序号':
                            continue
                        td = gd_td[j].text.strip()
                        if td == u'查看':
                            td = gd_td[j].a.get('onclick')
                            # print 'gudong', td
                            td = re.search(r'\d{3,}', td).group().strip("'")
                            detail_url = 'http://ah.gsxt.gov.cn/queryInvDetailAction.jspx?invId='+td
                            # print 'detail_url', detail_url
                            td = detail_url
                            self.get_gu_dong_detail(detail_url, json_dict)
                            # self.load_func(td)  抓取详情页内容方法，见cnt分页内容
                        json_dict[gudong_column_dict[th]] = td
                    json_dict['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.cur_zch, self.today, cnt)
                    json_dict[family + ':registrationno'] = self.cur_zch
                    json_dict[family + ':enterprisename'] = self.cur_mc
                    json_dict[family + ':id'] = str(cnt)
                    json_list.append(json_dict)
                    json_dict = {}
                    cnt += 1

                turn_pageo = soup.find_all('div', recursive=False)[1].find('ul').find_all('li')[1].text.strip()[1:-1]    #判断是否有分页，需要post分页地址，暂不处理
                # print 'gudong_turn_page:', turn_pageo
                turn_page = int(turn_pageo)

                # 股东分页情况处理
                if turn_page > 1:
                    # print '*'*1000
                    # print 'len_gudong_page', turn_page
                    for p in range(2, turn_page+1):
                        # link = 'http://ah.gsxt.gov.cn/QueryInvList.jspx?pno='+str(p)+'&mainId='+self.mainID
                        fkurl = 'http://ah.gsxt.gov.cn/business/QueryInvList.jspx?pno='+str(p)+'&order=0&mainId='+self.mainID
                        # print '***********gudongfenyelink******************', link
                        url = fkurl
                        r = self.get_request(url=url, params={})
                        # r.encoding = 'gbk'
                        soup = BeautifulSoup(r.text, 'html5lib')
                        # print '*******gudong**fenye*****',soup
                        # gd_th = soup.find_all(class_='detailsList')[0].find_all('tr')[1].find_all('th')
                        iftr = soup.find(class_='detailsListGDCZ').find_all('tr')
                        # print 'pp', p
                        for i in range(len(iftr)):
                            gd_td = iftr[i].find_all('td')
                            # print 'mm', i
                            for j in range(len(gd_th)):
                                th = gd_th[j].text.strip()
                                if th == u'序号':
                                    continue
                                td = gd_td[j].text.strip()
                                if td == u'查看':
                                    td = gd_td[j].a.get('onclick')
                                    # print 'gudong', td
                                    td = re.search(r'\d{3,}', td).group().strip("'")
                                    detail_url = 'http://ah.gsxt.gov.cn/queryInvDetailAction.jspx?invId='+td
                                    # print 'detail_url', detail_url
                                    td = detail_url
                                    self.get_gu_dong_detail(detail_url, json_dict)
                                    # self.load_func(td)  抓取详情页内容方法，见cnt分页内容
                                json_dict[gudong_column_dict[th]] = td
                            json_dict['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.cur_zch, self.today, cnt)
                            json_dict[family + ':registrationno'] = self.cur_zch
                            json_dict[family + ':enterprisename'] = self.cur_mc
                            json_dict[family + ':id'] = str(cnt)
                            json_list.append(json_dict)
                            json_dict = {}
                            cnt += 1
                if json_list:
                    self.json_result[family] = json_list
                    # print '-,-**gudong_json_list', len(json_list), json_list

    def get_gu_dong_detail(self, url, values):
        """
        查询股东详情
        :param param_pripid:
        :param param_invid:
        :return:
        """
        family = 'Shareholder_Info'
        table_id = '04'
        # print 'gudong_detail_url',url
        r = self.get_request(url=url, params={})
        # r.encoding = 'gbk'
        soup = BeautifulSoup(r.text, 'html5lib')
        # print '***__****gudong_detail*******',soup

        detail_tb_list = soup.find_all(class_='detailsList')
        # detail_th_list = ['subscripted_capital','actualpaid_capital','subscripted_method','subscripted_amount','subscripted_time','actualpaid_method','actualpaid_amount','actualpaid_time']
        # detail_th_new_list = [family+':'+x for x in detail_th_list]
        # print 'detail_th_new_list', detail_th_new_list
        n = 0
        rjmx_list = []
        sjmx_list = []
        rjmx_dict = {}
        sjmx_dict = {}
        for tr_ele in detail_tb_list:
            tr_ele_list = tr_ele.find_all('tr')
            if n == 0:

                for tr in tr_ele_list[1:]:
                    col = tr.th.text.strip()
                    val = tr.td.text.strip()
                    # print 'gddetails', col, val
                    if u'万美元' in col:
                        col = col.replace(u'万美元', u'万元')
                        val = val + u'万美元'
                    if u'万香港元' in col:
                        col = col.replace(u'万香港元', u'万元')
                        val = val + u'万香港元'
                    values[gudong_column_dict[col]] = val
            else:
                th_list = tr_ele_list[0].find_all('th')
                if u'认缴出资' in tr_ele_list[0].text.strip():
                    if len(tr_ele_list) == 1:
                        for c in range(len(th_list)):
                            col = th_list[c].text.strip()
                            val = u''
                            if u'万美元' in col:
                                col = col.replace(u'万美元', u'万元')
                                val = val + u'万美元'
                            if u'万香港元' in col:
                                col = col.replace(u'万香港元', u'万元')
                                val = val + u'万香港元'
                            values[gudong_column_dict[col]] = val
                            if u'认缴出资' in col:
                                rjmx_dict[col] = val
                        rjmx_list.append(rjmx_dict)
                    if len(tr_ele_list) > 1:
                        for tr in tr_ele_list[1:]:
                            if tr.text.strip():
                                td_list = tr.find_all('td')
                                for c in range(len(th_list)):
                                    col = th_list[c].text.strip()
                                    val = td_list[c].text.strip()
                                    # print col,val
                                    if u'万美元' in col:
                                        col = col.replace(u'万美元', u'万元')
                                        val = val + u'万美元'
                                    if u'万香港元' in col:
                                        col = col.replace(u'万香港元', u'万元')
                                        val = val + u'万香港元'
                                    values[gudong_column_dict[col]] = val
                                    if u'认缴出资' in col:
                                        rjmx_dict[col] = val
                                rjmx_list.append(rjmx_dict)
                                rjmx_dict = {}

                if u'实缴出资' in tr_ele_list[0].text.strip():
                    if len(tr_ele_list) == 1:
                        for c in range(len(th_list)):
                            col = th_list[c].text.strip()
                            val = u''
                            if u'万美元' in col:
                                col = col.replace(u'万美元', u'万元')
                                val = val + u'万美元'
                            if u'万香港元' in col:
                                col = col.replace(u'万香港元', u'万元')
                                val = val + u'万香港元'
                            values[gudong_column_dict[col]] = val
                            if u'实缴出资' in col:
                                sjmx_dict[col] = val
                        sjmx_list.append(sjmx_dict)
                    if len(tr_ele_list) > 1:
                        for tr in tr_ele_list[1:]:
                            if tr.text.strip():
                                td_list = tr.find_all('td')
                                for c in range(len(th_list)):
                                    col = th_list[c].text.strip()
                                    val = td_list[c].text.strip()
                                    # print col,val
                                    if u'万美元' in col:
                                        col = col.replace(u'万美元', u'万元')
                                        val = val + u'万美元'
                                    if u'万香港元' in col:
                                        col = col.replace(u'万香港元', u'万元')
                                        val = val + u'万香港元'
                                    values[gudong_column_dict[col]] = val
                                    if u'实缴出资' in col:
                                        sjmx_dict[col] = val
                                sjmx_list.append(sjmx_dict)
                                sjmx_dict = {}
            n += 1
        values[gudong_column_dict[u'认缴明细']] = rjmx_list
        values[gudong_column_dict[u'实缴明细']] = sjmx_list

        # print 'gdl_values',len(values),values

    def get_bian_geng(self, bd):
        """
        查询变更信息
        :param param_pripid: 部分省份查询变更信息可能用到的参数
        :param param_type: 部分省份查询变更信息可能用到的查询类型
        :return:
        """
        family = 'Changed_Announcement'
        table_id = '05'
        # self.json_result[family] = []
        json_list = []
        json_dict = {}

        # url = 'http://ah.gsxt.gov.cn/business/BGXX.jspx?id='+self.mainID
        # # print 'biangeng_url', url
        # r = self.get_request(url=url, params={})
        # # r.encoding = 'gbk'
        # r.encoding = 'utf-8'
        # soup = BeautifulSoup(r.text, 'html5lib')
        soup = bd
        # print '*******biangeng*******', soup
        try:
            tr_num = len(soup.find_all(class_='detailsList'))
        except:
            tr_num = 0

        if tr_num > 1:
            gd_th = soup.find_all(class_='detailsList')[0].find_all('th')
            # print 'th_previous',cc.find(id='altDiv').find_previous_sibling().text
            iftr = soup.find_all(class_='detailsList')[1].find_all('tr')
            if u'暂无变更信息' in soup.find_all(class_='detailsList')[1].text:
                self.info(u'暂无变更信息')
                return
            if len(iftr) > 0:
                cnt = 1
                for i in range(len(iftr)):
                    gd_td = iftr[i].find_all('td')
                    for j in range(len(gd_th)):
                        th = gd_th[j].text.strip()
                        td = gd_td[j].text.strip()
                        # print i,j,th,td
                        json_dict[biangeng_column_dict[th]] = td
                    json_dict['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.cur_zch, self.today, cnt)
                    json_dict[family + ':registrationno'] = self.cur_zch
                    json_dict[family + ':enterprisename'] = self.cur_mc
                    json_dict[family + ':id'] = str(cnt)
                    json_list.append(json_dict)
                    json_dict = {}
                    cnt += 1

                turn_pageo = soup.find(id='altDiv2').find_all('div', recursive=False)[1].ul.find_all('li')[1].text.strip()[1:-1]    #判断是否有分页，需要post分页地址，暂不处理
                # print 'biangeng_turn_page:', turn_pageo
                turn_page = int(turn_pageo)

                if turn_page > 1:
                    # print '*3'*1000
                    # sys.exit()
                    # print 'biangeng_page_splitter***************'
                    for p in range(2, turn_page+1):
                        # bgurl = 'http://ah.gsxt.gov.cn/QueryAltList.jspx?pno='+str(p)+'&mainId='+self.mainID
                        fkurl = 'http://ah.gsxt.gov.cn/business/QueryAltList.jspx?pno='+str(p)+'&order=0&mainId='+self.mainID
                        # print 'biangeng_fen_ye_link', fkurl
                        rc = self.get_request(url=fkurl)
                        soup = BeautifulSoup(rc.text, 'lxml')
                        # print 'biangeng_turn_soup', soup

                        # gd_th = soup.find_all(class_='detailsList')[0].find_all('tr')[1].find_all('th')
                        iftr = soup.find_all(class_='detailsList')[1].find_all('tr')
                        for i in range(len(iftr)):
                            gd_td = soup.find_all(class_='detailsList')[1].find_all('tr')[i].find_all('td')
                            for j in range(len(gd_th)):
                                th = gd_th[j].text.strip()
                                td = gd_td[j].text.strip()
                                # print i,j,th,td
                                json_dict[biangeng_column_dict[th]] = td
                            # print '****************json_dict',json_dict
                            json_dict['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.cur_zch, self.today, cnt)
                            json_dict[family + ':registrationno'] = self.cur_zch
                            json_dict[family + ':enterprisename'] = self.cur_mc
                            json_dict[family + ':id'] = str(cnt)
                            json_list.append(json_dict)
                            json_dict = {}
                            cnt += 1
                if json_list:
                    self.json_result[family] = json_list
                    # print '-,-**biangeng_json_list****', len(json_list), json_list

    def get_detail(self, sop):  # 北京变更详情专用, 其他省份暂时无用
        row_data = []
        # tables=self.driver.find_elements_by_xpath("//*[@id='tableIdStyle']/tbody")
        tables=sop.find_all(id='tableIdStyle')
        for t in tables:
            time.sleep(1)
            trs = t.find_all("tr")
            bt = trs[0].text
            ths = trs[1].find_all("th")
            for tr in trs[2:]:
                tds = tr.find_all("td")
                col_nums = len(ths)
                for j in range(col_nums):
                    col = ths[j].text.strip().replace('\n','')
                    td = tds[j]
                    val = td.text.strip()
                    row = col+u'：'+val
#                     print 'row',row
                    row_data.append(row)
            if u'变更前' in bt:
                self.bgq = u'；'.join(row_data)
                # print 'bgq',self.bgq
            elif u'变更后' in bt:
                self.bgh = u'；'.join(row_data)
                # print 'bgh',self.bgh
            row_data = []

    def get_zhu_yao_ren_yuan(self, bd):
        """
        查询主要人员信息
        :param param_pripid: 部分省份查询主要人员信息可能用到的参数
        :param param_type: 部分省份查询主要人员信息可能用到的查询类型
        :return:
        """
        family = 'KeyPerson_Info'
        table_id = '06'
        # self.json_result[family] = []
        json_list = []    # 主要人员的json列表
        values = {}    # 查询结果对应的字典

        # url = 'http://ah.gsxt.gov.cn/business/ZYRY.jspx?id='+self.mainID
        # # print 'zhuyaorenyuan_url', url
        # r = self.get_request(url=url, params={})
        # # r.encoding = 'gbk'
        # r.encoding = 'utf-8'
        # soup = BeautifulSoup(r.text, 'html5lib')
        soup = bd
        # print '*******zhuyaorenyuan*******', soup

        try:
            tr_num = len(soup.find_all(class_='keyPerInfo'))
        except:
            tr_num = 0
        # print 'zyry()*)(', tr_num
        if tr_num > 0:
            # 新增主要人员数目大于16时候翻页判定
            if u'查看更多' in soup.find('p').text.strip():
                try:
                    prebody = soup.find('p').text.strip()
                    link = soup.find('p').find('a').get('onclick')
                    uuid = re.search(u"(?<=id=).*(?=')",link).group()
                    n = re.search(u'(?<=共计).*(?=条)',prebody).group()
                    n = int(n)/16
                    # print 'uuid',uuid,'n',n
                    url = 'http://ah.gsxt.gov.cn/business/loadMoreMainStaff.jspx?uuid=%s&order=%s' %(uuid, n)
                    r = self.get_request(url=url)
                    soup = BeautifulSoup(r.text,'html5lib')
                    tr_num = len(soup.find_all(class_='keyPerInfo'))
                except Exception as e:
                    print 'zyry_turnpage_e', e
                    pass

            soup = soup.find_all(class_='keyPerInfo')  # 有几个人员

            # print '*******zhuyaorenyuan*******',soup
            # print 'tr_num', tr_num
            cnt = 1
            for t in range(tr_num):
                pson = soup[t].find_all('p')
                if len(pson):
                    name = pson[0].text.strip()
                    posn = pson[1].text.strip()
                    # print '******', t, 'name:', name, 'position:', posn
                    values[zhuyaorenyuan_column_dict[u'姓名']] = name
                    values[zhuyaorenyuan_column_dict[u'职务']] = posn
                    values['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.cur_zch, self.today, cnt)
                    values[family + ':registrationno'] = self.cur_zch
                    values[family + ':enterprisename'] = self.cur_mc
                    values[family + ':id'] = str(cnt)
                    json_list.append(values)
                    values = {}
                    cnt += 1
            if json_list:
                # print 'zhuyaorenyuan_jsonlist:', json_list
                self.json_result[family] = json_list

    def get_cheng_yuan_ming_ce(self, bd):
        """
        查询主要人员信息
        :param bd: 成员名册查询结果的SOUP格式
        :return:
        """
        family = 'KeyPerson_Info'
        table_id = '06'
        # self.json_result[family] = []
        json_list = []
        values = {}

        # url = 'http://ah.gsxt.gov.cn/business/ZYRY.jspx?id='+self.mainID
        # # print 'zhuyaorenyuan_url', url
        # r = self.get_request(url=url, params={})
        # # r.encoding = 'gbk'
        # r.encoding = 'utf-8'
        # soup = BeautifulSoup(r.text, 'html5lib')
        soup = bd
        # print '*******zhuyaorenyuan*******', soup

        try:
            tr_num = len(soup.find_all(class_='keyPerInfo'))
        except:
            tr_num = 0
        # print 'zyry()*)(', tr_num
        if tr_num > 0:
            # 新增成员名册数目大于16时候翻页判定
            if u'查看更多' in soup.find('p').text.strip():
                try:
                    prebody = soup.find('p').text.strip()
                    link = soup.find('p').find('a').get('onclick')
                    uuid = re.search(u"(?<=id=).*(?=')",link).group()
                    n = re.search(u'(?<=共计).*(?=条)',prebody).group()
                    n = int(n)/16
                    # print 'uuid',uuid,'n',n
                    url = 'http://ah.gsxt.gov.cn/business/loadMoreMainStaff.jspx?uuid=%s&order=%s' %(uuid, n)
                    r = self.get_request(url=url)
                    soup = BeautifulSoup(r.text,'html5lib')
                    tr_num = len(soup.find_all(class_='keyPerInfo'))
                except Exception as e:
                    print 'cymc_turnpage_e', e
                    pass
            soup = soup.find_all(class_='keyPerInfo')  # 有几个人员

            # print '*******zhuyaorenyuan*******',soup
            cnt = 1
            for t in range(tr_num):
                pson = soup[t]#.find_all('p')
                if len(pson):
                    name = pson.text.strip()
                    posn = ''
                    # print '******', t, 'name:', name, 'position:', posn
                    values[zhuyaorenyuan_column_dict[u'姓名']] = name
                    values[zhuyaorenyuan_column_dict[u'职务']] = posn
                    values['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.cur_zch, self.today, cnt)
                    values[family + ':registrationno'] = self.cur_zch
                    values[family + ':enterprisename'] = self.cur_mc
                    values[family + ':id'] = str(cnt)
                    json_list.append(values)
                    values = {}
                    cnt += 1
            if json_list:
                # print 'zhuyaorenyuan_jsonlist:', json_list
                self.json_result[family] = json_list

    def get_fen_zhi_ji_gou(self, bd):
        """
        查询分支机构信息
        :param bd: 分支机构查询的soup内容
        :return:
        """
        family = 'Branches'
        table_id = '08'
        # self.json_result[family] = []

        # url = 'http://ah.gsxt.gov.cn/business/FZJG.jspx?id='+self.mainID
        # # print 'fenzhijigou_url', url
        # r = self.get_request(url=url, params={})
        # # r.encoding = 'gbk'
        # r.encoding = 'utf-8'
        # soup = BeautifulSoup(r.text, 'html5lib')
        soup = bd
        # print '*******fenzhijigou*******', soup
        try:
            tr_num = len(soup.find_all('p'))
        except:
            tr_num = 0
        # print 'fenzhijigou:', tr_num
        if tr_num > 1:
            # soup = soup.find(class_='xxwk')
            print '*******fenzhijigou*******', soup

            values = {}
            json_list = []

            if soup.text.strip():
                tr_element_list = soup.find_all(class_='fenzhixinxin')
                idn = 1
                for tr_element in tr_element_list:
                    if tr_element.text == u'':
                        # print 'fenzhijigou_boom_breaker'
                        break
                    td_element_list = tr_element.find_all("p")
                    values[fenzhijigou_column_dict[u'名称']] = td_element_list[0].text.strip()
                    values[fenzhijigou_column_dict[u'注册号']] = td_element_list[1].text.strip().replace(u'·', '').split(u'：')[1]
                    values[fenzhijigou_column_dict[u'登记机关']] = td_element_list[2].text.strip().replace(u'·', '').split(u'：')[1]
                    values['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.cur_zch, self.today, idn)
                    values[family + ':registrationno'] = self.cur_zch
                    values[family + ':enterprisename'] = self.cur_mc
                    values[family + ':id'] = str(idn)
                    json_list.append(values)
                    # json_fenzhijigou=json.dumps(values,ensure_ascii=False)
                    # print 'json_fenzhijigou',json_fenzhijigou
                    values = {}
                    idn += 1

                if json_list:
                    self.json_result[family] = json_list
                    # print '-,-**fenzhijigou_json_list', len(json_list), json_list

    def get_qing_suan(self, bd):
        """
        查询清算信息
        :param bd: 清算信息表单的soup内容
        :return:
        """
        family = 'liquidation_Information'
        table_id = '09'
        # self.json_result[family] = []
        values = {}
        json_list = []

        # url = 'http://ah.gsxt.gov.cn/business/QSXX.jspx?id='+self.mainID
        # # print 'qingsuan_url:', url
        # r = self.get_request(url=url, params={})
        # # r.encoding = 'gbk'
        # r.encoding = 'utf-8'
        # soup = BeautifulSoup(r.text, 'html5lib')

        soup = bd
        # print 'qingsuan', soup
        try:
            if u'清算信息' in soup.text:
                table = soup.find('table')
                tr_list = table.find_all('tr')[1:]
                # try:
                fzr = tr_list[0]  # 清算负责人
                cy = tr_list[1]  # 清算组成员
                # print 'fzr',fzr,'cy',cy
                fzrtd = fzr.find_all('td')[0].text.strip()
                cytd = cy.find_all('td')[0].text.strip()
                # print '****qingsuanyisen**'
                if len(cy.find_all('td')) > 1:
                    cytd = [td.text for td in cy.find_all('td')]
                try:
                    if fzrtd or cytd:
                        # print u'清算有内容'
                        self.info(u'清算有内容')
                        values[qingsuan_column_dict[u'清算负责人']] = fzrtd
                        values[qingsuan_column_dict[u'清算组成员']] = cytd
                        values['rowkey'] = '%s_%s_%s_%s_' % (self.cur_mc, table_id, self.cur_zch, self.today)
                        values[family + ':registrationno'] = self.cur_zch
                        values[family + ':enterprisename'] = self.cur_mc
                        json_list.append(values)
                        if json_list:
                            # print 'qingsuan', json_list
                            self.json_result[family] = json_list
                except:
                    return
        except:
            return

    def get_dong_chan_di_ya(self, bd):
        """
        查询动产抵押信息
        :param bd: 动产抵押的soup内容
        :return:
        """
        family = 'Chattel_Mortgage'
        table_id = '11'
        # self.json_result[family] = []
        values = {}
        json_list = []

        # url = 'http://ah.gsxt.gov.cn/business/DCDY.jspx?id='+self.mainID
        # # print 'dcdyurl:', url
        # r = self.get_request(url=url, params={})
        # # r.encoding = 'gbk'
        # r.encoding = 'utf-8'
        # soup = BeautifulSoup(r.text, 'html5lib')
        soup = bd
        # print '*******dongchandiya*******', soup
        try:
            tr_num = len(soup.find_all('p'))
        except:
            tr_num = 0
        # print 'fenzhijigou:', tr_num
        if tr_num:
            soup = soup.find(id='mortDiv2')

            row_cnt = len(soup.find_all(class_="detailsList")[1].find_all('tr'))
            if u'暂无动产抵押登记信息' in soup.find_all(class_="detailsList")[1].text:
                self.info(u'暂无动产抵押登记信息')
                return
            if row_cnt > 0:
                # print 'come_on_bb_not_OK'
                tr_element_list = soup.find_all(class_="detailsList")[1].find_all('tr')
                th_element_list = soup.find_all(class_="detailsList")[0].find_all('tr')[0].find_all('th')
                idn = 1
                for tr_element in tr_element_list:
                    td_element_list = tr_element.find_all('td')
                    col_nums = len(th_element_list)
                    # print '*****', col_nums
                    for j in range(col_nums):
                        col_dec = th_element_list[j].text.strip().replace('\n','')
                        col = dongchandiyadengji_column_dict[col_dec]
                        td = td_element_list[j]
                        val = td.text.strip()
                        if val == u'查看':
                            mex = td.a.get('onclick')
                            td = re.search(r'(?<=[(]).*(?=[)])', mex).group().replace("'", "")
                            # urlsample = 'http://ah.gsxt.gov.cn/business/mortInfoDetail.jspx?id=400000000122041524'
                            # link = self.domain+td
                            link = 'http://ah.gsxt.gov.cn/business/mortInfoDetail.jspx?id='+td
                            # print u'动产抵押详情', link
                            values[col] = link
                        else:
                            values[col] = val
                    # values['RegistrationNo']=self.cur_code
                    # values['EnterpriseName']=self.org_name
                    # values['rowkey'] = values['EnterpriseName']+'_11_'+ values['RegistrationNo']+'_'+str(id)
                    values['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.cur_zch, self.today, idn)
                    values[family + ':registrationno'] = self.cur_zch
                    values[family + ':enterprisename'] = self.cur_mc
                    values[family + ':id'] = str(idn)
                    json_list.append(values)
                    # json_dongchandiyadengji=json.dumps(values,ensure_ascii=False)
                    # print 'json_dongchandiyadengji',json_dongchandiyadengji
                    values = {}
                    idn += 1
                if json_list:
                    # print '-,-**dongchandiya_json_list',len(json_list),json_list
                    self.json_result[family] = json_list

    def get_gu_quan_chu_zhi(self, bd):
        """
        查询股权出置信息
        :param bd: 股权出质的soup内容
        :return:
        """
        family = 'Equity_Pledge'
        table_id = '12'
        # self.json_result[family] = []
        json_list = []
        values = {}

        # url = 'http://ah.gsxt.gov.cn/business/GQCZ.jspx?id='+self.mainID
        # # print 'gqczurl:', url
        # r = self.get_request(url=url, params={})
        # # r.encoding = 'gbk'
        # r.encoding = 'utf-8'
        # soup = BeautifulSoup(r.text, 'html5lib')
        soup = bd
        # print '*******guquanchuzhi*******', soup
        try:
            tr_num = len(soup.find_all('p'))
        except:
            tr_num = 0
        # print 'fenzhijigou:', tr_num
        if tr_num:
            # print '*******guquanchuzhi*******',soup
            soup = soup.find(id='pledgeDiv2')
            table_element = soup.find_all(class_="detailsList")
            row_cnt = len(soup.find_all(class_="detailsList")[1].find_all('tr'))
            if u'暂无股权出质登记信息' in soup.find_all(class_="detailsList")[1].text:
                self.info(u'暂无暂无股权出质登记信息')
                return
            if row_cnt > 0:
                tr_element_list = soup.find_all(class_="detailsList")[1].find_all('tr')
                th_element_list = soup.find_all(class_="detailsList")[0].find_all('tr')[0].find_all('th')
                idn = 1
                for tr_element in tr_element_list:
                    td_element_list = tr_element.find_all('td')
                    col_nums = len(th_element_list)
                    for j in range(col_nums):
                        col_dec = th_element_list[j].text.strip().replace('\n','')
                        # print 'col_dec',col_dec
                        if col_dec == u'证照/证件号码' and th_element_list[j-1].text.strip().replace('\n','') == u'出质人':
                            # print '**',col_dec
                            col = guquanchuzhidengji_column_dict[col_dec]
                        elif col_dec == u'证照/证件号码' and th_element_list[j-1].text.strip().replace('\n','') == u'质权人':
                            # print '***',col_dec
                            col = guquanchuzhidengji_column_dict[u'证照/证件号码1']
                        else:
                            col = guquanchuzhidengji_column_dict[col_dec]
                        td = td_element_list[j]
                        val = td.text.strip()
                        if val == u'查看':
                            mex = td.a.get('onclick')
                            td = re.search(r'\d{3,}', mex).group().replace("'", "")
                            # link = self.domain+td
                            link = 'http://ah.gsxt.gov.cn/business/altPleInfo.jspx?pleId='+td
                            # print 'gqcz_link', link
                            values[col] = link
                            # print u'股权出质详情', link
                        else:
                            values[col] = val
                    # values['RegistrationNo']=self.cur_code
                    # values['EnterpriseName']=self.org_name
                    # values['rowkey'] = values['EnterpriseName']+'_12_'+ values['RegistrationNo']+'_'+str(id)
                    values['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.cur_zch, self.today, idn)
                    values[family + ':registrationno'] = self.cur_zch
                    values[family + ':enterprisename'] = self.cur_mc
                    values[family + ':id'] = str(idn)
                    json_list.append(values)
                    # json_guquanchuzhidengji=json.dumps(values,ensure_ascii=False)
                    # print 'json_guquanchuzhidengji',json_guquanchuzhidengji
                    values = {}
                    idn += 1

                if len(table_element) == 3:
                    turn_page = table_element[2].find_all('a')
                    # if len(turn_page) > 1:
                    #     print u'股权出质有分页'
                if json_list:
                    self.json_result[family] = json_list
                    # print '-,-**guquanchuzhi_json_list**',len(json_list),json_list

    def get_xing_zheng_chu_fa(self):
        """
        查询行政处罚信息，需重新发送查询请求
        :param param_pripid:
        :param param_type:
        :return:
        """
        family = 'Administrative_Penalty'
        table_id = '13'
        # self.json_result[family] = []
        values = {}
        json_list = []

        url = 'http://ah.gsxt.gov.cn/business/XZCF.jspx?id='+self.mainID
        # print 'xzcfurl:', url
        r = self.get_request(url=url, params={})
        # r.encoding = 'gbk'
        r.encoding = 'utf-8'
        soup = BeautifulSoup(r.text, 'html5lib')
        # print '*******xingzhengchufa*******', soup
        try:
            tr_num = len(soup.find_all('p'))
        except:
            tr_num = 0
        # print 'xingzhengchufa:', tr_num
        if tr_num:
            # print '*******xingzhengchufa*******',soup
            soup = soup.find(id='punDiv2')
            table_element = soup.find_all(class_='detailsList')
            row_cnt = len(soup.find_all(class_="detailsList")[1].find_all('tr'))
            if u'暂无行政处罚信息' in soup.find_all(class_="detailsList")[1].text:
                self.info(u'暂无行政处罚信息')
                return
            if row_cnt > 0:
                tr_element_list = soup.find_all(class_="detailsList")[1].find_all('tr')
                th_element_list = soup.find_all(class_="detailsList")[0].find_all('tr')[0].find_all('th')
                idn = 1
                for tr_element in tr_element_list:
                    td_element_list = tr_element.find_all('td')
                    col_nums = len(th_element_list)
                    for j in range(col_nums):
                        col_dec = th_element_list[j].text.strip().replace('\n','')
                        col = xingzhengchufa_column_dict[col_dec]
                        td = td_element_list[j]
                        val = td.text.strip()
                        if val == u'查看':
                            mex = td.a.get('onclick')
                            td = re.search(r'\d{3,}', mex).group().replace("'", "")
                            # val = self.domain+td
                            val = 'http://ah.gsxt.gov.cn/business/punishInfoDetail.jspx?id='+td
                            # print 'xingzhengchufa__val', val
                        values[col] = val
                    # values['RegistrationNo']=self.cur_code
                    # values['EnterpriseName']=self.org_name
                    # values['rowkey'] = values['EnterpriseName']+'_13_'+ values['RegistrationNo']+'_'+str(id)
                    values['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.cur_zch, self.today, idn)
                    values[family + ':registrationno'] = self.cur_zch
                    values[family + ':enterprisename'] = self.cur_mc
                    values[family + ':id'] = str(idn)
                    json_list.append(values)
                    # json_xingzhengchufa=json.dumps(values,ensure_ascii=False)
                    # print 'json_xingzhengchufa',json_xingzhengchufa
                    values = {}
                    idn += 1
                if len(table_element) == 3:
                    turn_page = table_element[2].find_all('a')
                    # if len(turn_page) > 1:
                    #     print u'行政处罚有分页'
                if json_list:
                    self.json_result[family] = json_list
                    # print '-,-**xingzhengchufa_jsonlist***', len(json_list), json_list

    def get_jing_ying_yi_chang(self):
        """
        查询经营异常信息，需要重新发送查询请求
        :param param_pripid:
        :param param_type:
        :return:
        """
        family = 'Business_Abnormal'
        table_id = '14'
        # self.json_result[family] = []
        values = {}
        json_list = []

        url = 'http://ah.gsxt.gov.cn/business/JYYC.jspx?id='+self.mainID
        # print 'jyycurl:', url
        r = self.get_request(url=url, params={})
        # r.encoding = 'gbk'
        r.encoding = 'utf-8'
        soup = BeautifulSoup(r.text, 'html5lib')
        # print '*******jingyingyichang*******', soup
        try:
            tr_num = len(soup.find_all('p'))
        except:
            tr_num = 0
        # print 'jingyingyichang:', tr_num
        if tr_num:
            soup = soup.find(id='excDiv2')
            table_element = soup.find_all(class_='detailsList')
            row_cnt = len(soup.find_all(class_="detailsList")[1].find_all('tr'))
            if u'暂无经营异常信息' in soup.find_all(class_="detailsList")[1].text or u'暂无列入经营异常名录信息' in soup.find_all(class_="detailsList")[1].text:
                self.info(u'暂无列入经营异常名录信息')
                return
            if row_cnt > 0:
                idn = 1
                tr_element_list = soup.find_all(class_="detailsList")[1].find_all('tr')
                th_element_list = soup.find_all(class_="detailsList")[0].find_all('tr')[0].find_all('th')
                for tr_element in tr_element_list:
                    td_element_list = tr_element.find_all('td')
                    col_nums = len(th_element_list)
                    for j in range(col_nums):
                        col_dec = th_element_list[j].text.strip().replace('\n','')
                        # print 'col_dec',col_dec
                        col = jingyingyichang_column_dict[col_dec]
                        td = td_element_list[j]
                        val = td.text.strip().replace('\t','').replace('\n','')
                        values[col] = val
                        # print 'iii',col,val
                    # values['RegistrationNo']=self.cur_code
                    # values['EnterpriseName']=self.org_name
                    # values['rowkey'] = values['EnterpriseName']+'_14_'+ values['RegistrationNo']+'_'+str(id)
                    values['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.cur_zch, self.today, idn)
                    values[family + ':registrationno'] = self.cur_zch
                    values[family + ':enterprisename'] = self.cur_mc
                    values[family + ':id'] = str(idn)
                    json_list.append(values)
                    # json_jingyingyichang=json.dumps(values,ensure_ascii=False)
                    # print 'json_jingyingyichang',json_jingyingyichang
                    values = {}
                    idn += 1
                if len(table_element) == 3:
                    turn_page = table_element[2].find_all('a')
                    # if len(turn_page) > 1:
                    #     print u'经营异常有分页'
                if json_list:
                    self.json_result[family] = json_list
                    # print '-,-**jingyingyichang',json_list

    def get_yan_zhong_wei_fa(self):
        """
        查询严重违法信息，需要向url重新发送查询请求
        :param param_pripid:
        :param param_type:
        :return:
        """
        family = 'Serious_Violations'
        table_id = '15'
        # self.json_result[family] = []
        values = {}
        json_list = []

        url = 'http://ah.gsxt.gov.cn/business/YZWF.jspx?id='+self.mainID
        # print 'yzwfurl:', url
        r = self.get_request(url=url, params={})
        # r.encoding = 'gbk'
        r.encoding = 'utf-8'
        soup = BeautifulSoup(r.text, 'html5lib')
        # print '*******yanzhongweifa*******', soup
        try:
            tr_num = len(soup.find_all('p'))
        except:
            tr_num = 0
        # print 'yanzhongweifa:', tr_num
        if tr_num:
            soup = soup.find(id='serillDiv2')
            table_element = soup.find_all(class_='detailsList')
            row_cnt = len(soup.find_all(class_="detailsList")[1].find_all('tr'))
            if u'暂无列入严重违法失信企业名单（黑名单）信息' in soup.find_all(class_="detailsList")[1].text:
                self.info(u'暂无列入严重违法失信企业名单（黑名单）信息')
                return
            if row_cnt > 0:
                tr_element_list = soup.find_all(class_="detailsList")[1].find_all('tr')
                th_element_list = soup.find_all(class_="detailsList")[0].find_all('tr')[0].find_all('th')
                idn = 1
                for tr_element in tr_element_list:
                    td_element_list = tr_element.find_all('td')
                    col_nums = len(th_element_list)
                    for j in range(col_nums):
                        col_dec = th_element_list[j].text.strip().replace('\n','')
                        col = yanzhongweifa_column_dict[col_dec]
                        td = td_element_list[j]
                        val = td.text.strip()
                        values[col]=val
                    # values['RegistrationNo']=self.cur_code
                    # values['EnterpriseName']=self.org_name
                    # values['rowkey'] = values['EnterpriseName']+'_15_'+ values['RegistrationNo']+'_'+str(id)
                    values['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.cur_zch, self.today, idn)
                    values[family + ':registrationno'] = self.cur_zch
                    values[family + ':enterprisename'] = self.cur_mc
                    values[family + ':id'] = str(idn)
                    json_list.append(values)
                    # json_yanzhongweifa=json.dumps(values,ensure_ascii=False)
                    # print 'json_yanzhongweifa',json_yanzhongweifa
                    values = {}
                    idn += 1
                if len(table_element) == 3:
                    turn_page = table_element[2].find_all('a')
                    # if len(turn_page) > 1:
                    #     print u'严重违法有分页'
                if json_list:
                    self.json_result[family] = json_list
                    # print '-,-**yanzhongweifa_json_list', len(json_list), json_list

    def get_chou_cha_jian_cha(self, bd):
        """
        查询抽查检查信息
        :param bd: 抽查检查的soup内容
        :return:
        """
        family = 'Spot_Check'
        table_id = '16'
        # self.json_result[family] = []
        values = {}
        json_list = []

        # url = 'http://ah.gsxt.gov.cn/business/CCJC.jspx?id='+self.mainID
        # # print 'ccjcurl:', url
        # r = self.get_request(url=url, params={})
        # # r.encoding = 'gbk'
        # r.encoding = 'utf-8'
        # soup = BeautifulSoup(r.text, 'html5lib')
        soup = bd
        # print '*******chouchajiancha*******', soup
        try:
            tr_num = len(soup.find_all('p'))
        except:
            tr_num = 0
        # print 'chouchajiancha:', tr_num
        if tr_num:
            soup = soup.find(id='spotCheck2')
            try:
                row_cnt = len(soup.find_all(class_='detailsList')[1].find_all('tr'))
            except:
                row_cnt = 0
            # print 'ccjc_row_cnt',row_cnt
            if u'暂无抽查检查结果信息' in soup.find_all(class_="detailsList")[1].text:
                self.info(u'暂无抽查检查结果信息')
                return
            if row_cnt > 0:
                # print '*****mmmm****'
                table_element = soup.find_all(class_='detailsList')
                tr_element_list = soup.find_all(class_='detailsList')[1].find_all('tr')
                th_element_list = soup.find_all(class_='detailsList')[0].find_all('tr')[0].find_all('th')
                idn = 1
                for tr_element in tr_element_list:
                    td_element_list = tr_element.find_all('td')
                    col_nums = len(th_element_list)
                    for j in range(col_nums):
                        col_dec = th_element_list[j].text.strip().replace('\n','')
                        col = chouchajiancha_column_dict[col_dec]
                        td = td_element_list[j]
                        val = td.text.strip()
                        values[col] = val
                    # values['RegistrationNo']=self.cur_code
                    # values['EnterpriseName']=self.org_name
                    # values['rowkey'] = values['EnterpriseName']+'_16_'+ values['RegistrationNo']+'_'+str(id)
                    values['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.cur_zch, self.today, idn)
                    values[family + ':registrationno'] = self.cur_zch
                    values[family + ':enterprisename'] = self.cur_mc
                    values[family + ':id'] = str(idn)
                    json_list.append(values)
                    # json_chouchajiancha=json.dumps(values,ensure_ascii=False)
                    # print 'json_chouchajiancha',json_chouchajiancha
                    values = {}
                    idn += 1
                if len(table_element) == 3:
                    turn_page = table_element[2].find_all('a')
                    # if len(turn_page) > 1:
                    #     print u'抽查检查有分页'
                if json_list:
                    self.json_result[family] = json_list
                    # print '-,-**chouchajiancha', len(json_list), json_list

    def get_nian_bao(self):
        """
        获取年报内容的方法
        :param self:
        :return:
        """

        dic = {}  # 年份容器

        self.nbjb_list = []  # 年报基本信息
        self.nbzczk_list = []  # 年报资产状况

        self.nbdwdb_list = []    # 年报对外担保
        self.nbgdcz_list = []    # 年报股东出资
        self.nbgqbg_list = []    # 年报股权变更
        self.nbwz_list = []    # 年报网站
        self.nbxg_list = []    # 年报修改
        self.nbdwtz_list = []    # 年报对外投资

        url = 'http://ah.gsxt.gov.cn/yearExm/QYNBXX.jspx?ram='+str(random.random())+'&id='+self.mainID
        url = 'http://ah.gsxt.gov.cn/yearReport/index/datafordetail.jspx?id='+self.mainID
        # print 'nianbaourl:', url
        try:
            r = self.get_request(url=url)
        except:
            self.info(u'该企业暂无年度报告信息')
            return
        soup = BeautifulSoup(r.text, 'html5lib')
        soup = soup.find(class_='panel_state_content')
        # print '****niaobao_soup****', soup
        div_list = soup.find_all('div', recursive=False)

        year_opt = div_list[0].select('option')[1]
        nball = div_list[0].select('option')[1:]
        for yb in nball:
            yr = yb.text.strip()[:4]
            yid = yb.get('value').strip()
            # print '**', yr, '*', yid
            dic[yr] = yid
        # for y in year_opt:
        # print 'year', year_opt
        self.y = year_opt.text.strip()[:4]
        # print 'y', self.y
        cnt = 0
        for div in div_list[1:]:
            cnt += 1
            dn = div.find_all('span')[0].text.strip()
            # print cnt, dn
            if dn == u'基本信息':
                self.load_nianbaojiben(div)
            elif dn == u'网站或网店信息':
                self.load_nianbaowangzhan(div)
            elif dn == u'股东及出资信息':
                self.load_nianbaogudongchuzi(div)
            elif dn == u'对外投资信息':
                self.load_nianbaoduiwaitouzi(div)
            elif dn == u'行政许可情况':  # 个体工商户出现 e.g.濉溪县界沟鸿星尔克专卖
                self.load_nianbaoxingzhengxuke(div)
            elif dn == u'资产状况信息':  # 个体工商户出现
                self.load_nianbaozichangeti(div)
            elif dn == u'分支机构情况':  # 个体工商户出现 e.g. 青阳县五梅经济林农民专业合作社
                self.load_nianbaofenzhijigou(div)
            elif dn == u'生产经营情况':  # 与企业资产状况信息区别? e.g. 安徽修正堂药房连锁经营有限公司阜南县任庙店
                self.load_nianbaoshengchanjingying(div)
            elif dn == u'企业资产状况信息':
                self.load_nianbaozichanzhuangkuang(div)
            elif dn == u'对外提供保证担保信息':
                self.load_nianbaoduiwaidanbao(div)
            elif dn == u'股权变更信息':
                self.load_nianbaoguquanbiangeng(div)
            elif dn == u'修改记录':
                self.load_nianbaoxiugai(div)
            else:
                # print u'未知区域div，看看是什么', dn
                self.info(u'未知区域div，看看是什么'+ dn)
        # print 'dic_before:', dic
        if len(dic) > 1:
            dic.pop(self.y)
            # print 'dic_after:', dic
            for y in dic.keys():
                urln = 'http://ah.gsxt.gov.cn/yearExm/QYNBXX.jspx?ram='+str(random.random())+'&id='+self.mainID+'&yearId='+dic[y]
                # print 'url', y, urln
                self.y = y

                try:
                    r = self.get_request(url=urln)
                except:
                    self.info(u'该企业年度报告信息无法打开')
                    break
                soup = BeautifulSoup(r.text, 'html5lib')
                soup = soup.find(class_='panel_state_content')
                # print '****niaobao_soup****', soup
                div_list = soup.find_all('div', recursive=False)

                year_opt = div_list[0].select('option')[1]
                nball = div_list[0].select('option')[1:]

                cnt = 0
                for div in div_list[1:]:
                    cnt += 1
                    dn = div.find_all('span')[0].text.strip()
                    # print cnt, dn
                    if dn == u'基本信息':
                        self.load_nianbaojiben(div)
                    elif dn == u'网站或网店信息':
                        self.load_nianbaowangzhan(div)
                    elif dn == u'股东及出资信息':
                        self.load_nianbaogudongchuzi(div)
                    elif dn == u'对外投资信息':
                        self.load_nianbaoduiwaitouzi(div)
                    elif dn == u'行政许可情况':  # 个体工商户出现 e.g.濉溪县界沟鸿星尔克专卖
                        self.load_nianbaoxingzhengxuke(div)
                    elif dn == u'资产状况信息':  # 个体工商户出现
                        self.load_nianbaozichangeti(div)
                    elif dn == u'分支机构情况':  # 个体工商户出现 e.g. 青阳县五梅经济林农民专业合作社
                        self.load_nianbaofenzhijigou(div)
                    elif dn == u'生产经营情况':  # 与企业资产状况信息区别? e.g. 安徽修正堂药房连锁经营有限公司阜南县任庙店
                        self.load_nianbaoshengchanjingying(div)
                    elif dn == u'企业资产状况信息':
                        self.load_nianbaozichanzhuangkuang(div)
                    elif dn == u'对外提供保证担保信息':
                        self.load_nianbaoduiwaidanbao(div)
                    elif dn == u'股权变更信息':
                        self.load_nianbaoguquanbiangeng(div)
                    elif dn == u'修改记录':
                        self.load_nianbaoxiugai(div)
                    else:
                        # print u'未知区域div，看看是什么', dn
                        self.info(u'未知区域div，看看是什么' + dn)
        if self.nbjb_list:
            self.json_result['report_base'] = self.nbjb_list  # 年报基本信息
        if self.nbzczk_list:
            self.json_result['industry_status'] = self.nbzczk_list  # 年报资产状况

        if self.nbdwdb_list:
            self.json_result['guarantee'] = self.nbdwdb_list
        if self.nbgdcz_list:
            self.json_result['enterprise_shareholder'] = self.nbgdcz_list
        if self.nbgqbg_list:
            self.json_result['equity_transfer'] = self.nbgqbg_list
        if self.nbwz_list:
            self.json_result['web_site'] = self.nbwz_list
        if self.nbxg_list:
            self.json_result['modify'] = self.nbxg_list
        if self.nbdwtz_list:
            self.json_result['investment'] = self.nbdwtz_list


    def load_nianbaojiben(self, soup):
        """
        年报基本信息
        :param soup:  年报基本信息内容的soup
        :return:
        """
        family = 'report_base'
        table_id = '40'
        tr_element_list = soup.find_all('tr')#(".//*[@id='jbxx']/table/tbody/tr")
        values = {}
        json_list = []
        for tr_element in tr_element_list[1:]:
            # th_element_list = tr_element.find_all('th')
            td_element_list = tr_element.find_all('td')
            for td in td_element_list:
                if td.text.strip():
                    td_list = td.text.replace(u'·', '').replace(u' ', '').strip().replace(u' ', '').split(u'：',1)
                    col = td_list[0].strip()
                    val = td_list[1].strip()
                    # print col, val
                    col = qiyenianbaojiben_column_dict[col]
                    values[col] = val
        values['rowkey'] = '%s_%s_%s_' %(self.cur_mc, self.y, table_id)
        values[family + ':registrationno'] = self.cur_zch
        values[family + ':enterprisename'] = self.cur_mc
        json_list.append(values)
        self.nbjb_list.append(values)
        # if json_list:
        #     # print 'nianbaojibenxinxi', json_list
        #     self.json_result[family] = json_list

    def load_nianbaowangzhan(self, soup):
        """
        年报网站信息
        :param soup: 网站内容的soup
        :return:
        """
        family = 'web_site'
        table_id = '41'
        values = {}
        json_list = []
        try:
            tr_num = len(soup.find_all(class_='detailsList'))
        except:
            tr_num = 0
        # print 'lentr', tr_num
        if tr_num > 1:
            gd_th = soup.find_all(class_='detailsList')[0].find_all('th')
            # print 'th_previous',cc.find(id='altDiv').find_previous_sibling().text
            try:
                iftr = soup.find_all(class_='detailsList')[1].find_all('tr')
            except:
                iftr = []
            if len(iftr) > 0:
                cnt = 1
                for i in range(len(iftr)):
                    if iftr[i].text.strip():
                        gd_td = iftr[i].find_all('td')
                        for j in range(len(gd_th)):
                            th = gd_th[j].text.strip()
                            td = gd_td[j].text.strip()
                            # print i,j,th,td
                            values[qiyenianbaowangzhan_column_dict[th]] = td
                        values['rowkey'] = '%s_%s_%s_%d' %(self.cur_mc, self.y, table_id, cnt)
                        values[family + ':registrationno'] = self.cur_zch
                        values[family + ':enterprisename'] = self.cur_mc
                        values[family + ':id'] = str(cnt)
                        json_list.append(values)
                        self.nbwz_list.append(values)
                        values = {}
                        cnt += 1
                # if json_list:
                #     # print 'nianbaowangzhan', json_list
                #     self.json_result[family] = json_list

    def load_nianbaogudongchuzi(self, soup):
        """
        年报股东出资信息
        :param soup:  股东内容soup
        :return:
        """
        family = 'enterprise_shareholder'
        table_id = '42'
        values = {}
        json_list = []
        try:
            tr_num = len(soup.find_all(class_='detailsList'))
        except:
            tr_num = 0

        if tr_num > 1:
            gd_th = soup.find_all(class_='detailsList')[0].find_all('th')
            # print 'th_previous',cc.find(id='altDiv').find_previous_sibling().text
            try:
                iftr = soup.find_all(class_='detailsList')[1].find_all('tr')
            except:
                iftr = []
            if len(iftr) > 0:
                cnt = 1
                for i in range(len(iftr)):
                    if iftr[i].text.strip():
                        gd_td = iftr[i].find_all('td')
                        for j in range(len(gd_th)):
                            th = gd_th[j].text.strip()
                            td = gd_td[j].text.strip()
                            # print i,j,th,td
                            values[qiyenianbaogudong_column_dict[th]] = td
                        values['rowkey'] = '%s_%s_%s_%d' %(self.cur_mc, self.y, table_id, cnt)
                        values[family + ':registrationno'] = self.cur_zch
                        values[family + ':enterprisename'] = self.cur_mc
                        values[family + ':id'] = str(cnt)
                        json_list.append(values)
                        self.nbgdcz_list.append(values)
                        values = {}
                        cnt += 1
                # if json_list:
                #     # print 'nianbaogudongchuzi', json_list
                #     self.json_result[family] = json_list

    def load_nianbaoxingzhengxuke(self, soup):
        # 个体工商户年报·行政许可暂缺字段
        pass

    def load_nianbaozichangeti(self, soup):
        # 个体工商户年报·资产状况暂缺字段
        pass

    def load_nianbaofenzhijigou(self, soup):
        # 个体工商户年报·分支机构情况暂缺字段
        pass

    def load_nianbaoshengchanjingying(self, soup):
        # 年报生产经营情况
        pass

    def load_nianbaoduiwaitouzi(self, soup):
        """
        年报对外投资信息
        :param soup: 对外投资内容soup
        :return:
        """
        family = 'investment'
        table_id = '47'
        values = {}
        json_list = []

        try:
            tr_num = len(soup.find_all(class_='detailsList'))
        except:
            tr_num = 0

        if tr_num > 1:
            gd_th = soup.find_all(class_='detailsList')[0].find_all('th')
            # print 'th_previous',cc.find(id='altDiv').find_previous_sibling().text
            try:
                iftr = soup.find_all(class_='detailsList')[1].find_all('tr')
            except:
                iftr = []

            if len(iftr) > 0:
                cnt = 1
                for i in range(len(iftr)):
                    if iftr[i].text.strip():
                        gd_td = iftr[i].find_all('td')
                        for j in range(len(gd_th)):
                            th = gd_th[j].text.strip()
                            td = gd_td[j].text.strip()
                            # print i,j,th,td
                            values[qiyenianbaoduiwaitouzi_column_dict[th]] = td
                        values['rowkey'] = '%s_%s_%s_%d' %(self.cur_mc, self.y, table_id, cnt)
                        values[family + ':registrationno'] = self.cur_zch
                        values[family + ':enterprisename'] = self.cur_mc
                        values[family + ':id'] = str(cnt)
                        json_list.append(values)
                        self.nbdwtz_list.append(values)
                        values = {}
                        cnt += 1
                # if json_list:
                #     # print 'nianbaoduiwaitouzi', json_list
                #     self.json_result[family] = json_list

    def load_nianbaozichanzhuangkuang(self, soup):
        """
        年报资产状况信息
        :param soup: 资产状况内容soup
        :return:
        """
        family = 'industry_status'
        table_id = '43'

        tr_element_list = soup.find_all("tr")
        values = {}
        json_list = []
        for tr_element in tr_element_list[1:]:
            # th_element_list = tr_element.find_all('th')
            td_element_list = tr_element.find_all('td')
            if len(td_element_list) > 0:
                col_nums = len(td_element_list)
                for i in range(col_nums/2):
                    col = td_element_list[i*2].get_text().strip().replace('\n','')
                    val = td_element_list[i*2+1].get_text().strip().replace('\n','')
                    if col != u'':
                        values[qiyenianbaozichanzhuangkuang_column_dict[col]] = val
#                     print col,val
        values['rowkey'] = '%s_%s_%s_' %(self.cur_mc, self.y, table_id)
        values[family + ':registrationno'] = self.cur_zch
        values[family + ':enterprisename'] = self.cur_mc
        json_list.append(values)
        self.nbzczk_list.append(values)
        # if json_list:
        #     # print 'json_nianbaozichan', json_list
        #     self.json_result[family] = json_list

    def load_nianbaoduiwaidanbao(self, soup):
        """
        年报对外担保信息
        :param soup: 对外担保内容soup
        :return:
        """
        family = 'guarantee'
        table_id = '44'
        values = {}
        json_list = []

        try:
            tr_num = len(soup.find_all(class_='detailsList'))
        except:
            tr_num = 0

        if tr_num > 1:
            gd_th = soup.find_all(class_='detailsList')[0].find_all('th')
            # print 'th_previous',cc.find(id='altDiv').find_previous_sibling().text
            try:
                iftr = soup.find_all(class_='detailsList')[1].find_all('tr')
            except:
                iftr = []
            if len(iftr) > 0:
                cnt = 1
                for i in range(len(iftr)):
                    if iftr[i].text.strip():
                        gd_td = iftr[i].find_all('td')
                        for j in range(len(gd_th)):
                            th = gd_th[j].text.strip()
                            td = gd_td[j].text.strip()
                            # print i,j,th,td
                            values[qiyenianbaoduiwaidanbao_column_dict[th]] = td
                        values['rowkey'] = '%s_%s_%s_%d' %(self.cur_mc, self.y, table_id, cnt)
                        values[family + ':registrationno'] = self.cur_zch
                        values[family + ':enterprisename'] = self.cur_mc
                        values[family + ':id'] = str(cnt)
                        json_list.append(values)
                        self.nbdwdb_list.append(values)
                        values = {}
                        cnt += 1
                # if json_list:
                #     # print 'nianbaoduiwaidanbao', json_list
                #     self.json_result[family] = json_list

    def load_nianbaoguquanbiangeng(self, soup):
        """
        年报股权变更信息
        :param soup: 股权变更soup内容
        :return:
        """
        family = 'equity_transfer'
        table_id = '45'
        values = {}
        json_list = []

        try:
            tr_num = len(soup.find_all(class_='detailsList'))
        except:
            tr_num = 0

        if tr_num > 1:
            gd_th = soup.find_all(class_='detailsList')[0].find_all('th')
            # print 'th_previous',cc.find(id='altDiv').find_previous_sibling().text
            try:
                iftr = soup.find_all(class_='detailsList')[1].find_all('tr')
            except:
                iftr = []
            if len(iftr) > 0:
                cnt = 1
                for i in range(len(iftr)):
                    if iftr[i].text.strip():
                        gd_td = iftr[i].find_all('td')
                        for j in range(len(gd_th)):
                            th = gd_th[j].text.strip()
                            td = gd_td[j].text.strip()
                            # print i,j,th,td
                            values[qiyenianbaoguquanbiangeng_column_dict[th]] = td
                        values['rowkey'] = '%s_%s_%s_%d' %(self.cur_mc, self.y, table_id, cnt)
                        values[family + ':registrationno'] = self.cur_zch
                        values[family + ':enterprisename'] = self.cur_mc
                        values[family + ':id'] = str(cnt)
                        json_list.append(values)
                        self.nbgqbg_list.append(values)
                        values = {}
                        cnt += 1
                # if json_list:
                #     # print 'nianbaoguquanbiangeng', json_list
                #     self.json_result[family] = json_list

    def load_nianbaoxiugai(self, soup):
        """
        年报修改信息
        :param soup:  修改soup内容
        :return:
        """
        family = 'modify'
        table_id = '46'
        values = {}
        json_list = []

        try:
            tr_num = len(soup.find_all(class_='detailsList'))
        except:
            tr_num = 0

        if tr_num > 1:
            gd_th = soup.find_all(class_='detailsList')[0].find_all('th')
            # print 'th_previous',cc.find(id='altDiv').find_previous_sibling().text
            try:
                iftr = soup.find_all(class_='detailsList')[1].find_all('tr')
            except:
                iftr = []
            if len(iftr) > 0:
                cnt = 1
                for i in range(len(iftr)):
                    if iftr[i].text.strip():
                        gd_td = iftr[i].find_all('td')
                        for j in range(len(gd_th)):
                            th = gd_th[j].text.strip()
                            td = gd_td[j].text.strip()
                            # print i,j,th,td
                            values[qiyenianbaoxiugaijilu_column_dict[th]] = td
                        values['rowkey'] = '%s_%s_%s_%d' %(self.cur_mc, self.y, table_id, cnt)
                        values[family + ':registrationno'] = self.cur_zch
                        values[family + ':enterprisename'] = self.cur_mc
                        values[family + ':id'] = str(cnt)
                        json_list.append(values)
                        self.nbxg_list.append(values)
                        values = {}
                        cnt += 1
                # if json_list:
                #     # print 'nianbaoxiugai', json_list
                #     self.json_result[family] = json_list

    def get_request_302(self, url, t=0, **kwargs):
        """
        手动处理包含302的请求
        :param url:
        :param t:
        :return:
        """
        try:
            for i in range(10):
                if self.use_proxy:
                    self.headers['Proxy-Authorization'] = self.proxy_config.get_auth_header(lock_id=self.lock_id, release_id=self.release_id)
                r = self.session.get(url=url, headers=self.headers, allow_redirects=False, timeout=self.timeout, **kwargs)
                # print '+' * 500
                # print r.status_code
                # print r.text
                # print '+' * 500
                if r.status_code != 200:
                    # print '+'*500
                    # print r.status_code
                    # print r.text
                    # print '+' * 500
                    if 300 <= r.status_code < 400:
                        self.release_id = '0'
                        protocal, addr = urllib.splittype(url)
                        url = protocal + '://' + urllib.splithost(addr)[0] + r.headers['Location']
                        continue
                    # elif self.province in (u'浙江省', u'北京市') and r.status_code == 504:
                    #     del self.session
                    #     self.session = requests.session()
                    #     self.session.proxies = self.proxy_config.get_proxy()
                    #     raise Exception(u'504错误')
                    # elif r.status_code == 403:
                    #     if self.use_proxy:
                    #         if self.lock_id != '0':
                    #             self.proxy_config.release_lock_id(self.lock_id)
                    #     else:
                    #         raise Exception(u'IP被封')
                    raise StatusCodeException(u'错误的响应代码 -> %d' % r.status_code)
                else:
                    if self.release_id != '0':
                        self.release_id = '0'
                    return r
        except (ChunkedEncodingError, StatusCodeException, ReadTimeout, ConnectTimeout, ProxyError, ConnectionError) as e:
            if t == 5:
                raise e
            else:
                return self.get_request_302(url, t+1, **kwargs)

    def post_request(self, url, t=0, **kwargs):
        """
        发送post请求,包含添加代理,锁定ip与重试机制
        :param url: 请求的url
        :param t: 重试次数
        :return:
        """
        try:
            if 'timeout' not in kwargs:
                kwargs['timeout'] = self.timeout
            if 'headers' not in kwargs:
                kwargs['headers'] = self.headers
            if self.use_proxy:
                kwargs['headers']['Proxy-Authorization'] = self.proxy_config.get_auth_header(lock_id=self.lock_id, release_id=self.release_id)
            r = self.session.post(url=url, **kwargs)
            # print r.status_code,r.headers,r.text
            if r.status_code != 200:

                self.info(u'错误的响应代码 -> %d\n%s' % (r.status_code, url))
                if self.province in (u'浙江省', u'北京市') and r.status_code == 504:
                    del self.session
                    self.session = requests.session()
                    self.session.proxies = self.proxy_config.get_proxy()
                    raise Exception(u'504错误')
                if r.status_code == 403:
                    if self.use_proxy:
                        if self.lock_id != '0':
                            self.proxy_config.release_lock_id(self.lock_id)
                            self.lock_id = self.proxy_config.get_lock_id()
                            self.release_id = self.lock_id
                    else:
                        raise Exception(u'IP被封')
                raise StatusCodeException(u'错误的响应代码 -> %d\n%s' % (r.status_code, url))
            else:
                if self.release_id != '0':
                    self.release_id = '0'
                return r
        except (ChunkedEncodingError, StatusCodeException, ReadTimeout, ConnectTimeout, ProxyError, ConnectionError) as e:
            if t == 15:
                raise e
            else:
                return self.post_request(url, t+1, **kwargs)

    def get_lock_id(self):
        """
        请求过程加载动态代理ip锁定程序，1为锁定ip
        :param self:
        :return:
        """
        if self.use_proxy:
            self.release_lock_id()
            self.lock_id = self.proxy_config.get_lock_id()
            self.release_id = self.lock_id

    def release_lock_id(self):
        """
        请求过程锁定ip释放程序，0为释放ip
        :param self:
        :return:
        """
        if self.use_proxy and self.lock_id != '0':
            self.proxy_config.release_lock_id(self.lock_id)
            self.lock_id = '0'

def get_args():
    """
    获取产品客户的查询内容及账户信息的方法
    :return:
    """
    args = dict()
    for arg in sys.argv:
        kv = arg.split('=')
        if kv[0] == 'companyName':
            args['companyName'] = kv[1].decode(sys.stdin.encoding, 'ignore')
        elif kv[0] == 'taskId':
            args['taskId'] = kv[1].decode(sys.stdin.encoding, 'ignore')
            args['taskId'] = kv[1].decode(sys.stdin.encoding, 'ignore')
        elif kv[0] == 'accountId':
            args['accountId'] = kv[1].decode(sys.stdin.encoding, 'ignore')
    return args


# if __name__ == '__main__':
#     args_dict = get_args()
#     searcher = AnHui('GSCrawlerTest')
#     searcher.submit_search_request(u"安徽海德石油化工有限公司")
#     # searcher.submit_search_request(u"安徽省水泥制品有限公司")#安徽省绮蔚商贸有限公司")
#     # 安徽省企之源广告策划公司")#安徽海德石油化工有限公司")  # 安徽省茶叶公司蚌埠市批发站")#安徽华星化工股份有限公司") #
#     #安徽古酒业有限公司")#安徽华隆塑料有限责任公司")#安徽宝庭门业有限公司")
#     #合肥浍溪新能源汽车技术有限公司")#颍上县艺之家装饰工程有限公司")#霍山县工艺厂")#芜湖歌斐证捷投资中心（有限合伙）")
#     #阜阳市物资回收总公司第一经营部")#肥西合宴福酒店（普通合伙）")#合肥钢铁集团有限公司")#泾县月亮湾吊车租赁部")#亳州市元一置业有限公司")芜湖县城北友谊印刷厂
#     # searcher.get_tag_a_from_page(u"银川塔木金商贸有限公司")
#     print json.dumps(searcher.json_result, ensure_ascii=False)

if __name__ == '__main__':
    args_dict = get_args()    # 获取账户信息和查询内容
    searcher = AnHui('GSCrawlerResultTest')    # 设置kafka消息队列的topic
    searcher.submit_search_request(u"合肥华耀电子工业有限公司")    # 提交查询请求
    # searcher.submit_search_request(u"安徽省水泥制品有限公司")#安徽省绮蔚商贸有限公司")
    # 安徽省企之源广告策划公司")#安徽海德石油化工有限公司")  # 安徽省茶叶公司蚌埠市批发站")#安徽华星化工股份有限公司") #
    #安徽古酒业有限公司")#安徽华隆塑料有限责任公司")#安徽宝庭门业有限公司")
    #合肥浍溪新能源汽车技术有限公司")#颍上县艺之家装饰工程有限公司")#霍山县工艺厂")#芜湖歌斐证捷投资中心（有限合伙）")
    #阜阳市物资回收总公司第一经营部")#肥西合宴福酒店（普通合伙）")#合肥钢铁集团有限公司")#泾县月亮湾吊车租赁部")#亳州市元一置业有限公司")芜湖县城北友谊印刷厂
    # searcher.get_tag_a_from_page(u"银川塔木金商贸有限公司")
    print json.dumps(searcher.json_result, ensure_ascii=False)

# test part
# if __name__ == '__main__':
#     searcher = AnHui('GSCrawlerResultTest')
#     f = open('E:\\ah30.txt', 'r').readlines()
#     # print f, len(f), f[0].strip().decode('gbk').encode('utf8')
#     cnt = 1
#     for name in f:
#
#         try:
#             word = name.strip().decode('gbk')#.encode('utf8')
#             print 'word',word,type(word)#.strip().decode('gbk').encode('utf8')
#         except:
#             word = name.strip()
#             print 'word2',word
#         try:
#             searcher.submit_search_request(word)
#             print cnt, json.dumps(searcher.json_result, ensure_ascii=False)
#         except:
#             print '***error***:', word
#             pass
#         cnt += 1