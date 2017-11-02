# coding=utf-8
# import PackageTool
import os
from bs4 import BeautifulSoup
import json
import re
from HeBeiConfig import *
import sys
import random
import subprocess
from geetest_broker.GeetestBroker import GeetestBrokerOffline
# from gs.Searcher import Searcher
from gs.SpiderMan import SpiderMan
from gs.Searcher import get_args
from gs.TimeUtils import *
import requests
from gs.USCC import check

# requests.packages.urllib3.disable_warnings()


class HeBei(SpiderMan, GeetestBrokerOffline):
    search_result_json = None
    pattern = re.compile("\s")
    input_company_name = None
    cur_mc = ''
    cur_code = ''
    flag = True
    json_result_data = []
    tagA = ''
    today = None
    # kafka = KafkaAPI("GSCrawlerTest")
    session_token = None
    cur_time = None
    verify_ip = None
    # save_tag_a = None
    load_func_dict = {}

    def __init__(self, dst_topic=None):
        """
        设置查询结果存放的kafka的topic
        :param dst_topic: 调用kafka程序的目标topic，topic分测试环境和正式环境
        :return:
        """
        super(HeBei, self).__init__(keep_session=True, dst_topic=dst_topic)
        self.headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Accept-Encoding': 'gzip, deflate',
                        'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'Connection': 'keep-alive',
                        'Host': 'he.gsxt.gov.cn',
                        'Referer': 'http://he.gsxt.gov.cn/notice/',
                        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:46.0) Gecko/20100101 Firefox/46.0'
                        }
        self.set_config()
        self.time = datetime.datetime.now().strftime('%Y%m%d')
        self.load_func_dict[u'动产抵押登记信息'] = self.load_dongchandiyadengji
        self.load_func_dict[u'动产抵押信息'] = self.load_dongchandiyadengji
        self.load_func_dict[u'股权出质登记信息'] = self.load_guquanchuzhidengji
        self.load_func_dict[u'行政处罚信息'] = self.load_xingzhengchufa
        self.load_func_dict[u'经营异常信息'] = self.load_jingyingyichang
        self.load_func_dict[u'严重违法信息'] = self.load_yanzhongweifa
        self.load_func_dict[u'严重违法失信信息'] = self.load_yanzhongweifa
        self.load_func_dict[u'抽查检查信息'] = self.load_chouchajiancha
        self.load_func_dict[u'基本信息'] = self.load_jiben
        self.load_func_dict[u'股东信息'] = self.load_gudong
        self.load_func_dict[u'发起人信息'] = self.load_gudong
        self.load_func_dict[u'变更信息'] = self.load_biangeng
        self.load_func_dict[u'主要人员信息'] = self.load_zhuyaorenyuan
        self.load_func_dict[u'分支机构信息'] = self.load_fenzhijigou
        self.load_func_dict[u'清算信息'] = self.load_qingsuan
        self.load_func_dict[u'参加经营的家庭成员姓名'] = self.load_jiatingchengyuan  # Modified by Jing
        self.load_func_dict[u'投资人信息'] = self.load_touziren  # Modified by Jing
        self.load_func_dict[u'合伙人信息'] = self.load_hehuoren  # Modified by Jing
        self.load_func_dict[u'成员名册'] = self.load_chengyuanmingce  # Modified by Jing
        self.load_func_dict[u'撤销信息'] = self.load_chexiao  # Modified by Jing
        self.load_func_dict[u'主管部门（出资人）信息'] = self.load_DICInfo  # Modified by Jing

    def set_config(self):
        """
        加载配置信息，注释掉的内容由统一调用程序配置
        :return:
        """
        self.province = u'河北省'

    def get_verify_ip(self):
        """
        确认请求源的ip
        :return:
        """
        url = 'http://www.hebscztxyxx.gov.cn/notice/security/verify_ip'
        r = self.post_request(url, verify=False)
        self.verify_ip = r.text

    def get_gt_challenge(self):
        """
        获取极验验证码的识别参数：gt和challenge
        :return:
        """
        url = 'http://he.gsxt.gov.cn/notice/pc-geetest/register?t=' + get_cur_ts_mil()
        r = self.get_request(url=url)
        soup = BeautifulSoup(r.text, 'html5lib')
        d = eval(soup.text)
        gt_code = d['gt']
        challenge = d['challenge']
        self.gt = gt_code
        self.challenge = challenge

    def get_session_token(self, t=0):
        """
        获取网站的认证session
        :param t: 尝试次数
        :return:
        """
        url2 = 'http://he.gsxt.gov.cn/notice/home'
        r = self.get_request(url=url2)
        bs = BeautifulSoup(r.text, 'html5lib')
        sp = bs.select('script')[0].text.strip()
        try:
            self.session_token = re.search(u'(?<=code:).*(?=,)', sp).group().strip().replace(' ', '').replace('"', '')
            # print 'session)token',self.session_token
            self.token = self.session_token
        except AttributeError as e:
            if t == 5:
                self.info(u'当前网站实在太累了了，休息' + time.ctime())
                raise e
            return self.get_session_token(t + 1)

    def get_tag_a_from_page(self, keyword):
        """
        输入内容判断
        :param keyword: 输入查询内容
        :param flags: 信用代码或公司名称
        :return:
        """
        self.expected_ip = ''
        self.keep_ip = True
        tag_a = self.get_tag_a_from_page0(keyword)
        self.keep_ip = False
        return tag_a

    def get_tag_a_from_page0(self, keyword):
        """
        搜索过程逻辑实现，加载验证码，锁定ip，获取网站通行证credit
        :param keyword: 查询的输入内容
        :return:
        """
        is_xydm = check(keyword)
        self.get_session_token()
        validate = self.get_geetest_validate()

        url_3 = "http://he.gsxt.gov.cn/notice/pc-geetest/validate"
        params_3 = {
            'geetest_challenge': self.challenge,
            'geetest_validate': validate,
            'geetest_seccode': '%s|jordan' % validate,
        }
        # print params_3
        self.headers['Referer'] = 'http://he.gsxt.gov.cn/notice/home'
        self.post_request(url_3, params=params_3)
        url_4 = "http://he.gsxt.gov.cn/notice/search/ent_info_list"
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
        soup = BeautifulSoup(r_4.text, 'html5lib')
        if u'Proxy authentication failed for client' in soup.text:
            self.info(u'代理出错')
            raise Exception
        results = soup.find_all(class_='tableContent')
        cnt = 0
        if len(results) > 0:
            for r in results:
                cnt += 1
                name = r.find('thead').text.strip()
                name = name.split('\n')[0].replace('(', u'（').replace(')', u'）').strip()
                if len(results) > 10:
                    code = r.find('tbody').find('th').find('em').text.strip()
                else:
                    try:
                        code = r.find('tbody').find('td').text.strip()
                    except:
                        code = r.find('tbody').find('th').find('em').text.strip()
                tagAs = r.get('onclick')
                tagA = re.search(u"(?<=[(']).*(?=[)'])", tagAs).group().replace(u"'", "")
                if is_xydm:
                    self.cur_mc = name
                    self.cur_code = code
                    self.tagA = tagA
                    return tagA
                else:
                    if name == keyword:
                        self.cur_mc = name
                        self.cur_code = code
                        self.tagA = tagA
                        return tagA
        self.info(u'查询无结果')
        return None

    def save_tag_a_to_db(self, tag_a):
        """
        将通过提交验证码获取到的tag_a存储到数据库中
        :param tag_a: 查询关键词
        :return:
        """
        # sql = "insert into GsSrc.dbo.tag_a values ('%s','%s',getdate(), '%s')" % (self.cur_mc, tag_a, self.province)
        # MSSQL.execute_update(sql)
        pass

    def parse_detail(self):
        """
        解析结果详情表内容
        :return:
        """
        page = self.tagA
        # print 'parse_page:', page
        r2 = self.get_request(url=page)
        resdetail = BeautifulSoup(r2.text, 'html5lib')
        lensoup = len(resdetail.find_all(class_='contentB'))
        resdetail = resdetail.find(class_='contentB')
        div_element_list = resdetail.find_all(class_='content1')  # (style="display: none;")
        for div_element in div_element_list:
            table_title = div_element.find(class_='titleTop').text.strip()
            table_body = div_element.find_next('table')
            if table_title == u'营业执照信息':
                self.load_jiben(table_body)
            elif u'股东及出资信息' in table_title:
                self.load_gudong(table_body)
            elif u'发起人及出资信息' in table_title:
                self.load_gudong(table_body)
            elif u'变更信息' in table_title:
                # print 'mi;im'
                self.load_biangeng(table_body)
            elif u'主要人员信息' in table_title:
                # self.info(u'主要人员')
                self.load_zhuyaorenyuan(div_element)
            elif u'成员名册' in table_title:
                # self.info(u'成员名册')
                self.load_zhuyaorenyuan(div_element)

            elif u'合伙人信息' in table_title:
                self.load_hehuoren(table_body)

            elif u'投资人信息' in table_title:
                self.load_touziren(table_body)

                # elif table_title == u'分支机构信息':
                #     self.load_fenzhijigou(table_body)
                # elif table_title == u'清算信息':
                #     self.load_qingsuan(table_body)
                # elif table_title == u'股权出质登记信息':
                #     self.load_guquanchuzhidengji(table_body)
                # elif table_title == u'动产抵押登记信息':
                #     self.load_dongchandiyadengji(table_body)
                # elif table_title == u'行政处罚信息':
                #     self.load_xingzhengchufa(table_body)
                # elif table_title == u'纳入经营异常名录信息':
                #     self.load_jingyingyichang(table_body)
                # elif table_title == u'严重违法失信企业名单（黑名单）信息':
                #     self.load_yanzhongweifa(table_body)
                # elif table_title == u'抽查检查结果信息':
                #     self.load_chouchajiancha(table_body)
                #             for table_element in table_element_list:
                #                 row_cnt=len(table_element.find_all("tr"))
                # #                 print 'row_cnt',row_cnt
                #                 table_desc = div_element.find("th").get_text().strip().split('\n')[0]
                #                 if table_desc == u'享受扶持信息':
                #                     continue
                #                 elif table_desc in self.load_func_dict:
                #                     if row_cnt > 3:
                #                         self.load_func_dict[table_desc](table_element)
                #                 else:
                #                     print table_desc
                #                     raise Exception("unknown table!")
                #         self.load_nianbao()
                #         print '*_*'*100
        page2 = self.tagA.replace('=01', '=02')
        # print 'parse_page:', page2
        r2 = self.get_request(url=page2)
        resdetail = BeautifulSoup(r2.text, 'html5lib')
        div_element_list = resdetail.find_all(class_='content1')  # (style="display: none;")
        for div_element in div_element_list:
            table_title = div_element.find(class_='titleTop').text.strip()
            table_body = div_element.find('table')
            # print 'pip2', table_title#, table_body.text
            if table_title == u'企业年报信息':
                # self.load_nianbao(table_body)
                pass
        # json_result = json.dumps(self.json_result, ensure_ascii=False)
        # print u'json_result结果', time.ctime(), json_result

    def load_jiben(self, table_element):
        """
        加载基本信息
        :param table_element: 基本信息表soup
        :return:
        """
        family = 'Registered_Info'
        table_id = '01'
        json_list = []
        values = {}

        tr_element_list = table_element.find_all("tr")
        for tr_element in tr_element_list:
            td_element_list = tr_element.find_all('td')
            for td in td_element_list:
                if td.text.strip():
                    td_list = td.text.replace(u'·', '').replace(u'?', '').strip().replace(u' ', '').split(u'：', 1)
                    col = td_list[0].strip()
                    val = td_list[1].strip().replace(u'***', u'')
                    col = jiben_column_dict[col]
                    values[col] = val

        values['rowkey'] = '%s_%s_%s_' % (self.cur_mc, table_id, self.cur_code)
        values[family + ':registrationno'] = self.cur_code
        values[family + ':enterprisename'] = self.cur_mc
        xydm = None
        zch = None
        if check(self.cur_code):
            xydm = self.cur_code
        else:
            zch = self.cur_code
        values[family + ':tyshxy_code'] = xydm
        values[family + ':zch'] = zch
        values[family + ':lastupdatetime'] = get_cur_time()
        values[family + ':province'] = u'河北省'
        json_list.append(values)
        self.json_result['Registered_Info'] = json_list
        # json_jiben = json.dumps(json_list, ensure_ascii=False)
        # print 'json_jiben', json_jiben

    def load_gudong(self, table_element):
        """
        加载股东信息
        :param table_element: 股东表内容soup
        :return:
        """
        family = 'Shareholder_Info'
        table_id = '04'

        tr_element_list = table_element.find_all(class_="page-item")
        th_element_list = table_element.find_all('th')
        jsonarray = []
        values = {}
        idx = 1
        for tr_element in tr_element_list:
            td_element_list = tr_element.find_all('td')
            col_nums = len(th_element_list)
            for i in range(col_nums):
                col_dec = th_element_list[i].get_text().strip().replace('\n', '')
                if col_dec == u'序号':
                    continue
                col = gudong_column_dict[col_dec]
                td = td_element_list[i]
                val = td.get_text().strip()
                # print '--gdval--', val
                if val == u'查看':
                    # print 'Q'*20
                    link = td.a.get('onclick')
                    tid = re.search(u"(?<=[(']).*(?=[)'])", link).group().replace(u"'", "")
                    # print 'tid', tid
                    link = 'http://www.hebscztxyxx.gov.cn/notice/notice/view_investor?uuid=' + tid
                    values[col] = link
                    self.get_gu_dong_detail(link, values)
                else:
                    values[col] = val
            values['%s:registrationno' % family] = self.cur_code
            values['%s:enterprisename' % family] = self.cur_mc
            values['%s:id' % family] = str(idx)
            values['rowkey'] = self.cur_mc + ('_%s_' % table_id) + self.cur_code + '_' + self.time + str(idx)
            jsonarray.append(values)
            values = {}
            idx += 1
        if jsonarray:
            self.json_result[family] = jsonarray
            json_gudong = json.dumps(jsonarray, ensure_ascii=False)
            # print 'json_gudong',json_gudong

    def get_gu_dong_detail(self, url, values):
        """
        查询股东详情
        """

        # print 'gudong_detail_url',url
        r = self.get_request(url=url, params={})
        # r.encoding = 'gbk'

        resdetail = r.text
        htmldetail = BeautifulSoup(resdetail, 'html5lib')
        # jsbody = htmldetail.find(class_='detail_content')
        # print '***a*', htmldetail
        # print 'jsbody', jsbody
        detail_content = htmldetail.find(class_='detail_content')
        detail_div_list = detail_content.find_all(class_='content2')  # 股东，认缴，实缴分为3个div

        rjmx_list = []  # 认缴明细列表
        sjmx_list = []  # 实缴明细列表
        rjmx_dict = {}  # 认缴明细字典
        sjmx_dict = {}  # 实缴明细字典

        if len(detail_div_list) <= 1:
            values[gudong_column_dict[u'认缴额（万元）']] = ''
            values[gudong_column_dict[u'实缴额（万元）']] = ''
            values[gudong_column_dict[u'认缴明细']] = rjmx_list
            values[gudong_column_dict[u'实缴明细']] = sjmx_list
        else:
            # 认缴模式
            if len(detail_div_list) == 3:
                t = 1
                div_ele = detail_div_list[t]
                div_title = div_ele.find('div').text.strip()
                div_table = div_ele.find('table')
                # print u'开始解析%s表' % div_title
                tr_ele_list = div_table.find_all('tr')
                th_list = tr_ele_list[0].find_all('th')
                if len(tr_ele_list) == 1:
                    for c in range(len(th_list)):
                        col = th_list[c].text.strip()
                        val = u''
                        values[gudong_column_dict[col]] = val

                elif len(tr_ele_list) == 2:
                    rje = 0
                    sje = 0
                    rje_val = 0
                    sje_val = 0
                    for tr in tr_ele_list[1:]:
                        td_list = tr.find_all('td')
                        if len(td_list) == 3:
                            for c in range(len(th_list)):
                                col = th_list[c].text.strip()
                                val = td_list[c].text.strip()
                                if c == 1 and col == u'认缴出资额（万元）':
                                    try:
                                        rje = float(val)
                                        # print 'rje', val
                                    except Exception as e:
                                        rje = ''
                                values[gudong_column_dict[col]] = val
                                rjmx_dict[col] = val
                            rje_val = rje_val + rje
                            # sje_val = sje_val+sje
                        else:
                            for c in range(len(th_list)):
                                col = th_list[c].text.strip()
                                val = ''
                                # print col,val
                                values[gudong_column_dict[col]] = val
                                # print 'cai',
                                rjmx_dict[col] = val
                        rjmx_list.append(rjmx_dict)
                        rjmx_dict = {}
                    # print '2','rjeval',rje_val#,'sjeval',sje_val
                    values[gudong_column_dict[u'认缴额（万元）']] = rje_val

                elif len(tr_ele_list) > 2:
                    self.info(u'股东详情认缴出现多层情况')
                    rje = 0
                    sje = 0
                    rje_val = 0
                    sje_val = 0
                    for tr in tr_ele_list[1:]:
                        td_list = tr.find_all('td')
                        if len(td_list) == 3:
                            for c in range(len(th_list)):
                                col = th_list[c].text.strip()
                                val = td_list[c].text.strip()
                                # print col,val
                                if c == 1 and col == u'认缴出资额（万元）':
                                    try:
                                        rje = rje + float(val)
                                        rje_val = rje_val + rje
                                        # print 'rje', rje
                                    except Exception as e:
                                        self.info(u'rje%s' % e)
                                        rje = rje + 0

                                values[gudong_column_dict[col]] = val
                                rjmx_dict[col] = val
                            rje_val = rje_val + rje

                        else:
                            for c in range(len(th_list)):
                                col = th_list[c].text.strip()
                                val = ''
                                # print col,val
                                values[gudong_column_dict[col]] = val
                                rjmx_dict[col] = val
                        rjmx_list.append(rjmx_dict)
                        rjmx_dict = {}
                    # print '3','rjeval',rje#,'sjeval',sje_val
                    values[gudong_column_dict[u'认缴额（万元）']] = rje
                values[gudong_column_dict[u'认缴明细']] = rjmx_list

                # 实缴模式
                t = 2
                div_ele = detail_div_list[t]
                div_title = div_ele.find('div').text.strip()
                div_table = div_ele.find('table')
                # print u'开始解析%s表' % div_title
                tr_ele_list = div_table.find_all('tr')

                th_list = tr_ele_list[0].find_all('th')
                if len(tr_ele_list) == 1:
                    for c in range(len(th_list)):
                        col = th_list[c].text.strip()
                        val = u''
                        values[gudong_column_dict[col]] = val

                elif len(tr_ele_list) == 2:
                    rje = 0
                    sje = 0
                    rje_val = 0
                    sje_val = 0
                    for tr in tr_ele_list[1:]:
                        td_list = tr.find_all('td')
                        if len(td_list) == 3:
                            for c in range(len(th_list)):
                                col = th_list[c].text.strip()
                                val = td_list[c].text.strip()

                                if c == 1 and col == u'实缴出资额（万元）':
                                    try:
                                        sje = float(val)
                                        # print 'sje', sje
                                    except Exception as e:
                                        sje = ''
                                # print col,val
                                values[gudong_column_dict[col]] = val
                                sjmx_dict[col] = val
                            # rje_val = rje_val+rje
                            try:
                                sje_val = sje_val + sje
                            except:
                                sje_val = ''
                                # print sje
                        else:
                            for c in range(len(th_list)):
                                col = th_list[c].text.strip()
                                val = ''
                                # print col,val
                                values[gudong_column_dict[col]] = val
                                sjmx_dict[col] = val
                        sjmx_list.append(sjmx_dict)
                        sjmx_dict = {}
                    # print '2','sjeval',sje_val
                    # values[gudong_column_dict[u'认缴额（万元）']] = rje_val
                    values[gudong_column_dict[u'实缴额（万元）']] = sje_val

                elif len(tr_ele_list) > 2:
                    self.info(u'股东详情实缴出现多层情况')
                    rje = 0
                    sje = 0
                    rje_val = 0
                    sje_val = 0
                    for tr in tr_ele_list[1:]:
                        td_list = tr.find_all('td')
                        if len(td_list) == 3:
                            for c in range(len(th_list)):
                                col = th_list[c].text.strip()
                                val = td_list[c].text.strip()

                                if c == 1 and col == u'实缴出资额（万元）':
                                    try:
                                        sje = sje + float(val)
                                        # print 'sje', sje
                                    except Exception as e:
                                        self.info(u'sje%s' % e)
                                        sje = sje + 0
                                values[gudong_column_dict[col]] = val
                                sjmx_dict[col] = val
                                # rje_val = rje_val+rje
                                # sje_val = sje_val+sje
                        else:
                            for c in range(len(th_list)):
                                col = th_list[c].text.strip()
                                val = ''
                                # print col,val
                                values[gudong_column_dict[col]] = val
                                sjmx_dict[col] = val
                        sjmx_list.append(sjmx_dict)
                        sjmx_dict = {}
                    # print '3','sjeval',sje
                    values[gudong_column_dict[u'实缴额（万元）']] = sje
                values[gudong_column_dict[u'实缴明细']] = sjmx_list

    def load_touziren(self, table_element):
        """
        加载投资人信息
        :param table_element: 投资人表soup内容
        :return:
        """
        tr_element_list = table_element.find_all(class_="page-item")
        th_element_list = table_element.find_all('th')[1:-1]
        jsonarray = []
        values = {}
        id = 1
        for tr_element in tr_element_list:
            td_element_list = tr_element.find_all('td')
            col_nums = len(th_element_list)
            for i in range(col_nums):
                col_dec = th_element_list[i].get_text().strip().replace('\n', '')
                col = touziren_column_dict[col_dec]
                td = td_element_list[i]
                val = td.get_text().strip()
                values[col] = val
            # print col,val
            values['Investor_Info:registrationno'] = self.cur_code
            values['Investor_Info:enterprisename'] = self.cur_mc
            values['Investor_Info:id'] = str(id)
            values['rowkey'] = self.cur_mc + '_02_' + self.cur_code + '_' + self.time + str(id)
            jsonarray.append(values)
            values = {}
            id += 1
        self.json_result['Investor_Info'] = jsonarray

    #         json_touziren=json.dumps(jsonarray,ensure_ascii=False)
    #         print 'json_touziren',json_touziren


    def load_hehuoren(self, table_element):
        """
        加载合伙人信息
        :param table_element: 合伙人表内容soup
        :return:
        """
        tr_element_list = table_element.find_all(class_="page-item")
        th_element_list = table_element.find_all('th')
        jsonarray = []
        values = {}
        id = 1
        for tr_element in tr_element_list:
            td_element_list = tr_element.find_all('td')
            col_nums = len(th_element_list)
            for i in range(1, col_nums):
                col_dec = th_element_list[i].get_text().strip().replace('\n', '')
                col = hehuoren_column_dict[col_dec]
                td = td_element_list[i]
                val = td.get_text().strip()
                values[col] = val
            # print col,val
            values['Shareholder_Info:registrationno'] = self.cur_code
            values['Shareholder_Info:enterprisename'] = self.cur_mc
            values['Shareholder_Info:id'] = str(id)
            values['rowkey'] = self.cur_mc + '_03_' + self.cur_code + '_' + self.time + str(id)
            jsonarray.append(values)
            values = {}
            id += 1
        self.json_result['Shareholder_Info'] = jsonarray

    #         json_hehuoren=json.dumps(jsonarray,ensure_ascii=False)
    #         print 'json_hehuoren',json_hehuoren

    def load_DICInfo(self, table_element):
        """
        加载控股人信息
        :param table_element:
        :return:
        """
        tr_element_list = table_element.find_all(class_="page-item")
        th_element_list = table_element.find_all('th')[1:-1]
        jsonarray = []
        values = {}
        id = 1
        for tr_element in tr_element_list:
            td_element_list = tr_element.find_all('td')
            col_nums = len(th_element_list)
            for i in range(col_nums):
                col_dec = th_element_list[i].get_text().strip().replace('\n', '')
                col = DICInfo_column_dict[col_dec]
                td = td_element_list[i]
                val = td.get_text().strip()
                values[col] = val
            # print col,val
            values['DIC_Info:registrationno'] = self.cur_code
            values['DIC_Info:enterprisename'] = self.cur_mc
            values['DIC_Info:id'] = str(id)
            jsonarray.append(values)
            values = {}
            id += 1
            # self.json_result['DIC_Info']=jsonarray
            #         json_DICInfo=json.dumps(jsonarray,ensure_ascii=False)
            #         print 'json_DICInfo',json_DICInfo

    def load_biangeng(self, table_element):
        """
        加载变更信息
        :param table_element: 变更表soup内容
        :return:
        """
        tr_element_list = table_element.find_all(class_="page-item")
        th_element_list = table_element.find_all('th')[1:]
        jsonarray = []
        values = {}
        id = 1
        for tr_element in tr_element_list:
            td_element_list = tr_element.find_all('td')[1:]
            col_nums = len(th_element_list)
            for i in range(col_nums):
                col_dec = th_element_list[i].text.strip().replace('\n', '')
                col = biangeng_column_dict[col_dec]
                td = td_element_list[i]
                val = td.get_text().strip()
                if val.endswith(u'收起更多'):
                    valmore = td.find(id='allWords').get_text().strip().replace('\n', '')
                    values[col] = valmore.replace(u'***', '')
                else:
                    values[col] = val
                    #                 print col,val
            values['Changed_Announcement:registrationno'] = self.cur_code
            values['Changed_Announcement:enterprisename'] = self.cur_mc
            values['Changed_Announcement:id'] = str(id)
            values['rowkey'] = self.cur_mc + '_05_' + self.cur_code + '_' + self.time + str(id)
            jsonarray.append(values)
            values = {}
            id += 1
        if jsonarray:
            self.json_result['Changed_Announcement'] = jsonarray
            #         json_biangeng=json.dumps(jsonarray,ensure_ascii=False)
            #         print 'json_biangeng',json_biangeng

    def load_chexiao(self, table_element):
        """
        加载撤销信息
        :param table_element:
        :return:
        """
        pass

    def load_zhuyaorenyuan(self, table_element):
        """
        加载主要人员信息
        :param table_element: 主要人员表soup内容
        :return:
        """
        # print 'zhuyaorenyuan', table_element

        family = 'KeyPerson_Info'
        table_id = '06'
        json_list = []
        values = {}
        # print table_element
        try:
            url = table_element.find(class_='titleTop').find('a').get('href')
        except Exception as e:
            # print 'zyry_url', e
            url = ''

        if url:
            # print 'zyry_url:', url
            r = self.get_request(url=url)
            soup = BeautifulSoup(r.text, 'html5lib')
            # print 'zhuyaosoup:', soup
            table_element = soup.find(class_='dlPiece')
        else:
            table_element = table_element.find_next('table')
        try:
            tr_num = len(table_element.find_all('ul'))
        except:
            tr_num = 0

        ul_list = table_element.find_all('ul')

        if tr_num > 0:
            cnt = 1
            for t in range(tr_num):
                pson = ul_list[t].find_all('li')
                if len(pson):
                    name = pson[0].text.strip()
                    posn = pson[1].text.strip()
                    # print '******', t, 'name:', name, 'position:', posn
                    values[zhuyaorenyuan_column_dict[u'姓名']] = name
                    values[zhuyaorenyuan_column_dict[u'职务']] = posn
                    values['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.cur_code, self.today, cnt)
                    values[family + ':registrationno'] = self.cur_code
                    values[family + ':enterprisename'] = self.cur_mc
                    values[family + ':id'] = str(cnt)
                    json_list.append(values)
                    values = {}
                    cnt += 1
            if json_list:
                # print 'zhuyaorenyuan_jsonlist:', json_list
                self.json_result[family] = json_list
                #         json_zhuyaorenyuan=json.dumps(jsonarray,ensure_ascii=False)
                #         print 'json_zhuyaorenyuan',json_zhuyaorenyuan

    def load_jiatingchengyuan(self, table_element):
        """
        加载家庭成员信息
        :param table_element: 成员表soup内容
        :return:
        """
        tr_element_list = table_element.find_all(class_="page-item")
        th_element_list = table_element.find_all('th')[1:-1]
        jsonarray = []
        values = {}
        id = 1
        for tr_element in tr_element_list:
            td_element_list = tr_element.find_all('td')
            for i in range(4):
                col_dec = th_element_list[i].text.strip().replace('\n', '')
                col = jiatingchengyuan_column_dict[col_dec]
                td = td_element_list[i]
                val = td.get_text().strip()
                values[col] = val
                #                 print th,val
                if len(values) == 2:
                    values['Family_Info:registrationno'] = self.cur_code
                    values['Family_Info:enterprisename'] = self.cur_mc
                    values['Family_Info:id'] = str(id)
                    values['rowkey'] = self.cur_mc + '_07_' + self.cur_code + '_' + self.time + str(id)
                    jsonarray.append(values)
                    values = {}
                    id += 1
        self.json_result['Family_Info'] = jsonarray

    #         json_jiatingchengyuan=json.dumps(jsonarray,ensure_ascii=False)
    #         print 'json_jiatingchengyuan',json_jiatingchengyuan

    def load_chengyuanmingce(self, table_element):
        """
        加载成员名册内容
        :param table_element: 成员名册表soup内容
        :return:
        """
        tr_element_list = table_element.find_all(class_="page-item")
        th_element_list = table_element.find_all('th')[1:-1]
        jsonarray = []
        values = {}
        for tr_element in tr_element_list:
            td_element_list = tr_element.find_all('td')
            for i in range(4):
                col_dec = th_element_list[i].text.strip().replace('\n', '')
                col = chengyuanmingce_column_dict[col_dec]
                td = td_element_list[i]
                val = td.get_text().strip()
                values[col] = val
                #                 print th,val
                if len(values) == 2:
                    values['Members_Info:registrationno'] = self.cur_code
                    values['Members_Info:enterprisename'] = self.cur_mc
                    values['Members_Info:id'] = str(id)
                    jsonarray.append(values)
                    values = {}
                    # self.json_result['Members_Info']=jsonarray
                    #         json_jiatingchengyuan=json.dumps(jsonarray,ensure_ascii=False)
                    #         print 'json_jiatingchengyuan',json_jiatingchengyuan

    def load_fenzhijigou(self, table_element):
        """
        分支机构内容
        :param table_element:
        :return:
        """
        # print 'fenzhijigou', table_element
        tr_element_list = table_element.find_all(class_="page-item")
        th_element_list = table_element.find_all('th')[1:-1]
        jsonarray = []
        values = {}
        id = 1
        for tr_element in tr_element_list:
            td_element_list = tr_element.find_all('td')
            col_nums = len(th_element_list)
            for i in range(col_nums):
                col_dec = th_element_list[i].text.strip().replace('\n', '')
                col = fenzhijigou_column_dict[col_dec]
                td = td_element_list[i]
                val = td.get_text().strip()
                values[col] = val
            # print col,val
            values['Branches:registrationno'] = self.cur_code
            values['Branches:enterprisename'] = self.cur_mc
            values['Branches:id'] = str(id)
            values['rowkey'] = self.cur_mc + '_08_' + self.cur_code + '_' + self.time + str(id)
            jsonarray.append(values)
            values = {}
            id += 1
        if jsonarray:
            self.json_result['Branches'] = jsonarray
            #         json_fenzhijigou=json.dumps(jsonarray,ensure_ascii=False)
            #         print 'json_fenzhijigou',json_fenzhijigou

    # 加载清算信息
    def load_qingsuan(self, table_element):
        """
        清算信息内容
        :param table_element: 清算信息表soup内容
        :return:
        """
        family = 'liquidation_Information'
        table_id = '09'

        # print 'qingsuan', table_element
        tr_element_list = table_element.find_all('tr')[1:]
        jsonarray = []
        values = {}
        try:
            for tr_element in tr_element_list:
                col = tr_element.find('th').text().strip()
                td_list = tr_element.find_all('td')
                td_va = []
                for td in td_list:
                    va = td.get_text().strip()
                    td_va.append(va)
                val = ','.join(td_va)
                values[qingsuan_column_dict[col]] = val
            if values.values()[0] or values.values()[1]:  # 清算无内容时成立
                values['liquidation_Information:registrationno'] = self.cur_code
                values['liquidation_Information:enterprisename'] = self.cur_mc
                values['rowkey'] = self.cur_mc + '_09_' + self.cur_code + '_'
                jsonarray.append(values)
                values = {}
                # print jsonarray
                self.json_result['liquidation_Information'] = jsonarray
        except:
            self.info(u'清算暂无相关数据')

    def load_dongchandiyadengji(self, table_element):
        """
        动产抵押登记信息
        :param table_element: 动产抵押表soup内容
        :return:
        """
        # print 'dongchandiya', table_element
        tr_element_list = table_element.find_all(class_="page-item")
        th_element_list = table_element.find_all('th')
        jsonarray = []
        values = {}
        id = 1
        for tr_element in tr_element_list:
            td_element_list = tr_element.find_all('td')
            col_nums = len(th_element_list)
            for i in range(col_nums):
                col_dec = th_element_list[i].text.strip().replace('\n', '')
                col = dongchandiyadengji_column_dict[col_dec]
                td = td_element_list[i]
                val = td.get_text().strip()
                if val == u'查看':
                    link = td.a.get('onclick')
                    tid = re.search(u"(?<=[(']).*(?=[)'])", link).group().replace(u"'", "")
                    # print 'tid', tid
                    link = 'http://www.hebscztxyxx.gov.cn/notice/notice/view_mortage?uuid=' + tid
                    # print 'dcdy', link
                    values[col] = link
                else:
                    values[col] = val
            values['Chattel_Mortgage:registrationno'] = self.cur_code
            values['Chattel_Mortgage:enterprisename'] = self.cur_mc
            values['Chattel_Mortgage:id'] = str(id)
            values['rowkey'] = self.cur_mc + '_11_' + self.cur_code + '_' + self.time + str(id)
            jsonarray.append(values)
            values = {}
            id += 1
        if jsonarray:
            self.json_result['Chattel_Mortgage'] = jsonarray
            json_dongchandiyadengji = json.dumps(jsonarray, ensure_ascii=False)
            # print 'json_dongchandiyadengji',json_dongchandiyadengji

    def load_guquanchuzhidengji(self, table_element):
        """
        股权出质登记信息
        :param table_element: 股权出质内容soup
        :return:
        """
        # print 'guquanchuzhi', table_element
        tr_element_list = table_element.find_all(class_="page-item")
        th_element_list = table_element.find_all('th')
        jsonarray = []
        values = {}
        id = 1
        for tr_element in tr_element_list:
            td_element_list = tr_element.find_all('td')
            col_nums = len(th_element_list)
            for i in range(col_nums):
                col_dec = th_element_list[i].text.strip().replace('\n', '')
                previous = th_element_list[(i - 1)].text.strip().replace('\n', '')
                if col_dec == u'证照/证件号码' and previous == u'出质人':
                    col = 'Equity_Pledge:equitypledge_pledgorid'
                elif col_dec == u'证照/证件号码' and previous == u'质权人':
                    col = 'Equity_Pledge:equitypledge_pawneeid'
                else:
                    col = guquanchuzhidengji_column_dict[col_dec]
                td = td_element_list[i]
                val = td.get_text().strip()
                if val == u'查看':
                    link = td.a.get('onclick')
                    tid = re.search(u"(?<=[(']).*(?=[)'])", link).group().replace(u"'", "")
                    # print 'tid', tid
                    link = 'http://www.hebscztxyxx.gov.cn/notice/notice/view_pledge?uuid=' + tid
                    # print 'gqcz', link
                    values[col] = link
                else:
                    values[col] = val
            values['Equity_Pledge:registrationno'] = self.cur_code
            values['Equity_Pledge:enterprisename'] = self.cur_mc
            values['Equity_Pledge:id'] = str(id)
            values['rowkey'] = self.cur_mc + '_12_' + self.cur_code + '_' + self.time + str(id)
            jsonarray.append(values)
            values = {}
            id += 1
        if jsonarray:
            self.json_result['Equity_Pledge'] = jsonarray
            json_guquanchuzhidengji = json.dumps(jsonarray, ensure_ascii=False)
            # print 'json_guquanchuzhidengji',json_guquanchuzhidengji

    def load_xingzhengchufa(self, table_element):
        """
        行政处罚内容
        :param table_element: 行政处罚soup内容
        :return:
        """
        # print 'xingzhengchufa', table_element
        tr_element_list = table_element.find_all(class_="page-item")
        th_element_list = table_element.find_all('th')
        jsonarray = []
        values = {}
        id = 1
        switchs = len(th_element_list)
        # print 'xzcf_switchs', switchs
        for tr_element in tr_element_list:
            td_element_list = tr_element.find_all('td')
            col_nums = len(th_element_list)
            for i in range(col_nums):
                col_dec = th_element_list[i].text.strip().replace('\n', '')
                col = xingzhengchufa_column_dict[col_dec]
                td = td_element_list[i]
                val = td.get_text().strip()
                if val == u'查看':
                    link = td.a.get('onclick')
                    tid = re.search(u"(?<=[(']).*(?=[)'])", link).group().replace(u"'", "")
                    # print 'tid', tid
                    link = 'http://www.hebscztxyxx.gov.cn/notice/notice/view_punish?uuid=' + tid
                    values[col] = link
                else:
                    values[col] = val
            values['Administrative_Penalty:registrationno'] = self.cur_code
            values['Administrative_Penalty:enterprisename'] = self.cur_mc
            values['Administrative_Penalty:id'] = str(id)
            values['rowkey'] = self.cur_mc + '_13_' + self.cur_code + '_' + self.time + str(id)
            jsonarray.append(values)
            values = {}
            id += 1
        if jsonarray:
            self.json_result['Administrative_Penalty'] = jsonarray
            #         json_xingzhengchufa=json.dumps(jsonarray,ensure_ascii=False)
            #         print 'json_xingzhengchufa',json_xingzhengchufa

    def load_jingyingyichang(self, table_element):
        """
        经营异常内容
        :param table_element: 经营异常soup
        :return:
        """
        # print 'jingyingyichang', table_element
        tr_element_list = table_element.find_all(class_="page-item")
        th_element_list = table_element.find_all('th')
        jsonarray = []
        values = {}
        id = 1
        for tr_element in tr_element_list:
            td_element_list = tr_element.find_all('td')
            col_nums = len(th_element_list)
            for i in range(col_nums):
                col_dec = th_element_list[i].text.strip().replace('\n', '')
                col = jingyingyichang_column_dict[col_dec]
                td = td_element_list[i]
                val = td.get_text().strip()
                values[col] = val
            # print col,val
            values['Business_Abnormal:registrationno'] = self.cur_code
            values['Business_Abnormal:enterprisename'] = self.cur_mc
            values['Business_Abnormal:id'] = str(id)
            values['rowkey'] = self.cur_mc + '_14_' + self.cur_code + '_' + self.time + str(id)
            jsonarray.append(values)
            values = {}
            id += 1
        if jsonarray:
            self.json_result['Business_Abnormal'] = jsonarray
            #         json_jingyingyichang=json.dumps(jsonarray,ensure_ascii=False)
            #         print 'json_jingyingyichang',json_jingyingyichang

    def load_yanzhongweifa(self, table_element):
        """
        严重违法内容
        :param table_element:
        :return:
        """
        # print 'yanzhongweifa', table_element
        tr_element_list = table_element.find_all(class_="page-item")
        th_element_list = table_element.find_all('th')
        jsonarray = []
        values = {}
        id = 1
        for tr_element in tr_element_list:
            td_element_list = tr_element.find_all('td')
            col_nums = len(th_element_list)
            for i in range(col_nums):
                col_dec = th_element_list[i].text.strip().replace('\n', '')
                col = yanzhongweifa_column_dict[col_dec]
                td = td_element_list[i]
                val = td.get_text().strip()
                values[col] = val
            # print col,val
            values['Serious_Violations:registrationno'] = self.cur_code
            values['Serious_Violations:enterprisename'] = self.cur_mc
            values['Serious_Violations:id'] = str(id)
            values['rowkey'] = self.cur_mc + '_15_' + self.cur_code + '_' + self.time + str(id)
            jsonarray.append(values)
            values = {}
            id += 1
        if jsonarray:
            self.json_result['Serious_Violations'] = jsonarray
            #         json_yanzhongweifa=json.dumps(jsonarray,ensure_ascii=False)
            #         print 'json_yanzhongweifa',json_yanzhongweifa

    def load_chouchajiancha(self, table_element):
        """
        抽查检查内容
        :param table_element: 抽查检查内容soup
        :return:
        """
        # print 'chouchajiancha',table_element
        tr_element_list = table_element.find_all(class_="page-item")
        th_element_list = table_element.find_all('th')
        jsonarray = []
        values = {}
        id = 1
        for tr_element in tr_element_list:
            td_element_list = tr_element.find_all('td')
            col_nums = len(th_element_list)
            for i in range(col_nums):
                col_dec = th_element_list[i].text.strip().replace('\n', '')
                col = chouchajiancha_column_dict[col_dec]
                td = td_element_list[i]
                val = td.get_text().strip()
                values[col] = val
            # print col,val
            values['Spot_Check:registrationno'] = self.cur_code
            values['Spot_Check:enterprisename'] = self.cur_mc
            values['Spot_Check:id'] = str(id)
            values['rowkey'] = self.cur_mc + '_16_' + self.cur_code + '_' + self.time + str(id)
            jsonarray.append(values)
            values = {}
            id += 1
        if jsonarray:
            self.json_result['Spot_Check'] = jsonarray
            #         json_chouchajiancha=json.dumps(jsonarray,ensure_ascii=False)
            #         print 'json_chouchajiancha',json_chouchajiancha

    # def get_lock_id(self):
    #     """
    #     请求过程加载动态代理ip锁定程序，1为锁定ip
    #     :param self:
    #     :return:
    #     """
    #     if self.use_proxy:
    #         self.release_lock_id()
    #         self.lock_id = self.proxy_config.get_lock_id()
    #         self.release_id = self.lock_id
    #
    # def release_lock_id(self):
    #     """
    #     请求过程锁定ip释放程序，0为释放ip
    #     :param self:
    #     :return:
    #     """
    #     if self.use_proxy and self.lock_id != '0':
    #         self.proxy_config.release_lock_id(self.lock_id)
    #         self.lock_id = '0'

    def submit_search_request(self, keyword, account_id='null', task_id='null'):
        """
        提交查询请求
        :param keyword: 查询关键词(公司名称或者注册号)
        :param account_id: 在线更新,kafka所需参数
        :param task_id: 在线更新kafka所需参数
        :return:
        """
        keyword = self.process_mc(keyword)  # 公司名称括号统一转成全角
        self.input_company_name = keyword
        self.session = requests.session()  # 初始化session
        # self.add_proxy(self.app_key)  # 为session添加代理
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
        if not tag_a:
            tag_a = self.get_tag_a_from_page(keyword)
        if tag_a:
            if self.save_tag_a:  # 查询结果与所输入公司名称一致时,将其写入数据库
                self.save_tag_a_to_db(tag_a)
            self.info(u'解析详情信息')
            self.parse_detail()
            res = 1
        else:
            self.info(u'查询无结果')
        self.info(u'消息写入kafka')
        if 'Registered_Info' in self.json_result:
            self.json_result['inputCompanyName'] = self.json_result['Registered_Info'][0]['Registered_Info:enterprisename']
        self.send_msg_to_kafka(json.dumps(self.json_result, ensure_ascii=False))
        return res

    def post_request(self, url, **kwargs):
        for t in range(self.max_try_times):
            proxy_config = self.get_proxy()
            kwargs['proxies'] = {'http': 'http://%(user)d:%(pwd)s@%(proxy)s' % proxy_config,
                                 'https': 'https://%(user)d:%(pwd)s@%(proxy)s' % proxy_config}
            kwargs['timeout'] = proxy_config['timeout']
            kwargs.setdefault('headers', {})
            kwargs['headers']['Connection'] = 'close'
            kwargs['headers']['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:45.0) Gecko/20100101 Firefox/45.0'
            try:
                if self.session:
                    r = self.session.post(url=url, **kwargs)
                else:
                    r = requests.post(url=url, **kwargs)
                if r.text == '':
                    raise requests.exceptions.RequestException()
                else:
                    return r
            except requests.exceptions.RequestException, e:
                if t == self.max_try_times - 1:
                    raise e

    def get_request(self, url, **kwargs):
        for t in range(self.max_try_times):
            proxy_config = self.get_proxy()
            kwargs['proxies'] = {'http': 'http://%(user)d:%(pwd)s@%(proxy)s' % proxy_config,
                                 'https': 'https://%(user)d:%(pwd)s@%(proxy)s' % proxy_config}
            kwargs['timeout'] = proxy_config['timeout']
            kwargs.setdefault('headers', {})
            kwargs['headers']['Connection'] = 'close'
            kwargs['headers']['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:45.0) Gecko/20100101 Firefox/45.0'
            try:
                if self.session:
                    r = self.session.get(url=url, **kwargs)
                else:
                    r = requests.get(url=url, **kwargs)
                if r.text == '':
                    raise requests.exceptions.RequestException()
                else:
                    return r
            except requests.exceptions.RequestException, e:
                if t == self.max_try_times - 1:
                    raise e

if __name__ == '__main__':
    args_dict = get_args()
    searcher = HeBei('GSCrawlerTest')
    searcher.get_session_token()
    searcher.submit_search_request(u'河间市东方汽车电线电缆厂')  # 天顺橡胶化工有限公司')
    # searcher.submit_search_request(u'911302007356029939')#911302007356029939')#奇瑞')#清河县飘丝纺羊绒制品有限公司')
    # 上海益中亘泰物业管理有限公司廊坊分公司') #河北泰华实业集团有限公司')
    # searcher.submit_search_request(keyword=args_dict['companyName'], account_id=args_dict['accountId'], task_id=args_dict['taskId'])
    print json.dumps(searcher.json_result, ensure_ascii=False)

    # test part
    # if __name__ == '__main__':
    #     searcher = HeBei('GSCrawlerTest')
    #     f = open('E:\\hb30.txt', 'r').readlines()
    #     # print f, len(f), f[0].strip().decode('gbk').encode('utf8')
    #     cnt = 1
    #     for name in f:
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