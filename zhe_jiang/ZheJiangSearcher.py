# coding=utf-8
from gs.Searcher import Searcher
from gs.Searcher import get_args
from geetest_broker.GeetestBroker import GeetestBrokerOffline
import requests
import os
import sys
import re
import time
import platform
if platform.system() == 'Windows':
    import PyV8
else:
    from pyv8 import PyV8
import subprocess
from bs4 import BeautifulSoup
from TableConfig import *
from gs.TimeUtils import get_cur_time, get_cur_ts_mil
import json
import urllib
from requests.exceptions import ReadTimeout
from requests.exceptions import ConnectTimeout
from requests.exceptions import ProxyError
from requests.exceptions import ConnectionError
from requests.exceptions import ChunkedEncodingError
from gs.MyException import StatusCodeException
from gs.USCC import check
import datetime
reload(sys)
sys.setdefaultencoding('utf8')


class ZheJiangSearcher(Searcher, GeetestBrokerOffline):
    """
    工商浙江省为最严厉省份，ip一旦被封，永不释放，除非网站有重大版本的更新
    """
    load_func_dict = {}
    corpid = None    # 对应表内容的id
    regno = None    # 企业的注册号

    def __init__(self, dst_topic=None):
        """
        设置查询结果存放的kafka的topic
        :param dst_topic: 调用kafka程序的目标topic，topic分测试环境和正式环境
        :return:
        """
        super(ZheJiangSearcher, self).__init__(use_proxy=True, dst_topic=dst_topic)
        # self.load_func_dict[u'登记信息'] = self.get_deng_ji
        # self.load_func_dict[u'基本信息'] = self.get_ji_ben
        # self.load_func_dict[u'股东信息'] = self.get_gu_dong
        # self.load_func_dict[u'变更信息'] = self.get_bian_geng
        # self.load_func_dict[u'备案信息'] = self.get_bei_an
        # self.load_func_dict[u'主要人员信息'] = self.get_zhu_yao_ren_yuan
        # self.load_func_dict[u'分支机构信息'] = self.get_fen_zhi_ji_gou
        # self.load_func_dict[u'清算信息'] = self.get_qing_suan
        # self.load_func_dict[u'投资人信息'] = self.get_tou_zi_ren
        # self.load_func_dict[u'主管部门（出资人）信息'] = self.get_zhu_guan_bu_men     #Modified by Jing
        # self.load_func_dict[u'参加经营的家庭成员姓名'] = self.load_jiatingchengyuan     # Modified by Jing
        # self.load_func_dict[u'合伙人信息'] = self.load_hehuoren     #Modified by Jing
        # self.load_func_dict[u'成员名册'] = self.load_chengyuanmingce     #Modified by Jing
        # self.load_func_dict[u'撤销信息'] = self.load_chexiao     #Modified by Jing
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0",
                        "Host": "zj.gsxt.gov.cn",
                        "Accept": "*/*",
                        "Accept-Encoding": "gzip, deflate",
                        "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
                        "Referer": "http://zj.gsxt.gov.cn/client/entsearch/toEntSearch",
                        "Connection": "keep-alive"
                        }
        self.set_config()
        # self.log_name = self.topic + "_" + str(uuid.uuid1())
        self.domain = 'http://zj.gsxt.gov.cn/client/entsearch/'

    def set_config(self):
        """
        加载配置信息，注释掉的内容由统一调用程序配置
        :return:
        """
        # self.plugin_path = os.path.join(sys.path[0], '../zhe_jiang/ocr/jisuan/zhejiang.bat')
        # self.group = 'Crawler'  # 正式
        # self.kafka = KafkaAPI("GSCrawlerResult")  # 正式
        # self.group = 'CrawlerTest'  # 测试
        # self.kafka = KafkaAPI("GSCrawlerTest")  # 测试
        # self.topic = 'GsSrc33'
        self.province = u'浙江省'
        # self.kafka.init_producer()
        self.set_request_timeout(20)

    # def recognize_yzm(self, yzm_path):
    #     """
    #     识别验证码
    #     :param yzm_path: 验证码保存路径
    #     :return: 验证码识别结果
    #     """
    #     cmd = self.plugin_path + " " + yzm_path
    #     # print cmd
    #     process = subprocess.Popen(cmd.encode('GBK', 'ignore'), stdout=subprocess.PIPE)
    #     process_out = process.stdout.read()
    #     process_out = process_out.strip()
    #     answer = process_out.split('\r\n')[-1].strip()
    #     if answer.endswith(yzm_path):
    #         answer = u''
    #     # print 'answer: ' + answer.decode('gbk', 'ignore')
    #     return answer.decode('gbk', 'ignore')

    def download_yzm(self):
        """
        下载验证码
        :return: 验证码路径
        """
        # print 'lock_id -> %s' % self.lock_id
        image_url = 'http://gsxt.zjaic.gov.cn/common/captcha/doReadKaptcha.do'
        r = self.get_request(image_url)
        # print 1, r.headers
        yzm_path = self.get_yzm_path().replace('/', '\\')
        with open(yzm_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
                    f.flush()
            f.close()
        return yzm_path

    def save_tag_a_to_db(self, tag_a):
        """
        数据库存入查询结果tag的url连接
        :param tag_a:
        :return:
        """
        pass

    def get_tag_a_from_db(self, keyword):
        """
        从数据库获取url连接
        :param keyword:
        :return:
        """
        return None

    def get_the_mc_or_code(self, keyword):
        """
        判断keyword为公司名还是信用代码
        :param keyword:
        :return:
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

    def get_tag_a_from_page(self, keyword):
        """
        输入内容判断
        :param keyword: 输入查询内容
        :param flags: 信用代码或公司名称
        :return:
        """
        return self.get_tag_a_from_page0(keyword)

    def get_coding_art(self, keyword):
        """
        此部分为工商浙江的最核心技术难点部分，此部分内容可以避免极验验证码和
        随机弹出的滑动验证码。极大的提升了验证码拖延速度的瓶颈。
        :param keyword: 查询内容
        :return: 查询内容的JS加密后内容
        """
        doer = PyV8.JSContext()
        doer.enter()               # js解析PyV8环境搭建
        # path = sys.path[0] + '/des.js'
        # print os.path.dirname(__file__)
        path = os.path.join(os.path.dirname(__file__), 'des.js')    # 验证码加密JS路径
        # print 'path:', path
        f = open(path).read()   # 读取js代码
        # print f
        doer.eval(f)  # 预加载js代码的function
        if type(keyword) == unicode:
            worded = doer.eval("strEnc('%s','a','b','c')" % keyword.encode('utf-8'))
        else:
            worded = doer.eval("strEnc('%s','a','b','c')" % keyword)
        # print 'worded', keyword, worded
        return worded

    def get_tag_a_from_page0(self, keyword):
        """
        搜索过程逻辑实现，加载验证码（伪），锁定ip，
        :param keyword: 查询的输入内容
        :return: 查询结果div
        """
        if check(keyword):
            is_xydm = True
        else:
            is_xydm = False
        keyworded = self.get_coding_art(keyword)
        url = 'http://zj.gsxt.gov.cn/client/entsearch/list?isOpanomaly=&pubType=1&searchKeyWord=%s' % keyworded
        print 'url', url
        r = self.get_request(url=url)
        soup = BeautifulSoup(r.text, 'html5lib')
        soup = soup.find(class_='enterprise-info-list')
        # print 'souped', soup
        if not soup.text.strip():
            # print u'***验证码识别通过***no_result***'
            self.info(u'***验证码识别通过***no_result***')
            return None
        if soup.find('li'):
            # print 'r.headers', r.headers
            # print u'**********验证码识别通过***安徽*********'  #, soup.find(class_='list')
            self.info(u'**********验证码识别通过***浙江*********')
            if soup.find('li').text.strip() != u'':
                return soup.find_all('li')
            else:
                self.info(u'查询无结果')
                return None

    def get_search_args(self, tag_a, keyword):
        """
        解析查询结果内容
        :param tag_a: 查询结果div
        :param keyword: 查询输入内容
        :return:
        """
        if check(keyword):
            is_xydm = True
        else:
            is_xydm = False
        gsm_list = []    # 公司名列表
        lik_list = []    # 公司详情url列表
        dat_list = []    # 公司日期列表
        if len(tag_a) > 1:
            for ta in tag_a:
                cm = ta.find('span').text.strip().replace('(', u'（').replace(')', u'）').strip()
                lik = ta.find('a').get('href')
                try:
                    dat = ta.find_all('span')[-1].text.strip().split(u'：')[1]
                except:
                    self.info('dat-ept')
                    dat = ta.find_all('span')[-1].text.strip()
                # print cm, lik, dat
                if is_xydm or cm == keyword:
                    gsm_list.append(cm)
                    lik_list.append(lik)
                    dat_list.append(dat)

                # print 'cmpame', cm, dat
                # self.save_company_name_to_db(cm)

        # 出现重名公司按日期排序并选择日期距离现在最近的公司
        try:
            ct = gsm_list.count(keyword)
            if ct <= 1:
                n = gsm_list.index(keyword)
            else:
                rq_list = []
                od_list = []
                for s in range(len(gsm_list)):
                    if gsm_list[s] == keyword:
                        rq = dat_list[s]
                        rq_list.append(rq)
                        od_list.append(s)
                # print rq_list
                rq_list = [q.replace(u'年', '-').replace(u'月', '-').replace(u'日', '') for q in rq_list]
                # print rq_list
                xx = sorted(rq_list)
                nn = rq_list.index(xx[-1])
                # print xx
                n = od_list[nn]
            # print 'list_n', n, ct
        except:
            n = 0
        tag_a = tag_a[n]
        # print 'tag_a', tag_a
        name = tag_a.find('span').text.strip()   # name为公司查询结果名；keyword为查询前数据库公司名
        name_link = tag_a.find('a').get('href')
        # mainID = re.search(r'(?<=id=).*',name_link).group()
        # mainID = tag_a.find_all('p')[0].find_all('span')[-1].get('id')
        try:
            code = tag_a.div.find_all('span')[0].text.strip().replace(' ', '').replace(u'\n', '').replace(u'\t', '').split(u'：')[1]    # 注册号
        except:
            code = tag_a.div.find_all('span')[0].text.strip().replace(' ', '').replace(u'\n', '').replace(u'\t', '').split(u':')[1]    # 注册号
        tagA = self.domain + name_link  # 验证码通过后链接地址
        # print '+++++++', name, '##', code, 'mainID:', mainID
        # self.mainID = mainID  # 安徽有分页情况可能用到
        self.cur_mc = name.replace('(', u'（').replace(')', u'）').strip()
        self.cur_zch = code
        self.tagA = tagA  # 安徽三大参数，公司名称name，注册号code， 跳过验证码的地址tagA
        if is_xydm or self.cur_mc == keyword:
            # print 'same'
            self.info(u'查询结果一致')
            return 1
        else:
            # print 'insane'
            self.info(u'查询结果不一致')
            self.save_company_name_to_db(self.cur_mc)
            return 0

        # print u'公司名(name)cur_mc: %s, 注册号(code)cur_zch: %s,tagA:%s' % (name, code, tagA)
        # if self.flag:
        #     # print 'mc',self.cur_mc,'kw',keyword
        #     if self.cur_mc == keyword:
        #         # print 'same'
        #         self.info(u'查询结果一致')
        #         return 1
        #     else:
        #         # print 'insane'
        #         self.info(u'查询结果不一致')
        #         self.save_company_name_to_db(self.cur_mc)
        #         return 0
        # else:
        #     self.info(self.cur_mc)
        #     return 1

    def parse_detail(self):
        """
        解析公司详情信息
        :param kwargs:
        :return:
        """
        r = self.get_request(url=self.tagA)
        soup = BeautifulSoup(r.text, 'html5lib')
        # print '*taga*', soup
        prid = soup.find(id='params').input.get('value')
        regNO = soup.find(id='regNO').get('value')
        # print self.tagA
        encrypripid = re.search(u'(?<=Id=).*(?=&)', self.tagA).group()
        # print '***prid', prid, '**regNO', regNO, '***encrypripid', encrypripid
        self.prid = prid
        self.regNO = regNO
        self.encrypripid = encrypripid
        bd = soup.find(class_='tab-panel')
        divs = bd.find_all(class_='mod-bd-panel_company')
        cnt = 1
        for div in divs:
            dv = div.find('h3').text.strip()
            # print '*', cnt, dv
            cnt += 1
            if u'营业执照信息' == dv:
                self.info(u'解析基本信息...')
                self.get_ji_ben(div)
            elif u'股东及出资信息' in dv and u'截止' in dv:
                self.info(u'解析股东信息...')
                self.get_gu_dong(div)
            elif u'主管部门（出资人）信息' in dv:
                self.info(u'解析主管部门出资人信息')
                self.get_gu_dong(div)
            elif u'投资人信息' in dv:
                self.info(u'投资人信息')
                self.get_gu_dong(div)
            elif u'股东及出资信息' in dv:
                self.info(u'解析股东出资详情信息')
                # self.get_gu_dong_details(div)
            elif u'变更信息' == dv:
                self.info(u'解析变更信息')
                self.get_bian_geng(div)
            elif u'主要人员信息' in dv:
                self.info(u'解析主要人员信息')
                self.get_zhu_yao_ren_yuan(div)
            elif u'合伙人信息' in dv:
                self.info(u'合伙人')
                self.get_gu_dong(div)

            # elif u'分支机构信息' in dv:
            #     self.info(u'解析分支机构信息')
            #     self.get_fen_zhi_ji_gou(div)
        #     elif u'清算信息' == dv:
        #         self.info(u'解析清算信息')
        #         self.get_qing_suan(div)
        #     elif u'动产抵押登记信息' == dv:
        #         self.info(u'解析动产抵押信息')
        #         self.get_dong_chan_di_ya(div)
        #     elif u'股权出质登记信息' == dv:
        #         self.info(u'解析股权出质信息')
        #         self.get_gu_quan_chu_zhi(div)
        #
        #     elif u'抽查检查结果信息' == dv:
        #         self.info(u'解析抽查检查信息')
        #         self.get_chou_cha_jian_cha(div)
        #
        # self.get_xing_zheng_chu_fa()
        # self.get_jing_ying_yi_chang()
        # self.get_yan_zhong_wei_fa()

        return

    def get_regno(self):
        """
        获取注册登记号
        :return:
        """
        url = 'http://gsxt.zjaic.gov.cn/appbasicinfo/doViewAppBasicInfo.do'
        params = {'corpid': self.corpid}
        r = self.get_request(url=url, params=params)
        soup = BeautifulSoup(r.text, 'lxml')
        h_element = soup.find_all('h2')[0].text
        regno_info = h_element.split('\n')[2].replace(u'注册号：','')
        self.regno = regno_info.strip()

    # def get_deng_ji(self):
    #     """
    #     加载登记信息，需要重新发送请求
    #     :return:
    #     """
    #     for i in range(5):
    #         url = 'http://gsxt.zjaic.gov.cn/appbasicinfo/doReadAppBasicInfo.do'
    #         params = {'corpid': self.corpid}
    #         r = self.get_request(url=url, params=params)
    #         if u'系统警告' in r.text and i < 4:
    #             continue
    #         elif u'系统警告' in r.text and i == 4:
    #             break
    #         else:
    #             soup = BeautifulSoup(r.text, 'lxml')
    #             table_elements = soup.find_all("table")
    #             for table_element in table_elements:
    #                 table_name = table_element.find("th").get_text().strip()  # 表格名称
    #                 if u'股东信息' in table_name:
    #                     self.get_gu_dong(table_element)
    #                 elif table_name in self.load_func_dict:
    #                     self.load_func_dict[table_name](table_element)
    #                 else:
    #                     self.info(u'未知表名')

    def get_ji_ben(self, table_element):
        """
        查询基本信息
        :param table_element: 基本信息的soup内容
        :return: 基本信息结果
        """
        """
        查询基本信息
        :return: 基本信息结果
        """
        json_list = []
        family = 'Registered_Info'
        table_id = '01'
        self.json_result[family] = []

        li_element_list = table_element.find_all('li')
        values = {}
        for td in li_element_list:
            if td.text.strip():
                td_list = td.text.replace(u'·', '').replace(u'•', '').replace(u' ', '').strip().replace(u' ', '').split(u'：',1)
                col = td_list[0].strip()
                val = td_list[1].strip()
                # print col, val
                col = jiben_column_dict[col]
                values[col] = val
        # print 'cur_time', get_cur_time()

        values['rowkey'] = '%s_%s_%s_' % (self.cur_mc, table_id, self.cur_zch)
        print 'self.cur_zch', self.cur_zch, values['rowkey']
        values[family + ':registrationno'] = self.cur_zch
        values[family + ':enterprisename'] = self.cur_mc
        xydm = ''
        zch = ''
        if check(self.cur_zch):
            xydm = self.cur_zch
        else:
            zch = self.cur_zch
        values[family + ':tyshxy_code'] = xydm
        values[family + ':zch'] = zch
        values[family + ':lastupdatetime'] = get_cur_time()
        values[family + ':province'] = u'浙江省'
        json_list.append(values)
        self.json_result[family] = json_list

    def get_gu_dong(self, table_element):
        """
        查询股东信息，需要重新发送请求
        :param table_element: 股东信息的soup内容
        :return:
        """
        family = 'Shareholder_Info'
        table_id = '04'
        # self.json_result[family] = []
        values = {}
        json_list = []
        url = 'http://zj.gsxt.gov.cn/midinv/list.json?_t='+get_cur_ts_mil()
        params = {'length': 5, 'params[priPID]': self.prid, 'start': 0}
        r = self.post_request(url=url, params=params,is_json=True)
        jsn = json.loads(r.content)
        # print '*gudong*', jsn
        # print '1', jsn['recordsTotal'], '2', jsn['recordsFiltered'], '3', jsn['data']
        num = jsn['recordsTotal']
        num = int(num)
        # print 'num', num
        if num%5 == 0:
            rnd = num/5
        else:
            rnd = num/5 + 1
        lists = jsn['data']
        cnt = 1
        if lists:
            for ele in lists:
                # 可选择的参数
                gdtype = ele[u'invType']              # 股东类型代号
                gd = ele[u'inv']                # 股东!!
                # zjlx = ele[]                    # 证件类型
                zjhm = ele[u'bLicNO']       # 证件号码 当股东类型为1时候有效
                gd_id = ele[u'id']              # 详情可能使用的id参数
                gdlxbk = ele[u'cerTypeName']    # 股东代号不为1时的股东类型

                if gdtype == '1':
                    gdlx = u'企业法人'              # 股东类型!!
                    zjlx = u'法人营业执照'        # 证件类型!!
                    zjcode = zjhm                    # 证件号码!!
                elif gdtype == '2':
                    gdlx = u'自然人'
                    zjlx = gdlxbk               # 股东为非法人类型的证件类型
                    zjcode = u'非公示项'
                elif gdtype == '3':
                    gdlx = u'其它股东'
                    zjlx = gdlxbk               # 股东为非法人类型的证件类型
                    zjcode = u'非公示项'
                else:
                    gdlx = u''
                    zjlx = gdlxbk               # 股东为非法人类型的证件类型
                    zjcode = u'非公示项'

                # 查看详情
                # print '*',cnt, gdlx, gd, zjlx, zjcode
                if gd_id:
                    url = 'http://zj.gsxt.gov.cn/midinv/findMidInvById?midInvId=%s' % gd_id
                    # print 'gddsurl:', url
                    self.get_gd_detail(values, url)
                else:
                    url = ''
                values[gudong_column_dict[u'股东类型']] = gdlx
                values[gudong_column_dict[u'股东']] = gd
                values[gudong_column_dict[u'证照/证件类型']] = zjlx
                values[gudong_column_dict[u'证照/证件号码']] = zjcode
                values[gudong_column_dict[u'详情']] = url
                values['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.cur_zch, self.today, cnt)
                values[family + ':registrationno'] = self.cur_zch
                values[family + ':enterprisename'] = self.cur_mc
                values[family + ':id'] = str(cnt)
                json_list.append(values)
                values = {}
                cnt += 1

            if rnd > 1:
                if rnd > 200:
                    self.info(u'老多股东了')
                    rnd = 200
                for t in range(1, rnd):
                    url = 'http://zj.gsxt.gov.cn/midinv/list.json?_t='+get_cur_ts_mil()
                    params = {'length': 5, 'params[priPID]': self.prid, 'start': t*5}
                    try:
                        r = self.post_request(url=url, params=params,is_json=True)
                        # print 'rex', r.text
                    except Exception:
                        # print 'break@round', t
                        self.info(u'无力回合%d' %t)
                        break
                    try:
                        jsn = json.loads(r.content)
                    except Exception as e:
                        print t, e
                        continue
                    # print '*gudong*', t, jsn
                    lists = jsn['data']
                    if lists:
                        for ele in lists:
                            # 可选择的参数
                            gdtype = ele[u'invType']              # 股东类型代号
                            gd = ele[u'inv']                # 股东!!
                            # zjlx = ele[]                    # 证件类型
                            zjhm = ele[u'bLicNO']       # 证件号码  当股东类型为1时候有效
                            gd_id = ele[u'id']              # 详情可能使用的id参数
                            gdlxbk = ele[u'cerTypeName']    # 股东代号不为1时的股东类型

                            if gdtype == '1':
                                gdlx = u'企业法人'              # 股东类型!!
                                zjlx = u'法人营业执照'        # 证件类型!!
                                zjcode = zjhm                    # 证件号码!!
                            elif gdtype == '2':
                                gdlx = u'自然人'
                                zjlx = gdlxbk               # 股东为非法人类型的证件类型
                                zjcode = u'非公示项'
                            elif gdtype == '3':
                                gdlx = u'其它股东'
                                zjlx = gdlxbk               # 股东为非法人类型的证件类型
                                zjcode = u'非公示项'
                            else:
                                gdlx = u''
                                zjlx = gdlxbk               # 股东为非法人类型的证件类型
                                zjcode = u'非公示项'

                            # 查看详情
                            # print '*', cnt, gdlx, gd, zjlx, zjcode
                            if gd_id:
                                url = 'http://zj.gsxt.gov.cn/midinv/findMidInvById?midInvId=%s' % gd_id
                                # print 'gddsurl:', 'cnt', cnt, url
                                self.get_gd_detail(values, url)
                            else:
                                url = ''
                            values[gudong_column_dict[u'股东类型']] = gdlx
                            values[gudong_column_dict[u'股东']] = gd
                            values[gudong_column_dict[u'证照/证件类型']] = zjlx
                            values[gudong_column_dict[u'证照/证件号码']] = zjcode
                            values[gudong_column_dict[u'详情']] = url
                            values['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.cur_zch, self.today, cnt)
                            values[family + ':registrationno'] = self.cur_zch
                            values[family + ':enterprisename'] = self.cur_mc
                            values[family + ':id'] = str(cnt)
                            json_list.append(values)
                            values = {}
                            cnt += 1
            if json_list:
                # print 'gudong_json', json_list
                self.json_result[family] = json_list

    def get_gd_detail(self, values, url):
        """
        获取股东详情信息
        :param values: 股东内容字典
        :param url: 股东详情内容的url
        :return:
        """
        values = values
        url = url
        r = self.get_request(url=url)
        # print r.text
        soup = BeautifulSoup(r.text, 'html5lib')
        # print 'gd-details-soup', soup
        div_elements = soup.find_all(class_='mod-bd-panel_company')    # div
        for div in div_elements:
            title = div.find('h3').text.strip()
            table = div.find('table')
            if title == u'企业资产状况信息':

                tr_list = table.find_all('tr')[1:]              # 去掉股东
                for tre in tr_list:
                    td_list = tre.find_all('td')
                    col_num = len(td_list)/2
                    for i in range(col_num):
                        col = td_list[i*2].text.strip()
                        if not col:
                            # print 'dj'
                            continue
                        val = td_list[i*2+1].text.strip()
                        # print 'dc**djxx', col, val
                        values[gudong_column_dict[col]] = val

            elif title == u'认缴明细信息':
                th_list = table.find_all('tr')[0].find_all('th')
                text = table.find('tbody').contents[1]
                tess = str(text).replace(' ','')
                table1 = BeautifulSoup(tess, 'html.parser')
                # print 'table1', table1
                tr_list = table1.find_all('tr')
                # print len(tr_list)
                # for tr in tr_list:
                    # print 'mm', tr,tr.find_all('td'),len(tr.find_all('td'))
                if len(tr_list) > 0:
                    dyn = 1
                    if len(tr_list) == 1:
                        for tre in tr_list:
                            col_num = len(th_list)
                            td_list = tre.find_all('td')
                            for i in range(col_num):
                                col = th_list[i].text.strip()
                                val = td_list[i].text.strip()
                                # print u'γγ', col, val
                                values[gudong_column_dict[col]] = val
                    elif len(tr_list) == 2:
                        for tre in tr_list[1:]:
                            # print 'tre', tre
                            col_num = len(th_list)
                            td_list = tre.find_all('td')
                            for i in range(col_num):
                                col = th_list[i].text.strip()
                                val = td_list[i].text.strip()
                                # print u'γγ', col, val
                                values[gudong_column_dict[col]] = val

            elif title == u'实缴明细信息':
                th_list = table.find_all('tr')[0].find_all('th')
                text = table.find('tbody').contents[1]
                tess = str(text).replace(' ','')
                table2 = BeautifulSoup(tess, 'html.parser')
                # print 'table2', table2
                tr_list = table2.find_all('tr')
                if len(tr_list) > 0:
                    dyn = 1
                    if len(tr_list) == 1:
                        for tre in tr_list:
                            col_num = len(th_list)
                            td_list = tre.find_all('td')
                            for i in range(col_num):
                                col = th_list[i].text.strip()
                                val = td_list[i].text.strip()
                                # print u'γγ', col, val
                                values[gudong_column_dict[col]] = val
                    elif len(tr_list) == 2:
                        for tre in tr_list[1:]:
                            col_num = len(th_list)
                            td_list = tre.find_all('td')
                            for i in range(col_num):
                                col = th_list[i].text.strip()
                                val = td_list[i].text.strip()
                                # print u'γγ', col, val
                                values[gudong_column_dict[col]] = val

    def get_tou_zi_ren(self, table_element):
        """
        加载投资人信息，由股东信息实现
        :param table_element:
        :return:
        """
        pass

    def get_bian_geng(self, table_element):
        """
        查询变更信息，需要重新发送请求
        :return:变更信息
        """
        family = 'Changed_Announcement'
        table_id = '05'
        values = {}
        json_list = []

        url = 'http://zj.gsxt.gov.cn/midaltitem/list.json?_t='+get_cur_ts_mil()
        params = {'length': 5, 'params[priPID]': self.prid, 'start': 0,'params[entTypeCatg]':11}
        r = self.post_request(url=url, params=params,is_json=True)
        #print 'rex', r.text
        jsn = json.loads(r.content)
        # print jsn
        # print '*biangeng*', jsn
        # print '1', jsn['recordsTotal'], '2', jsn['recordsFiltered'], '3', jsn['data']
        num = jsn['recordsTotal']

        num = int(num)
        if num%5 == 0:
            rnd = num/5
        else:
            rnd = num/5 + 1
        lists = jsn['data']
        cnt = 1
        if lists:
            for ele in lists:
                # 可选择的参数
                bgsx = ele[u'altContent']              # 变更事项
                bgbe = ele[u'altBeContent']         # 变更前
                bgaf = ele[u'altAfContent']           # 变更后
                bgdt = ele[u'altDate']                   # 变更日期
                bgmb = ele[u'altItem']                  # 变更可能的参数

                # 查看详情
                # print '*', cnt, bgsx, bgbe, bgaf, bgdt
                values[biangeng_column_dict[u'变更事项']] = bgsx
                values[biangeng_column_dict[u'变更前内容']] = bgbe
                values[biangeng_column_dict[u'变更后内容']] = bgaf
                values[biangeng_column_dict[u'变更日期']] = bgdt
                values['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.cur_zch, self.today, cnt)
                values[family + ':registrationno'] = self.cur_zch
                values[family + ':enterprisename'] = self.cur_mc
                values[family + ':id'] = str(cnt)
                json_list.append(values)
                values = {}
                cnt += 1

            if rnd > 1:

                for t in range(1, rnd):
                    #print t
                    url = 'http://zj.gsxt.gov.cn/midaltitem/list.json?_t='+get_cur_ts_mil()
                    params = {'length': 5, 'params[priPID]': self.prid, 'start': t*5,'params[entTypeCatg]':11}
                    r = self.post_request(url=url, params=params,is_json=True)
                    #print 'rex', r.text

                    jsn = json.loads(r.content)

                    # print '*gudong*', jsn
                    lists = jsn['data']
                    if lists:
                        for ele in lists:
                            # 可选择的参数
                            bgsx = ele[u'altContent']              # 变更事项
                            bgbe = ele[u'altBeContent']         # 变更前
                            bgaf = ele[u'altAfContent']           # 变更后
                            bgdt = ele[u'altDate']                   # 变更日期
                            bgmb = ele[u'altItem']                  # 变更可能的参数

                            # 查看详情
                            # print '*', cnt, bgsx, bgbe, bgaf, bgdt
                            values[biangeng_column_dict[u'变更事项']] = bgsx
                            values[biangeng_column_dict[u'变更前内容']] = bgbe
                            values[biangeng_column_dict[u'变更后内容']] = bgaf
                            values[biangeng_column_dict[u'变更日期']] = bgdt
                            values['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.cur_zch, self.today, cnt)
                            values[family + ':registrationno'] = self.cur_zch
                            values[family + ':enterprisename'] = self.cur_mc
                            values[family + ':id'] = str(cnt)
                            json_list.append(values)
                            values = {}
                            cnt += 1

            if json_list:
                # print 'biangeng_json', json_list
                self.json_result[family] = json_list

    def get_bei_an(self):
        """
        获取备案信息内容
        :return:
        """
        for i in range(5):
            url = 'http://gsxt.zjaic.gov.cn/filinginfo/doViewFilingInfo.do'
            params = {'corpid': self.corpid}
            r = self.get_request(url=url, params=params)
            if u'系统警告' in r.text and i < 4:
                continue
            elif u'系统警告' in r.text and i == 4:
                break
            else:
                soup = BeautifulSoup(r.text, 'lxml')
                table_elements = soup.find_all("table")
                for table_element in table_elements:
                    table_name = table_element.find("th").get_text().strip()  # 表格名称
                    if table_name in self.load_func_dict:
                        self.load_func_dict[table_name](table_element)
                    else:
                        self.info(u'未知表名')
                break

    def get_zhu_yao_ren_yuan(self, table_element):
        """
        查询主要人员信息
        :param table_element:
        :return:
        """
        family = 'KeyPerson_Info'
        table_id = '06'
        values = {}
        json_list = []

        url = 'http://zj.gsxt.gov.cn/midmember/list.json?_t='+get_cur_ts_mil()
        params = {'priPID': self.prid}
        r = self.post_request(url=url, params=params,is_json=True)
        #print 'rex', r.text
        jsn = json.loads(r.content)
        # print '*biangeng*', jsn
        lists = jsn
        cnt = 1
        if lists:
            for ele in lists:
                # 可选择的参数
                xm = ele[u'name']                       # 姓名
                zw = ele[u'posiContent']             # 职位
                # print cnt, 'xm', xm, 'zw', zw
                values[zhuyaorenyuan_column_dict[u'姓名']] = xm
                values[zhuyaorenyuan_column_dict[u'职务']] = zw
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

    def get_fen_zhi_ji_gou(self, table_element):
        """
        查询分支机构信息
        :param table_element:
        :return:
        """
        family = 'Branches'
        table_id = '08'
        values = {}
        json_list = []
        url = 'http://zj.gsxt.gov.cn/midbranch/list.json?_t='+get_cur_ts_mil()
        params = {'priPID': self.prid}
        r = self.post_request(url=url, params=params,is_json=True)
        # print 'rex', r.text
        jsn = json.loads(r.content)
        # print '*biangeng*', jsn
        lists = jsn
        cnt = 1
        if lists:
            for ele in lists:
                # 可选择的参数
                fgs = ele[u'entName']           # 分公司
                zch = ele[u'regNO']              # 注册号
                zcj = ele[u'regOrgName']     # 注册局
                # print cnt, 'fgs', fgs, 'zch', zch, 'zcj', zcj
                values[fenzhijigou_column_dict[u'名称']] = fgs
                values[fenzhijigou_column_dict[u'注册号']] = zch
                values[fenzhijigou_column_dict[u'登记机关']] = zcj
                values['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.cur_zch, self.today, cnt)
                values[family + ':registrationno'] = self.cur_zch
                values[family + ':enterprisename'] = self.cur_mc
                values[family + ':id'] = str(cnt)
                json_list.append(values)
                values = {}
                cnt += 1
        if json_list:
            # print 'fenzhijigou_jsonlist:', json_list
            self.json_result[family] = json_list

    def get_qing_suan(self, table_element):
        """
        查询清算信息
        :param table_element:
        :return:
        """
        family = 'liquidation_Information'
        table_id = '09'
        values = {}
        json_list = []
        url = 'http://zj.gsxt.gov.cn/midliquidation/get.json?_t='+get_cur_ts_mil()
        params = {'priPID': self.prid}
        r = self.post_request(url=url, params=params,is_json=True)
        # print 'rex', r.text
        jsn = json.loads(r.content)
        # print '*qs*', jsn
        lists = jsn
        cnt = 1
        if lists:
            ele = lists
            chief = ele[u'ligPrincipal']            # 负责人
            memb = ele[u'liqMem']                # 组成员
            # print cnt, 'chief', chief, 'memb', memb
            values[qingsuan_column_dict[u'清算组负责人']] = chief
            values[qingsuan_column_dict[u'清算组成员']] = memb
            values['rowkey'] = '%s_%s_%s_%s_' % (self.cur_mc, table_id, self.cur_zch, self.today)
            values[family + ':registrationno'] = self.cur_zch
            values[family + ':enterprisename'] = self.cur_mc
            if chief or memb:
                json_list.append(values)
            if json_list:
                self.json_result[family] = json_list

    def get_dong_chan_di_ya(self, table_element):
        """
        查询动产抵押信息
        :return:动产抵押信息
        """
        family = 'Chattel_Mortgage'
        table_id = '11'
        values = {}
        json_list = []
        url = 'http://zj.gsxt.gov.cn/pub/mortreginfo/list.json?_t='+get_cur_ts_mil()
        params = {'length': 5, 'params[regNO]': self.regNO, 'params[uniCode]': self.cur_zch, 'start': 0}
        # print 'params', params
        r = self.post_request(url=url, params=params,is_json=True)
        #print 'rex', r.text
        jsn = json.loads(r.content)
        #print '*dcdy*', jsn
        # print '1', jsn['recordsTotal'], '2', jsn['recordsFiltered'], '3', jsn['data']
        num = jsn['recordsTotal']
        num = int(num)
        if num%5 == 0:
            rnd = num/5
        else:
            rnd = num/5 + 1
        lists = jsn['data']
        cnt = 1

        # self.dcdydj_list = []
        # self.dyqrgk_list = []
        # self.bdbzqgk_list = []
        # self.dywgk_list = []
        # self.dcdybg_list = []
        # self.dcdyzx_list = []

        if lists:
            for ele in lists:
                # 可选择的参数
                djbh = ele[u'filingNO']              # 登记编号
                djrq = ele[u'checkDate']                # 登记日期
                djjg = ele[u'departMentName']                    # 登记机关
                bdbzqse = ele[u'mortGageAmount']       # 被担保债权数额
                zt = ele[u'cancelStatus']              # 状态    为0时为'有效'，其他为'-'
                dtlid = ele[u'id']                      # 详情链接可能需要的id号
                gsrq = ele[u'checkDate']    # 公示日期  YY-mm-dd转格式
                if zt == 0:
                    ztcode = u'有效'
                else:
                    ztcode = u'-'

                if bdbzqse:
                    zqse = str(bdbzqse)+u' 万元'        # 债权数额
                else:
                    zqse = u''
                if gsrq:
                    nyr = gsrq.split(u'-')
                    gsrq_cn = u'%s年%s月%s日' % (nyr[0], nyr[1], nyr[2])       # 转换后日期
                else:
                    gsrq_cn = u''

                # 查看详情
                # print '*', cnt, djbh, gsrq_cn, djjg, bdbzqse, ztcode, gsrq_cn, url
                if dtlid:
                    url = 'http://zj.gsxt.gov.cn/pub/mortreginfo/detail?id=%s' % dtlid
                    # print 'dcdydts_url:', url
                    detail=self.get_dcdy_detail(url)

                else:
                    url = ''
                values[dongchandiyadengji_column_dict[u'登记编号']] = djbh
                values[dongchandiyadengji_column_dict[u'登记日期']] = gsrq_cn
                values[dongchandiyadengji_column_dict[u'登记机关']] = djjg
                values[dongchandiyadengji_column_dict[u'被担保债权数额']] = zqse
                values[dongchandiyadengji_column_dict[u'状态']] = ztcode
                values[dongchandiyadengji_column_dict[u'公示日期']] = gsrq_cn
                values[dongchandiyadengji_column_dict[u'详情']] = url
                values[family+':detail']=detail
                values['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.cur_zch, self.today, cnt)
                values[family + ':registrationno'] = self.cur_zch
                values[family + ':enterprisename'] = self.cur_mc
                values[family + ':id'] = str(cnt)
                print values
                json_list.append(values)
                values = {}
                cnt += 1

            if rnd > 1:
                for t in range(1, rnd):
                    url = 'http://zj.gsxt.gov.cn/midinv/list.json?_t='+get_cur_ts_mil()
                    params = {'length': 5, 'params[priPID]': self.prid, 'start': t*5}
                    r = self.post_request(url=url, params=params,is_json=True)
                    # print 'rex', r.text
                    jsn = json.loads(r.content)
                    # print '*gudong*', jsn
                    lists = jsn['data']
                    if lists:
                        for ele in lists:
                            # 可选择的参数
                            djbh = ele[u'filingNO']              # 登记编号
                            djrq = ele[u'checkDate']                # 登记日期
                            djjg = ele[u'departMentName']                    # 登记机关
                            bdbzqse = ele[u'mortGageAmount']       # 被担保债权数额
                            zt = ele[u'cancelStatus']              # 状态    为0时为'有效'，其他为'-'
                            dtlid = ele[u'id']                      # 详情链接可能需要的id号
                            gsrq = ele[u'checkDate']    # 公示日期  YY-mm-dd转格式
                            if zt == 0:
                                ztcode = u'有效'
                            else:
                                ztcode = u'-'

                            if bdbzqse:
                                zqse = bdbzqse+u'万元'        # 债权数额
                            else:
                                zqse = u''
                            if gsrq:
                                nyr = gsrq.split(u'-')
                                gsrq_cn = u'%s年%s月%s日' % (nyr[0], nyr[1], nyr[2])       # 转换后日期
                            else:
                                gsrq_cn = u''

                            # 查看详情
                            # print '*', cnt, djbh, gsrq_cn, djjg, bdbzqse, ztcode, gsrq_cn, url
                            if dtlid:
                                url = 'http://zj.gsxt.gov.cn/pub/mortreginfo/detail?id=%s' % dtlid
                                # print 'dcdydts_url:', url
                                detail=self.get_dcdy_detail(url)
                            else:
                                url = ''
                            values[dongchandiyadengji_column_dict[u'登记编号']] = djbh
                            values[dongchandiyadengji_column_dict[u'登记日期']] = gsrq_cn
                            values[dongchandiyadengji_column_dict[u'登记机关']] = djjg
                            values[dongchandiyadengji_column_dict[u'被担保债权数额']] = zqse
                            values[dongchandiyadengji_column_dict[u'状态']] = ztcode
                            values[dongchandiyadengji_column_dict[u'公示日期']] = gsrq_cn
                            values[dongchandiyadengji_column_dict[u'详情']] = url
                            values[family+':detail']=detail
                            values['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.cur_zch, self.today, cnt)
                            values[family + ':registrationno'] = self.cur_zch
                            values[family + ':enterprisename'] = self.cur_mc
                            values[family + ':id'] = str(cnt)
                            json_list.append(values)
                            values = {}
                            cnt += 1
            if json_list:
                # print 'dcdy_json', json_list
                self.json_result[family] = json_list
                # self.info(self.json_result[family])

            # if self.dcdydj_list:
            #     self.json_result['dcdydj'] = self.dcdydj_list
            # if self.dyqrgk_list:
            #     self.json_result['dyqrgk'] = self.dyqrgk_list
            # if self.bdbzqgk_list:
            #     self.json_result['bdbzqgk'] = self.bdbzqgk_list
            # if self.dywgk_list:
            #     self.json_result['dywgk'] = self.dywgk_list
            # if self.dcdybg_list:
            #     self.json_result['dcdybg'] = self.dcdybg_list
            # if self.dcdyzx_list:
            #     self.json_result['dcdyzx'] = self.dcdyzx_list

    def get_dcdy_detail(self, link):
        """
        动产抵押登记详情信息
        :param link: 详情url地址
        :return:
        """
        values = {}
        url = link
        r = self.get_request(url=url)
        # print r.text
        soup = BeautifulSoup(r.text, 'html5lib')
        # print 'dcdy-details-soup', soup
        div_elements = soup.find_all(class_='mod-bd-panel_company')    # div
        for div in div_elements:
            title = div.find('h3').text.strip()
            table = div.find('table')
            if title == u'动产抵押登记信息':
                values[title] = {}
                family = 'dcdydj'
                tableID = '63'
                json_list = []
                djbh = u''
                djrq = u''
                tr_list = table.find_all('tr')
                for tre in tr_list:
                    td_list = tre.find_all('td')
                    col_num = len(td_list)/2
                    for i in range(col_num):
                        col = td_list[i*2].text.strip()
                        if not col:
                            continue
                        val = td_list[i*2+1].text.strip()
                        values[title][col] = val
                #         if col == u'登记编号':
                #             djbh = val
                #             self.djbh = djbh
                #         if col == u'登记日期':
                #             djrq = val
                #             self.djrq = djrq
                # values['rowkey'] = '%s_%s_%s_%s' %(self.cur_mc, self.djbh, self.djrq, tableID)
                # values[family + ':registrationno'] = self.cur_zch
                # values[family + ':enterprisename'] = self.cur_mc
                # # json_list.append(values)
                # self.dcdydj_list.append(values)


                # self.json_result[family] = json_list

            elif title == u'被担保债权概况信息':
                values[title] = {}
                family = 'bdbzqgk'
                tableID = '56'

                json_list = []

                tr_list = table.find_all('tr')
                for tre in tr_list:
                    td_list = tre.find_all('td')
                    col_num = len(td_list)/2
                    for i in range(col_num):
                        col = td_list[i*2].text.strip()
                        if not col:
                            # print 'bdbzqgk'
                            continue
                        val = td_list[i*2+1].text.strip()
                        # print 'dc**bdbrgk', col, val
                        values[title][col] = val
                # values['rowkey'] = '%s_%s_%s_%s' %(self.cur_mc, self.djbh, self.djrq, tableID)
                # values[family + ':registrationno'] = self.cur_zch
                # values[family + ':enterprisename'] = self.cur_mc
                # # json_list.append(values)
                # self.bdbzqgk_list.append(values)
                # # self.json_result[family] = json_list
            elif title == u'注销':
                values[title] = {}
                family = 'dcdyzx'
                tableID = '59'

                json_list = []

                tr_list = table.find_all('tr')
                for tre in tr_list:
                    td_list = tre.find_all('td')
                    col_num = len(td_list)/2
                    for i in range(col_num):
                        col = td_list[i*2].text.strip()
                        if not col:
                            # print 'zx'
                            continue
                        val = td_list[i*2+1].text.strip()
                        # print 'dc**zx', col, val
                        values[title][col] = val
                # values['rowkey'] = '%s_%s_%s_%s' %(self.cur_mc, self.djbh, self.djrq, tableID)
                # values[family + ':registrationno'] = self.cur_zch
                # values[family + ':enterprisename'] = self.cur_mc
                # # json_list.append(values)
                # self.dcdyzx_list.append(values)
                # # self.json_result[family] = json_list

            elif title == u'抵押权人概况信息':
                values[title] = []
                family = 'dyqrgk'
                tableID = '55'
                json_list = []

                th_list = table.find_all('tr')[0].find_all('th')
                tr_list = table.find_all('tr')
                gkn = 1  # 概况递增id
                if len(tr_list) > 1:
                    for tre in tr_list[1:]:
                        one_col={}
                        col_num = len(th_list)
                        td_list = tre.find_all('td')
                        for i in range(col_num):
                            col = th_list[i].text.strip()
                            val = td_list[i].text.strip()
                            # print u'@@', col, val
                            one_col[col]=val
                            #values[dcdy_diyaquanren_column_dict[col]] = val
                        values[title].append(one_col)
                    #     values['rowkey'] = '%s_%s_%s_%s%d' %(self.cur_mc, self.djbh, self.djrq, tableID, gkn)
                    #     values[family + ':registrationno'] = self.cur_zch
                    #     values[family + ':enterprisename'] = self.cur_mc
                    #     values[family + ':id'] = str(gkn)
                    #     try:
                    #         values.pop(dcdy_diyaquanren_column_dict[u'序号'])
                    #     except KeyError as e:
                    #         # self.info(u'%s' % e)
                    #         pass
                    #     # json_list.append(values)
                    #     self.dyqrgk_list.append(values)
                    #     values = {}
                    #     gkn += 1
                    # # if json_list:
                    # #     self.json_result[family] = json_list

            elif title == u'抵押物概况信息':
                values[title] = []
                family = 'dywgk'
                tableID = '57'

                json_list = []

                th_list = table.find_all('tr')[0].find_all('th')
                tr_list = table.find_all('tr')
                dyn = 1
                if len(tr_list) > 1:
                    for tre in tr_list[1:]:
                        one_col={}
                        col_num = len(th_list)
                        td_list = tre.find_all('td')
                        for i in range(col_num):
                            col = th_list[i].text.strip()
                            val = td_list[i].text.strip()
                            # print u'ββ', col, val
                            one_col[col] = val
                        values[title].append(one_col)
                    #     values['rowkey'] = '%s_%s_%s_%s%d' %(self.cur_mc, self.djbh, self.djrq, tableID, dyn)
                    #     values[family + ':registrationno'] = self.cur_zch
                    #     values[family + ':enterprisename'] = self.cur_mc
                    #     values[family + ':id'] = str(dyn)
                    #     try:
                    #         values.pop(dcdy_diyawu_column_dict[u'序号'])
                    #     except KeyError as e:
                    #         # self.info(u'%s' % e)
                    #         pass
                    #     # json_list.append(values)
                    #     self.dywgk_list.append(values)
                    #     values = {}
                    #     dyn += 1
                    #
                    # # if json_list:
                    # #     self.json_result[family] = json_list

            elif title == u'变更':
                values[title] = []
                family = 'dcdybg'
                tableID = '58'

                json_list = []


                th_list = table.find_all('tr')[0].find_all('th')
                tr_list = table.find_all('tr')
                if len(tr_list) > 1:
                    dyn = 1
                    for tre in tr_list[1:]:
                        one_col={}
                        col_num = len(th_list)
                        td_list = tre.find_all('td')
                        for i in range(col_num):
                            col = th_list[i].text.strip()
                            val = td_list[i].text.strip()
                            one_col[col]=val
                            # print u'γγ', col, val
                            #values[dcdy_biangeng_column_dict[col]] = val
                        values.append(one_col)
                        # values['rowkey'] = '%s_%s_%s_%s%d' %(self.cur_mc, self.djbh, self.djrq, tableID, dyn)
                        # values[family + ':registrationno'] = self.cur_zch
                        # values[family + ':enterprisename'] = self.cur_mc
                        # values[family + ':id'] = str(dyn)
                        # try:
                        #     values.pop(dcdy_biangeng_column_dict[u'序号'])
                        # except KeyError as e:
                        #     # self.info(u'*%s' % e)
                        #     pass
                        # json_list.append(values)
                        # self.dcdybg_list.append(values)
                        # values = {}
                        # dyn += 1

            else:
                self.info(u'unknown0title:%s' % title)
        return values
    def get_gu_quan_chu_zhi(self, table_element):
        """
        查询动产抵押信息
        :return:动产抵押信息
        """
        family = 'Equity_Pledge'
        table_id = '13'
        values = {}
        json_list = []
        url = 'http://zj.gsxt.gov.cn/pub/sppledge/list.json?_t='+get_cur_ts_mil()
        params = {'length': 5, 'params[priPID]': self.prid, 'start': 0}
        r = self.post_request(url=url, params=params,is_json=True)
        # print 'rex', r.text
        jsn = json.loads(r.content)
        # print '*gudong*', jsn
        # print '1', jsn['recordsTotal'], '2', jsn['recordsFiltered'], '3', jsn['data']
        num = jsn['recordsTotal']
        num = int(num)
        if num%5 == 0:
            rnd = num/5
        else:
            rnd = num/5 + 1
        lists = jsn['data']
        cnt = 1

        # self.gqczbg_list = []
        # self.gqczzx_list = []

        if lists:
            for ele in lists:
                # 可选择的参数  登记编号 	出质人 	证照/证件号码 	出质股权数额 	质权人 	证照/证件号码 	股权出质设立登记日期 	状态 	公示日期 	详情
                djbh = ele[u'orderNO']              # 登记编号
                czr = ele[u'pledgor']                # 出质人
                czrzjhm = ele[u'pleBLicNO']   # 出质人证件号码  （非公示项）,为ID！！！！
                czgqse = ele[u'impAm']       # 出质股权数额
                zqr = ele[u'impOrg']              # 质权人
                zqrzjhm = ele[u'impBLicNO']    # 质权人证件号码
                djrq = ele[u'recDate']      # 股权出质设立登记日期
                zt = ele[u'status']         # 状态
                gsrq = ele[u'equPleDate']    # 公示日期
                dtlid = ele[u'id']          # 详情url可能用到的id信息

                if djrq:
                    nyr = gsrq.split(u'-')
                    djrq_cn = u'%s年%s月%s日' % (nyr[0], nyr[1], nyr[2])       # 转换后日期
                else:
                    djrq_cn = u''

                if gsrq:
                    nyr = gsrq.split(u'-')
                    gsrq_cn = u'%s年%s月%s日' % (nyr[0], nyr[1], nyr[2])       # 转换后日期
                else:
                    gsrq_cn = u''
                if zt == u'K' or zt == u'B':
                    ztcode = u'有效'
                else:
                    ztcode = u'无效'
                # 查看详情
                # print '*',cnt, djbh, czr, czrzjhm, czgqse, zqr, zqrzjhm, djrq_cn, ztcode, gsrq_cn
                if dtlid:
                    url = 'http://zj.gsxt.gov.cn/pub/sppledge/detail?id=%s' % dtlid
                    # print 'gqczurl:', url
                    detail=self.get_gqcz_detail(url)
                else:
                    url = ''
                values[guquanchuzhidengji_column_dict[u'登记编号']] = djbh
                values[guquanchuzhidengji_column_dict[u'出质人']] = czr
                values[guquanchuzhidengji_column_dict[u'证照/证件号码']] = czrzjhm
                values[guquanchuzhidengji_column_dict[u'出质股权数额']] = czgqse
                values[guquanchuzhidengji_column_dict[u'质权人']] = zqr
                values[guquanchuzhidengji_column_dict[u'证照/证件号码1']] = zqrzjhm
                values[guquanchuzhidengji_column_dict[u'股权出质设立登记日期']] = djrq_cn
                values[guquanchuzhidengji_column_dict[u'状态']] = ztcode
                values[guquanchuzhidengji_column_dict[u'公示日期']] = gsrq_cn
                values[guquanchuzhidengji_column_dict[u'详情']] = url
                values[family+':detail']=detail
                values['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.cur_zch, self.today, cnt)
                values[family + ':registrationno'] = self.cur_zch
                values[family + ':enterprisename'] = self.cur_mc
                values[family + ':id'] = str(cnt)
                json_list.append(values)
                values = {}
                cnt += 1

            if rnd > 1:
                for t in range(1, rnd):
                    url = 'http://zj.gsxt.gov.cn/midinv/list.json?_t='+get_cur_ts_mil()
                    params = {'length': 5, 'params[priPID]': self.prid, 'start': t*5}
                    r = self.post_request(url=url, params=params,is_json=True)
                    # print 'rex', r.text
                    jsn = json.loads(r.content)
                    # print '*gudong*', jsn
                    lists = jsn['data']
                    if lists:
                        for ele in lists:
                            # 可选择的参数
                            djbh = ele[u'orderNO']              # 登记编号
                            czr = ele[u'pledgor']                # 出质人
                            czrzjhm = ele[u'pleBLicNO']   # 出质人证件号码  （非公示项）,为ID！！！！
                            czgqse = ele[u'impAm']       # 出质股权数额
                            zqr = ele[u'impOrg']              # 质权人
                            zqrzjhm = ele[u'impBLicNO']    # 质权人证件号码
                            djrq = ele[u'recDate']      # 股权出质设立登记日期
                            zt = ele[u'status']         # 状态
                            gsrq = ele[u'equPleDate']    # 公示日期
                            dtlid = ele[u'id']          # 详情url可能用到的id信息

                            if djrq:
                                nyr = gsrq.split(u'-')
                                djrq_cn = u'%s年%s月%s日' % (nyr[0], nyr[1], nyr[2])       # 转换后日期
                            else:
                                djrq_cn = u''

                            if gsrq:
                                nyr = gsrq.split(u'-')
                                gsrq_cn = u'%s年%s月%s日' % (nyr[0], nyr[1], nyr[2])       # 转换后日期
                            else:
                                gsrq_cn = u''
                            if zt == u'K' or zt == u'B':
                                ztcode = u'有效'
                            else:
                                ztcode = u'无效'
                            # 查看详情
                            # print '*',cnt, djbh, czr, czrzjhm, czgqse, zqr, zqrzjhm, djrq_cn, ztcode, gsrq_cn
                            if dtlid:
                                url = 'http://zj.gsxt.gov.cn/pub/sppledge/detail?id=%s' % dtlid
                                # print 'gqczurl:', url
                                detail = self.get_gqcz_detail(url)
                            else:
                                url = ''
                            values[guquanchuzhidengji_column_dict[u'登记编号']] = djbh
                            values[guquanchuzhidengji_column_dict[u'出质人']] = czr
                            values[guquanchuzhidengji_column_dict[u'证照/证件号码']] = czrzjhm
                            values[guquanchuzhidengji_column_dict[u'出质股权数额']] = czgqse
                            values[guquanchuzhidengji_column_dict[u'质权人']] = zqr
                            values[guquanchuzhidengji_column_dict[u'证照/证件号码1']] = zqrzjhm
                            values[guquanchuzhidengji_column_dict[u'股权出质设立登记日期']] = djrq_cn
                            values[guquanchuzhidengji_column_dict[u'状态']] = ztcode
                            values[guquanchuzhidengji_column_dict[u'公示日期']] = gsrq_cn
                            values[guquanchuzhidengji_column_dict[u'详情']] = url
                            values[family+':detail']=detail
                            values['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.cur_zch, self.today, cnt)
                            values[family + ':registrationno'] = self.cur_zch
                            values[family + ':enterprisename'] = self.cur_mc
                            values[family + ':id'] = str(cnt)
                            json_list.append(values)
                            values = {}
                            cnt += 1
            if json_list:
                # print 'gqcz_json', json_list
                self.json_result[family] = json_list
            # if self.gqczbg_list:
            #     self.json_result['gqczbg'] = self.gqczbg_list
            # if self.gqczzx_list:
            #     self.json_result['gqczzx'] = self.gqczzx_list

    def get_gqcz_detail(self, link):
        """
        股权出质详情信息
        :param link:  详情对应的url
        :return:
        """
        url = link
        values = {}
        r = self.get_request(url=url)
        # print r.text
        soup = BeautifulSoup(r.text, 'html5lib')
        # print 'gqcz-details-soup', soup
        div_elements = soup.find_all(class_='mod-bd-panel_company')    # div
        for div in div_elements:
            title = div.find('h3').text.strip()
            table = div.find('table')
            if title == u'股权出质变更信息':
                values[title]=[]
                family = 'gqczbg'
                tableID = '61'
                json_list = []
                th_list = table.find_all('tr')[0].find_all('th')
                tr_list = table.find_all('tr')
                if len(tr_list) > 1:
                    dyn = 1
                    for tre in tr_list[1:]:
                        one_col={}
                        if not tre.text.strip():                # 空表不加载
                            continue
                        col_num = len(th_list)
                        td_list = tre.find_all('td')
                        for i in range(col_num):
                            col = th_list[i].text.strip()
                            val = td_list[i].text.strip()
                            # print u'γγ', col, val
                            one_col[col]=val
                        values[title].append(one_col)
                        #     values[gqcz_biangeng_column_dict[col]] = val
                        # values['rowkey'] = '%s_%s_%s_%s%d' %(self.cur_mc, self.djbh, self.djrq, tableID, dyn)
                        # values[family + ':registrationno'] = self.cur_zch
                        # values[family + ':enterprisename'] = self.cur_mc
                        # values[family + ':id'] = str(dyn)
                        # try:
                        #     values.pop(gqcz_biangeng_column_dict[u'序号'])
                        # except KeyError as e:
                        #     # self.info(u'*%s' % e)
                        #     pass
                        # json_list.append(values)
                        # self.gqczbg_list.append(values)
                        # values = {}
                        # dyn += 1

            elif title == u'股权出质注销信息':
                values[title]={}
                family = 'gqczzx'
                tableID = '60'

                json_list = []
                tr_list = table.find_all('tr')
                if len(tr_list) >= 1:
                    #dyn = 1
                    for tre in tr_list:
                        if not tre.text.strip():
                            continue
                        td_list = tre.find_all('td')

                        col = td_list[0].text.strip()
                        val = td_list[1].text.strip()
                        values[title][col] = val
                            # print u'γγ', col, val
                            #values[gqcz_zhuxiao_column_dict[col]] = val
            #             values['rowkey'] = '%s_%s_%s_%s%d' %(self.cur_mc, self.djbh, self.djrq, tableID, dyn)
            #             values[family + ':registrationno'] = self.cur_zch
            #             values[family + ':enterprisename'] = self.cur_mc
            #             values[family + ':id'] = str(dyn)
            #             try:
            #                 values.pop(gqcz_zhuxiao_column_dict[u'序号'])
            #             except KeyError as e:
            #                 # self.info(u'*%s' % e)
            #                 pass
            #             json_list.append(values)
            #             self.gqczzx_list.append(values)
            #             values = {}
            #             dyn += 1
            # else:
            #     self.info(u'gqczUnknownTitle:%s' % title)
        return values
    def get_xing_zheng_chu_fa(self):
        """
        查询行政处罚信息
        :return:
        """
        family = 'Administrative_Penalty'
        table_id = '13'
        values = {}
        json_list = []
        url = 'http://zj.gsxt.gov.cn/pub/pubotherpunish/list.json?_t='+get_cur_ts_mil()
        params = {'length': 5, 'params[priPID]': self.prid, 'start': 0}
        r = self.post_request(url=url, params=params,is_json=True)
        # print 'rex', r.text
        jsn = json.loads(r.content)
        # print '*gudong*', jsn
        # print '1', jsn['recordsTotal'], '2', jsn['recordsFiltered'], '3', jsn['data']
        num = jsn['recordsTotal']
        num = int(num)
        if num%5 == 0:
            rnd = num/5
        else:
            rnd = num/5 + 1
        lists = jsn['data']
        cnt = 1
        if lists:
            # print '****xzcf-need****'
            for ele in lists:
                # 可选择的参数   	决定书文号 	违法行为类型 	行政处罚内容 	决定机关名称 	处罚决定日期 	公示日期 	详情
                jdswh = ele[u'penDecNo']    # 决定书文号
                wfxwlx = ele[u'illegActType']    # 违法行为类型
                xzcfnr = ele[u'penContent']     # 行政处罚内容
                jdjgmc = ele[u'judAuth']     # 决定机关名称
                cfjdrq = ele[u'penDecIssDate']    # 处罚决定日期
                gsrq = ele[u'auditDate']     # 公示日期

                dtlid = ele[u'id']      # 详情url可能用到的id
                caseno = ele[u'caseNO']   # 详情url可能用到的参数

                if cfjdrq:
                    nyr = cfjdrq.split(u'-')
                    cfjdrq_cn = u'%s年%s月%s日' % (nyr[0], nyr[1], nyr[2])       # 转换后日期
                else:
                    cfjdrq_cn = u''

                if gsrq:
                    nyr = gsrq.split(u'-')
                    gsrq_cn = u'%s年%s月%s日' % (nyr[0], nyr[1], nyr[2])       # 转换后日期
                else:
                    gsrq_cn = u''

                if caseno:
                    # url = 'http://zj.gsxt.gov.cn/midinv/findMidInvById?midInvId=%s' % dtlid
                    url = 'http://zj.gsxt.gov.cn/pub/pubotherpunish/detail?caseNO=%s&priPID=%s' % (caseno, self.prid)
                    # print 'xzcfurl:', 'cnt', cnt, url
                    # r = self.get_request(url=url)
                    # print 'xingzhengchufa_text', r.content
                else:
                    url = ''

                values[xingzhengchufa_column_dict[u'决定书文号']] = jdswh
                values[xingzhengchufa_column_dict[u'违法行为类型']] = wfxwlx
                values[xingzhengchufa_column_dict[u'行政处罚内容']] = xzcfnr
                values[xingzhengchufa_column_dict[u'决定机关名称']] = jdjgmc
                values[xingzhengchufa_column_dict[u'处罚决定日期']] = cfjdrq_cn
                values[xingzhengchufa_column_dict[u'公示日期']] = gsrq_cn
                values[xingzhengchufa_column_dict[u'详情']] = url

                values['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.cur_zch, self.today, cnt)
                values[family + ':registrationno'] = self.cur_zch
                values[family + ':enterprisename'] = self.cur_mc
                values[family + ':id'] = str(cnt)
                json_list.append(values)
                values = {}
                cnt += 1

            if json_list:
                # print 'xingzhengchufa_json', json_list
                self.json_result[family] = json_list

    def get_jing_ying_yi_chang(self):
        """
        查询经营异常信息
        :return:
        """
        family = 'Business_Abnormal'
        table_id = '14'
        values = {}
        json_list = []
        url = 'http://zj.gsxt.gov.cn/pub/client/pubopanomaly/list/list.json?_t='+get_cur_ts_mil()
        params = {'length': 5, 'params[priPID]': self.prid, 'start': 0}
        r = self.post_request(url=url, params=params,is_json=True)
        # print 'rex', r.text
        jsn = json.loads(r.content)
        # print '*gudong*', jsn
        # print '1', jsn['recordsTotal'], '2', jsn['recordsFiltered'], '3', jsn['data']
        num = jsn['recordsTotal']
        num = int(num)
        if num%5 == 0:
            rnd = num/5
        else:
            rnd = num/5 + 1
        lists = jsn['data']
        cnt = 1
        if lists:
            # print '****jyyc-need****'
            for ele in lists:
                # 可选择的参数        纳入经营异常名录原因 	列入日期 	作出决定机关（列入） 	移出经营异常名录原因 	移出日期 	作出决定机关（移出）
                nrjyycmlyy = ele[u'speCauseCN']       # 纳入经营异常名录原因
                lrrq = ele[u'abnTime']                          # 列入日期
                zcjdjgin = ele[u'decorgCN']                 # 作出决定机关（列入）
                ycjyycmlyy = ele[u'remExcpresCN']    # 移出经营异常名录原因
                ycrq = ele[u'remDate']                         # 移出日期
                zcjdjgout = ele[u'reDecOrgCN']          # 作出决定机关（移出）

                if lrrq:
                    nyr = lrrq.split(u'-')
                    lrrq_cn = u'%s年%s月%s日' % (nyr[0], nyr[1], nyr[2])       # 转换后日期
                else:
                    lrrq_cn = u''

                if ycrq:
                    nyr = ycrq.split(u'-')
                    ycrq_cn = u'%s年%s月%s日' % (nyr[0], nyr[1], nyr[2])       # 转换后日期
                else:
                    ycrq_cn = u''

                values[jingyingyichang_column_dict[u'纳入经营异常名录原因']] = nrjyycmlyy
                values[jingyingyichang_column_dict[u'列入日期']] = lrrq_cn
                values[jingyingyichang_column_dict[u'作出决定机关（列入）']] = zcjdjgin
                values[jingyingyichang_column_dict[u'移出经营异常名录原因']] = ycjyycmlyy
                values[jingyingyichang_column_dict[u'移出日期']] = ycjyycmlyy
                values[jingyingyichang_column_dict[u'作出决定机关（移出）']] = zcjdjgout

                values['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.cur_zch, self.today, cnt)
                values[family + ':registrationno'] = self.cur_zch
                values[family + ':enterprisename'] = self.cur_mc
                values[family + ':id'] = str(cnt)
                json_list.append(values)
                values = {}
                cnt += 1
            if json_list:
                # print 'jingyingyichang_json', json_list
                self.json_result[family] = json_list

    def get_yan_zhong_wei_fa(self):
        """
        查询严重违法信息
        :return:严重违法信息
        """
        family = 'Serious_Violations'
        table_id = '15'
        values = {}
        json_list = []
        url = 'http://zj.gsxt.gov.cn/entinfo/illegalinfo?encryPriPID=%s&classFlag=1' % (self.encrypripid)
        # print 'yzwf_url', url
        return
        self.json_result[family] = []
        url = 'http://gsxt.zjaic.gov.cn/blacklist/doViewBlackListInfo.do'
        params = {'corpid': self.corpid}
        r = self.get_request(url=url, params=params)
        if u'系统警告' not in r.text:
            soup = BeautifulSoup(r.text, 'lxml')
            table_element = soup.find("table")
            if u'此企业暂无严重违法信息' not in table_element.text:
                th_element_list = table_element.select('th')[1:]
                tr_element_list = table_element.select('tr')[2:]
                for tr_element in tr_element_list:
                    td_element_list = tr_element.select('td')
                    col_nums = len(th_element_list)
                    self.json_result[family].append({})
                    for j in range(col_nums):
                        col_dec = th_element_list[j].text.strip().replace('\n', '')
                        col = yanzhongweifa_column_dict[col_dec]
                        td = td_element_list[j]
                        val = self.pattern.sub('', td.text)
                        self.json_result[family][-1][col] = val
        for i in range(len(self.json_result[family])):
            self.json_result[family][i]['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.cur_zch, self.today, i+1)
            self.json_result[family][i][family + ':registrationno'] = self.cur_zch
            self.json_result[family][i][family + ':enterprisename'] = self.cur_mc
            self.json_result[family][i][family + ':id'] = i+1
            # print json.dumps(self.json_result[family], ensure_ascii=False)

    def get_chou_cha_jian_cha(self, table_element):
        """
        查询抽查检查信息
        :return:抽查检查信息
        """
        family = 'Spot_Check'
        table_id = '16'
        values = {}
        json_list = []
        url = 'http://zj.gsxt.gov.cn/pubscresult/list.json?_t='+get_cur_ts_mil()
        params = {'length': 5, 'params[priPID]': self.prid, 'start': 0}
        r = self.post_request(url=url, params=params,is_json=True)
        # print 'rex', r.text
        jsn = json.loads(r.content)
        # print '*dcjc*', jsn
        # print '1', jsn['recordsTotal'], '2', jsn['recordsFiltered'], '3', jsn['data']
        num = jsn['recordsTotal']
        num = int(num)
        if num%5 == 0:
            rnd = num/5
        else:
            rnd = num/5 + 1
        lists = jsn['data']
        cnt = 1
        if lists:
            for ele in lists:
                # 可选择的参数
                jcssjg = ele[u'inspectDesc']       # 检查实施机关
                lx = ele[u'scType']                     # 类型
                rq = ele[u'inspectDate']             # 抽查日期
                jg = ele[u'scResult']                   # 结果

                if rq:
                    rqlists = rq[:10].split(u'-')
                    rq_cn = u'%s年%s月%s日' % (rqlists[0], rqlists[1], rqlists[2])       # 转换后日期
                else:
                    rq_cn = u''

                if jg == u'1':
                    jg_cn = u'正常（符合信息公示相关规定）;'
                elif jg == u'2':
                    jg_cn = u'公示信息隐瞒真实情况、弄虚作假;'
                elif jg == u'3':
                    jg_cn == u'被撤销登记;'
                elif jg == u'4':
                    jg_cn == u'未按规定公示即时信息;'
                elif jg == u'5':
                    jg_cn == u'未按规定公示年报信息;'
                elif jg == u'6':
                    jg_cn == u'不予配合情节严重;'
                elif jg == u'7':
                    jg_cn == u'通过登记的住所（经营场所）无法联系;'
                elif jg == u'8':
                    jg_cn == u'已办理营业执照注销;'
                elif jg == u'9':
                    jg_cn == u'被吊销营业执照;'
                else:
                    jg_cn == u'正常（符合信息公示相关规定）;'

                values[chouchajiancha_column_dict[u'检查实施机关']] = jcssjg
                values[chouchajiancha_column_dict[u'类型']] = lx
                values[chouchajiancha_column_dict[u'日期']] = rq_cn
                values[chouchajiancha_column_dict[u'结果']] = jg_cn
                values['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.cur_zch, self.today, cnt)
                values[family + ':registrationno'] = self.cur_zch
                values[family + ':enterprisename'] = self.cur_mc
                values[family + ':id'] = str(cnt)
                json_list.append(values)
                values = {}
                cnt += 1
            if json_list:
                # print 'chouchajiancha_json', json_list
                self.json_result[family] = json_list

    def get_request(self, url, t=0, **kwargs):
        """
        发送get请求,包含添加代理,锁定ip与重试机制
        :param url: 请求的url
        :param t: 重试次数
        """
        try:
            if 'timeout' not in kwargs:
                kwargs['timeout'] = self.timeout
            if 'headers' not in kwargs:
                kwargs['headers'] = self.headers
            if self.use_proxy:
                kwargs['headers']['Proxy-Authorization'] = self.proxy_config.get_auth_header(lock_id=self.lock_id, release_id=self.release_id)
            r = self.session.get(url=url, **kwargs)
            if r.status_code != 200:
                # print r.status_code
                self.info(u'错误的响应代码 -> %d\n%s' % (r.status_code, url))
                if self.province == u'浙江省' and r.status_code == 504:
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
                # print 't->', t
                return self.get_request(url, t+1, **kwargs)

    def post_request(self, url, t=0,is_json=False, **kwargs):
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
                if is_json:
                    try:
                        jsn = json.loads(r.content)
                    except:
                        raise StatusCodeException(u'返回内容不是json格式 ->%s' % (url))
                if self.release_id != '0':
                    self.release_id = '0'
                return r
        except (ChunkedEncodingError, StatusCodeException, ReadTimeout, ConnectTimeout, ProxyError, ConnectionError) as e:
            if t == 15:
                raise e
            else:
                time.sleep(2)
                return self.post_request(url, t+1, **kwargs)

    def get_request_302(self, url, t=0, **kwargs):
        """
        手动处理包含302的请求
        :param url:
        :param t:
        :return:
        """
        try:
            self.get_lock_id()
            # print self.lock_id
            for i in range(10):
                if self.use_proxy:
                    self.headers['Proxy-Authorization'] = self.proxy_config.get_auth_header(lock_id=self.lock_id, release_id=self.release_id)
                r = self.session.get(url=url, headers=self.headers, allow_redirects=False, timeout=self.timeout, **kwargs)
                if r.status_code != 200:
                    if 300 <= r.status_code < 400:
                        self.release_id = '0'
                        protocal, addr = urllib.splittype(url)
                        url = protocal + '://' + urllib.splithost(addr)[0] + r.headers['Location']
                        continue
                    elif self.province in (u'浙江省', u'北京市') and r.status_code == 504:
                        del self.session
                        self.session = requests.session()
                        self.session.proxies = self.proxy_config.get_proxy()
                        raise Exception(u'504错误')
                    elif r.status_code == 403:
                        if self.use_proxy:
                            if self.lock_id != '0':
                                self.proxy_config.release_lock_id(self.lock_id)
                                self.lock_id = self.proxy_config.get_lock_id()
                                self.release_id = self.lock_id
                        else:
                            raise Exception(u'IP被封')
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

    def post_request_302(self, url, t=0, **kwargs):
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
                r = self.session.post(url=url, headers=self.headers, allow_redirects=False, timeout=self.timeout, **kwargs)
                if r.status_code != 200:
                    if 300 <= r.status_code < 400:
                        protocal, addr = urllib.splittype(url)
                        url = protocal + '://' + urllib.splithost(addr)[0] + r.headers['Location']
                        # print '302 url', url
                        continue
                    elif self.province in (u'浙江省', u'北京市') and r.status_code == 504:
                        del self.session
                        self.session = requests.session()
                        self.session.proxies = self.proxy_config.get_proxy()
                        raise Exception(u'504错误')
                    elif r.status_code == 403:
                        if self.use_proxy:
                            if self.lock_id != '0':
                                self.proxy_config.release_lock_id(self.lock_id)
                                self.lock_id = self.proxy_config.get_lock_id()
                                self.release_id = self.lock_id
                        else:
                            raise Exception(u'IP被封')
                    raise StatusCodeException(u'错误的响应代码 -> %d' % r.status_code)
                else:
                    if self.release_id != '0':
                        self.release_id = '0'
                    return r
        except (ChunkedEncodingError, StatusCodeException, ReadTimeout, ConnectTimeout, ProxyError, ConnectionError) as e:
            if t == 5:
                raise e
            else:
                return self.post_request_302(url, t+1, **kwargs)

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

    def submit_search_request(self, keyword, account_id='null', task_id='null'):
        """
        提交查询请求
        :param keyword: 查询关键词(公司名称或者注册号)
        :param flags: True表示keyword代表公司名，False表示keyword代表注册号
        :param account_id: 在线更新,kafka所需参数
        :param task_id: 在线更新kafka所需参数
        :return:
        """
        if check(keyword):
            is_xydm = True
        else:
            is_xydm = False
            keyword = self.process_mc(keyword)  # 公司名称括号统一转成全角
        self.input_company_name = keyword
        self.session = requests.session()  # 初始化session
        self.add_proxy(self.app_key)  # 为session添加代理
        res = 0
        self.cur_mc = ''  # 当前查询公司名称
        self.cur_zch = ''  # 当前查询公司注册号
        self.today = str(datetime.date.today()).replace('-', '')
        self.json_result.clear()
        self.json_result['inputCompanyName'] = keyword
        self.json_result['accountId'] = account_id
        self.json_result['taskId'] = task_id
        self.save_tag_a = True
        self.info(u'keyword: %s' % keyword)
        tag_a = self.get_tag_a_from_db(keyword)
        # print 'first_tag_a', tag_a
        if not tag_a:
            # print 'not _tag_a'
            tag_a = self.get_tag_a_from_page(keyword)
        # if not tag_a:  # 等所有省份都修改结束，使用此段代码代替以上代码
        #     tag_a = self.get_tag_a_from_page(keyword, flags)
        if tag_a:
            # print 'have _tag_a', tag_a
            # args = self.get_search_args(tag_a, keyword)
            if self.get_search_args(tag_a, keyword):
                if self.save_tag_a:  # 查询结果与所输入公司名称一致时,将其写入数据库
                    self.save_tag_a_to_db(tag_a)
                self.info(u'解析详情信息')
                self.parse_detail()
                res = 1
            # else:
            #     self.info(u'查询结果不一致')
            #     save_dead_company(keyword)
        else:
            if self.use_proxy and self.lock_id != '0':
                self.proxy_config.release_lock_id(self.lock_id)
            self.info(u'查询无结果')
            # save_dead_company(keyword)
        if 'Registered_Info' in self.json_result:
            self.json_result['inputCompanyName'] = self.json_result['Registered_Info'][0]['Registered_Info:enterprisename']
        self.info(u'消息写入kafka')
        # self.kafka.send(json.dumps(self.json_result, ensure_ascii=False))
        print json.dumps(self.json_result, ensure_ascii=False)
        self.send_msg_to_kafka(json.dumps(self.json_result, ensure_ascii=False))
        # self.info(json.dumps(self.json_result, ensure_ascii=False))
        return res

if __name__ == '__main__':
    args_dict = get_args()
    # args_dict = {'companyName': u'浙江朗诗德健康饮水设备股份有限公司', 'accountId': '123', 'taskId': '456'}
    searcher = ZheJiangSearcher('GSCrawlerTest')
    # searcher.submit_search_request(u'浙江今朝电气有限公司')#浙江朗诗德健康饮水设备股份有限公司')
    searcher.submit_search_request(u'桐乡其乐针织制衣有限公司')#海宁市红狮电梯装饰有限公司') #农夫山泉股份有限公司）建德市香山天然水厂  浙江隆华钛业有限公司
    searcher.info(json.dumps(searcher.json_result, ensure_ascii=False))
