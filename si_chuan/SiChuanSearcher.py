# coding=utf-8
# import PackageTool
import requests
import os
from bs4 import BeautifulSoup
import json
import re
from si_chuan.Tables_dict import *
import sys
import random
import subprocess
from geetest_broker.GeetestBroker import GeetestBrokerOffline
from gs.Searcher import Searcher
from gs.Searcher import get_args
from gs.TimeUtils import *
from gs import CompareStatus
import requests

requests.packages.urllib3.disable_warnings()


class SiChuan(Searcher, GeetestBrokerOffline):
    search_result_json = None
    pattern = re.compile("\s")
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
        super(SiChuan, self).__init__(use_proxy=True, dst_topic=dst_topic)
        self.headers = {'Accept': 'application/json, text/javascript, */*; q=0.01',
                        'Accept-Encoding': 'gzip, deflate',
                        'Accept-Language': 'zh-CN,zh;q=0.8',
                        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                        'Host': 'sc.gsxt.gov.cn',
                        'AlexaToolbar-ALX_NS_PH': 'AlexaToolbar/alx-4.0.1',
                        'Referer': 'http://sc.gsxt.gov.cn/notice/home',
                        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'
                        }
        # self.cur_time = '%d' % (time.time() * 1000)
        # self.get_session_token()
        # self.get_verify_ip()
        # self.json_result = {}
        self.set_config()
        # self.log_name = self.topic + "_" + str(uuid.uuid1())
        time = datetime.datetime.now()
        self.time = time.strftime('%Y%m%d')
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
        # self.plugin_path = os.path.join(sys.path[0], '../he_bei/ocr/type34.bat')
        # # self.group = 'Crawler'  # 正式
        # # self.kafka = KafkaAPI("GSCrawlerResult")  # 正式
        # self.group = 'CrawlerTest'  # 测试
        # self.kafka = KafkaAPI("GSCrawlerTest")  # 测试
        # self.topic = 'GsSrc13'
        self.province = u'河北省'
        # self.kafka.init_producer()

    def get_verify_ip(self):
        url = 'http://sc.gsxt.gov.cn/notice/security/verify_ip'
        r = self.post_request(url, verify=False)
        self.verify_ip = r.text
        # pass

    def get_verify_keyword(self, keyword):
        url = "http://sc.gsxt.gov.cn/notice/security/verify_keyword"
        params = {'keyword': keyword}
        r = self.post_request(url, params, verify=False)
        # print '***', r.text
        return r.text
        # pass

    # def get_challenge_code(self):
    def get_gt_challenge(self):
        # url = 'http://www.hebscztxyxx.gov.cn/notice/pc-geetest/register?t='+get_cur_ts_mil()
        url = 'http://sc.gsxt.gov.cn/notice/pc-geetest/register?t=' + get_cur_ts_mil()
        r = self.get_request(url=url)
        # print r.content
        soup = BeautifulSoup(r.text, 'html5lib')
        # print soup.text
        d = eval(soup.text)
        gtCode = d['gt']
        challenge = d['challenge']
        self.gt = gtCode
        self.challenge = challenge
        # print 'gtCode:', gtCode, 'challengeCode:', challenge

    def get_validate_image_save_path(self):
        return os.path.join(sys.path[0], '../temp/' + str(random.random())[2:] + '.png')

    def get_validate_file_path(self):
        return os.path.join(sys.path[0], '../temp/' + str(random.random())[2:] + '.txt')

    def get_tag_a_from_db(self, keyword):
        # 无需tagA查询
        return []

    def recognize_yzm(self, validate_path, validate_result_path):
        cmd = self.plugin_path + " " + validate_path + " " + validate_result_path
        # print cmd
        os.path.join(cmd)
        p = subprocess.Popen(cmd.encode('gbk', 'ignore'), stdout=subprocess.PIPE)
        p.communicate()
        fo = open(validate_result_path, 'r')
        answer = fo.readline().strip()
        fo.close()
        # print 'answer: '+answer.decode('gbk', 'ignore')
        os.remove(validate_path)
        os.remove(validate_result_path)
        return answer.decode('gbk', 'ignore')

    def get_yzm(self):
        image_url = 'http://sc.gsxt.gov.cn/notice/captcha?preset=&ra='
        r = self.get_request(url=image_url)
        # print r.headers
        yzm_path = self.get_validate_image_save_path()
        with open(yzm_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
                    f.flush()
            f.close()
        yzm_file_path = self.get_validate_file_path()
        yzm = self.recognize_yzm(yzm_path, yzm_file_path)
        return yzm

    def get_session_token(self, t=0):
        # url2 = 'http://www.hebscztxyxx.gov.cn/notice/'  # yzm_page

        url2 = 'http://sc.gsxt.gov.cn/notice/'
        # url2 = 'http://www.hebscztxyxx.gov.cn/notice/search/popup_captcha?adfwkey=plp16'
        r = self.get_request(url=url2)
        bs = BeautifulSoup(r.text, 'html5lib')
        sp = bs.select('script')[0].text.strip()
        # print '*******************',sp
        try:
            self.session_token = re.search(u'(?<=code:).*(?=,)', sp).group().strip().replace(' ', '').replace('"', '')
            # print 'session)token',self.session_token
            self.token = self.session_token
        except AttributeError as e:
            if t == 5:
                self.info(u'当前网站实在太累了了，休息' + time.ctime())
                raise e
            return self.get_session_token(t + 1)

    def get_the_mc_or_code(self, keyword):
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

    def get_tag_a_from_page(self, keyword, flags=0):
        return self.get_tag_a_from_page0(keyword)

    def get_tag_a_from_page0(self, keyword):
        self.flag = self.get_the_mc_or_code(keyword)
        for i in range(6):#成功获取validate，循环重置session
            self.get_lock_id()
            self.get_session_token()
            validate = self.get_geetest_validate()
            # print validate
            if len(validate) > 4:
                break
            else:
                self.release_lock_id()
                self.reset_session()
                time.sleep(3)
                continue
        self.release_lock_id()

        url_3 = "http://sc.gsxt.gov.cn/notice/pc-geetest/validate"
        params_3 = {
            'geetest_challenge': self.challenge,
            'geetest_validate': validate,
            'geetest_seccode': '%s|jordan' % validate,
        }
        # print params_3
        self.headers['Referer'] = 'http://sc.gsxt.gov.cn/notice/home'
        r_3 = self.post_request(url_3, params=params_3,)
        # print r_3.text

        url_4 = "http://sc.gsxt.gov.cn/notice/search/ent_info_list"
        params_4 = {
            'condition.searchType': '1',
            'captcha': '',
            'geetest_challenge': self.challenge,
            'geetest_validate': validate,
            'geetest_seccode': '%s|jordan' % validate,
            'session.token': self.token,
            'condition.keyword': keyword,
        }
        # print params_4
        r_4 = self.post_request(url=url_4, params=params_4)
        # print r_4.text, r_4.headers
        # self.release_lock_id()
        soup = BeautifulSoup(r_4.text, 'html5lib')
        # print 'soup:', soup
        if u'Proxy authentication failed for client' in soup.text:
            self.info(u'代理出错')
            raise Exception

        results = soup.find_all(class_='tableContent')
        # print 'results_lens', len(results)

        self.xydm_if = ''
        self.zch_if = ''

        cnt =0
        company_list = []
        company_code = []
        company_tags = []
        sort_index=[]
        for r in results:
            name_parts = r.find_all('span')
            name = r.find('thead').text.strip()
            name = name.split('\n')[0].replace('(', u'（').replace(')', u'）').strip()
            if name != keyword:
                continue
            else:
                if len(results) > 0:
                    nn = ''
                    for r in results:
                        cnt += 1
                        name_parts = r.find_all('span')
                        # for p in name_parts:
                        # 	print '**',p.text
                        name = r.find('thead').text.strip()
                        # print '--',name.split('\n')[0]
                        name = name.split('\n')[0].replace('(', u'（').replace(')', u'）').strip()
                        if name==keyword:
                            company_status=r.find('i').text.strip()
                            try:
                                code = r.find('tbody').find('th').find('em').text.strip()
                            except:
                                code = r.find('tbody').find('td').text.strip()
                            tagAs = r.get('onclick')
                            # print tagAs
                            tagA = re.search(u"(?<=[(']).*(?=[)'])", tagAs).group().replace(u"'", "")
                            # print cnt, name, code, tagA
                            sort_index.append(company_status)
                            company_list.append(name)
                            company_code.append(code)
                            company_tags.append(tagA)
                            continue
                    if len(sort_index)>1:#判断出现同名情况
                        for company_status_i in sort_index:
                            if CompareStatus.status_dict[company_status_i]==1:
                                index_n=sort_index.index(company_status_i)
                    else:
                        index_n=0
                else:
                    # print '**'*100, u'查询无结果'
                    self.info(u'查询无结果')
                    return None

                if len(company_list) > 1:
                    for name in company_list[1:]:
                        pass
                        # self.save_company_name_to_db(name)

                self.cur_mc = company_list[index_n].replace('(', u'（').replace(')', u'）')
                self.cur_code = company_code[index_n]
                self.cur_zch = company_code[index_n]
                self.tagA = company_tags[index_n]
                if len(self.cur_code) == 18:
                    self.xydm_if = self.cur_code
                else:
                    self.zch_if = self.cur_code
                # print 'name:', company_list[0], 'code:', company_code[0], 'tagA:', company_tags[0]
                # r = requests.get(company_tags[0])
                # print r.text,r.headers

                return company_tags[index_n]
            return None

    def get_search_args(self, tag_a, keyword):
        if tag_a:
            # print 'tag_a', tag_a, 'self.mc:', self.cur_mc
            self.tagA = tag_a
            if self.flag:
                if self.cur_mc == keyword:
                    return 1
                else:
                    return 0
            else:
                self.info(self.cur_mc)
                return 1
        else:
            return 0

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
        page = self.tagA
        # print 'parse_page:', page
        r2 = self.get_request(url=page)
        resdetail = BeautifulSoup(r2.text, 'html5lib')
        lensoup = len(resdetail.find_all(class_='contentB'))
        # print 'self.save_tag_a', lensoup, resdetail.find(class_='contentB')
        # print '*'*1000
        resdetail = resdetail.find(class_='contentB')
        div_element_list = resdetail.find_all(class_='content1')  # (style="display: none;")
        # print 'dvns', len(div_element_list)
        for div_element in div_element_list:
            # print 'ff'*100
            table_title = div_element.find(class_='titleTop').text.strip()
            table_body = div_element.find_next('table')
            # print '*pip*', table_title#, table_body
            if table_title == u'营业执照信息':
                self.load_jiben(table_body)
            elif u'股东及出资信息' in table_title:
                # self.info(u'股东')
                self.load_gudong(table_body)
            elif u'主管部门（出资人）信息' in table_title:
                # self.info(u'股东')
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
        # print 'self.save_tag_a', resdetail
        # print self.save_tag_a
        # if not self.save_tag_a:
        #     li_list = resdetail.select('html body.layout div.main div.notice ul li')
        #     mc = li_list[0].text
        #     code = li_list[1].text
        #     title_bar = resdetail.find(class_='title-bar clearfix')
        #     # if not title_bar:
        #     #     print '************************************'
        #     #     print r2.text
        #     # mc=title_bar.find('li')
        #     # code=mc.find_next('li')
        #     self.cur_mc=mc.strip()
        #     self.cur_code=code.strip()[13:]
        # print '**', self.cur_mc,self.cur_code
        div_element_list = resdetail.find_all(class_='content1')  # (style="display: none;")
        for div_element in div_element_list:
            table_title = div_element.find(class_='titleTop').text.strip()
            table_body = div_element.find('table')
            # print 'pip2', table_title#, table_body.text
            if table_title == u'企业年报信息':
                # self.load_nianbao(table_body)
                pass

        json_result = json.dumps(self.json_result, ensure_ascii=False)
        # print u'json_result结果', time.ctime(), json_result

    def load_jiben(self, table_element):
        family = 'Registered_Info'
        table_id = '01'
        json_list = []
        values = {}

        tr_element_list = table_element.find_all("tr")
        for tr_element in tr_element_list:
            # th_element_list = tr_element.find_all('th')
            td_element_list = tr_element.find_all('td')
            for td in td_element_list:
                if td.text.strip():
                    td_list = td.text.replace(u'·', '').replace(u'?', '').strip().replace(u' ', '').split(u'：', 1)
                    col = td_list[0].strip()
                    val = td_list[1].strip().replace(u'***', u'')
                    # print col, val
                    col = jiben_column_dict[col]
                    values[col] = val

        values['rowkey'] = '%s_%s_%s_' % (self.cur_mc, table_id, self.cur_zch)
        values[family + ':registrationno'] = self.cur_zch
        values[family + ':enterprisename'] = self.cur_mc
        values[family + ':tyshxy_code'] = self.xydm_if
        values[family + ':zch'] = self.zch_if
        values[family + ':lastupdatetime'] = get_cur_time()
        values[family + ':province'] = u'四川省'
        json_list.append(values)
        self.json_result['Registered_Info'] = json_list
        json_jiben = json.dumps(json_list, ensure_ascii=False)
        # print 'json_jiben', json_jiben

    def load_gudong(self, table_element):
        family = 'Shareholder_Info'
        table_id = '04'

        tr_element_list = table_element.find_all(class_="page-item")
        th_element_list = table_element.find_all('th')
        jsonarray = []
        values = {}
        id = 1
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
                    link = 'http://sc.gsxt.gov.cn/notice/notice/view_investor?uuid=' + tid
                    values[col] = link
                    self.get_gu_dong_detail(link, values)
                else:
                    values[col] = val
            values['Shareholder_Info:registrationno'] = self.cur_code
            values['Shareholder_Info:enterprisename'] = self.cur_mc
            values['Shareholder_Info:id'] = str(id)
            values['rowkey'] = self.cur_mc + '_04_' + self.cur_code + '_' + self.time + str(id)
            jsonarray.append(values)
            values = {}
            id += 1
        if jsonarray:
            self.json_result['Shareholder_Info'] = jsonarray
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
        # detail_content = htmldetail.find_all(class_='detail_content')
        # print detail_content
        detail_div_list = htmldetail.find_all(class_='content2')  # 股东，认缴，实缴分为3个div

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

    def load_touziren(self, table_element):
        tr_element_list = table_element.find_all(class_="page-item")
        th_element_list = table_element.find_all('th')
        jsonarray = []
        values = {}
        id = 1
        for tr_element in tr_element_list:
            td_element_list = tr_element.find_all('td')
            col_nums = len(th_element_list)
            for i in range(0, col_nums):
                col_dec = th_element_list[i].get_text().strip().replace('\n', '')
                col = touziren_column_dict[col_dec]
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

    def load_DICInfo(self, table_element):
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
        pass

    def load_zhuyaorenyuan(self, table_element):
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
                #         json_zhuyaorenyuan=json.dumps(jsonarray,ensure_ascii=False)
                #         print 'json_zhuyaorenyuan',json_zhuyaorenyuan

    def load_jiatingchengyuan(self, table_element):
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

    def load_nianbao(self, table_body):
        # print 'nianbao:', table_body
        family = 'annual_report'
        table_id = '39'

        json_list = []
        values = {}
        tr_ele_list = table_body.find_all('tr')
        th_ele_list = table_body.find_all('th')

        idn = 1
        year_list = []  # 存年份
        year_link = []  # 存年份链接
        for tr_ele in tr_ele_list[1:-1]:  # 去掉第一行th（标题行），去掉最后一行（页码行）
            td_list = tr_ele.find_all('td')
            for i in range(len(th_ele_list)):
                col = th_ele_list[i].text.strip()
                val = td_list[i].text.strip()
                if col == u'报送年度':
                    y = val[:4]
                    year_list.append(y)
                if val == u'查看':
                    link = td_list[i].a.get('href')
                    values[qiyenianbao_column_dict[col]] = link
                    year_link.append(link)
                else:
                    values[qiyenianbao_column_dict[col]] = val
            values['rowkey'] = '%s_%s_%s_%d' % (self.cur_mc, y, table_id, idn)
            values[family + ':registrationno'] = self.cur_zch
            values[family + ':enterprisename'] = self.cur_mc
            values[family + ':id'] = str(idn)
            json_list.append(values)
            values = {}
            idn += 1
        if json_list:
            # print 'nb', json_list
            self.json_result[family] = json_list

        # 获取年报详情页面
        self.nbjb_list = []  # 年报基本信息
        self.nbzczk_list = []  # 年报资产状况

        self.nbdwdb_list = []
        self.nbgdcz_list = []
        self.nbgqbg_list = []
        self.nbwz_list = []
        self.nbxg_list = []
        self.nbdwtz_list = []

        if year_link:
            for i in range(len(year_link)):
                year = year_list[i]
                link = year_link[i]
                # print 'uiu', i, year, link
                self.y = year

                r = self.get_request(url=link)
                soup = BeautifulSoup(r.text, 'html5lib')
                # print 'Q'*1000
                # print 'nianbaoyesoup:', soup
                # print 'q'*1000
                soup = soup.find(class_='content3')
                div_element_list = soup.find_all(class_='content1')
                for div_element in div_element_list:
                    table_title = div_element.find(class_='titleTop').find('h1').text.strip()
                    table_body = div_element.find('table')
                    # print 'rqs', table_title#, table_body.text
                    # continue
                    if table_title == u'基本信息':
                        self.get_nianbaojiben(table_body)
                    elif table_title == u'网站或网店信息':
                        self.get_nianbaowangzhan(table_body)
                    elif table_title == u'股东及出资信息':
                        self.get_nianbaogudongchuzi(table_body)
                    elif table_title == u'对外投资信息':
                        self.get_nianbaoduiwaitouzi(table_body)
                    elif table_title == u'企业资产状况信息':
                        self.get_nianbaozichanzhuangkuang(table_body)
                    elif table_title == u'股权变更信息':
                        self.get_nianbaoguquanbiangeng(table_body)
                    elif table_title == u'对外提供保证担保信息':
                        self.get_nianbaoduiwaidanbao(table_body)
                    elif table_title == u'修改信息':
                        self.get_nianbaoxiugai(table_body)
                    else:
                        self.info(u'看看是什么：' + table_title)

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

    def get_nianbaojiben(self, soup):
        # print 'nbjb', soup
        family = 'report_base'
        table_id = '40'
        tr_element_list = soup.find_all('tr')  # (".//*[@id='jbxx']/table/tbody/tr")
        values = {}
        json_list = []
        for tr_element in tr_element_list[1:]:
            # th_element_list = tr_element.find_all('th')
            td_element_list = tr_element.find_all('td')
            for td in td_element_list:
                if td.text.strip():
                    td_list = td.text.replace(u'·', '').replace(u'?', '').strip().replace(u' ', '').split(u'：', 1)
                    col = td_list[0].strip()
                    val = td_list[1].strip()
                    # print col, val
                    col = qiyenianbaojiben_column_dict[col]
                    values[col] = val
        values['rowkey'] = '%s_%s_%s_' % (self.cur_mc, self.y, table_id)
        values[family + ':registrationno'] = self.cur_zch
        values[family + ':enterprisename'] = self.cur_mc
        json_list.append(values)
        # print 'jb', values
        self.nbjb_list.append(values)

    def get_nianbaowangzhan(self, soup):
        # print 'nbwz', soup
        family = 'web_site'
        table_id = '41'
        values = {}
        json_list = []
        tr_element_list = soup.find_all('tr')
        cnt = 1

        if len(tr_element_list):
            for tr_ele in tr_element_list:
                if tr_ele.text.strip():
                    li_lists = tr_ele.find_all('li')[1:]
                    for li in li_lists:
                        li_list = li.text.replace(u'·', '').replace(u'?', '').strip().replace(u' ', '').split(u'：', 1)
                        col = li_list[0].strip()
                        val = li_list[1].strip()
                        values[qiyenianbaowangzhan_column_dict[col]] = val
                    values['rowkey'] = '%s_%s_%s_%d' % (self.cur_mc, self.y, table_id, cnt)
                    values[family + ':registrationno'] = self.cur_zch
                    values[family + ':enterprisename'] = self.cur_mc
                    values[family + ':id'] = str(cnt)
                    json_list.append(values)
                    self.nbwz_list.append(values)
                    values = {}
                    cnt += 1
                    # if json_list:
                    #     print 'wz',json_list

    def get_nianbaogudongchuzi(self, soup):
        # print 'nbgd', soup
        family = 'enterprise_shareholder'
        table_id = '42'
        values = {}
        json_list = []

        gd_th = soup.find_all('th')
        tr_element_list = soup.find_all('tr')[1:-1]
        iftr = tr_element_list

        cnt = 1
        for i in range(len(iftr)):
            if iftr[i].text.strip():
                gd_td = iftr[i].find_all('td')
                for j in range(len(gd_th)):
                    th = gd_th[j].text.strip()
                    td = gd_td[j].text.strip()
                    # print i,j,th,td
                    values[qiyenianbaogudong_column_dict[th]] = td
                values['rowkey'] = '%s_%s_%s_%d' % (self.cur_mc, self.y, table_id, cnt)
                values[family + ':registrationno'] = self.cur_zch
                values[family + ':enterprisename'] = self.cur_mc
                values[family + ':id'] = str(cnt)
                json_list.append(values)

                self.nbgdcz_list.append(values)
                values = {}
                cnt += 1
                # if json_list:
                #     print 'nbgdcz', json_list

    def get_nianbaoduiwaitouzi(self, soup):
        # print 'dwtz', soup
        family = 'investment'
        table_id = '47'
        values = {}
        json_list = []

        tr_element_list = soup.find_all('tr')
        cnt = 1
        if len(tr_element_list):
            for tr_ele in tr_element_list:
                if tr_ele.text.strip():
                    li_lists = tr_ele.find_all('li')

                    col = u'公司名称'
                    name = li_lists[0].text.strip()  # 公司名称
                    values[qiyenianbaoduiwaitouzi_column_dict[col]] = name

                    li_list = li_lists[1].text.replace(u'·', '').replace(u'?', '').strip().replace(u' ', '').split(u'：',
                                                                                                                   1)
                    col = li_list[0].strip()
                    val = li_list[1].strip()
                    values[qiyenianbaoduiwaitouzi_column_dict[col]] = val
                    values['rowkey'] = '%s_%s_%s_%d' % (self.cur_mc, self.y, table_id, cnt)
                    values[family + ':id'] = str(cnt)
                    json_list.append(values)
                    self.nbdwtz_list.append(values)
                    values = {}
                    cnt += 1
                    # if json_list:
                    #     print 'nbdwtz', json_list

    def get_nianbaozichanzhuangkuang(self, soup):
        # print 'nbzczt', soup
        family = 'industry_status'
        table_id = '43'

        tr_element_list = soup.find_all("tr")
        values = {}
        json_list = []
        for tr_element in tr_element_list:
            th_element_list = tr_element.find_all('th')
            td_element_list = tr_element.find_all('td')
            if len(td_element_list) > 0:
                col_nums = len(td_element_list)
                for i in range(col_nums):
                    col = th_element_list[i].get_text().strip().replace('\n', '')
                    val = td_element_list[i].get_text().strip().replace('\n', '')
                    if col != u'':
                        values[qiyenianbaozichanzhuangkuang_column_dict[col]] = val
                        #                     print col,val
        values['rowkey'] = '%s_%s_%s_' % (self.cur_mc, self.y, table_id)
        values[family + ':registrationno'] = self.cur_zch
        values[family + ':enterprisename'] = self.cur_mc
        json_list.append(values)
        self.nbzczk_list.append(values)
        # if json_list:
        #     print 'json_nianbaozichan', json_list

    def get_nianbaoguquanbiangeng(self, soup):
        # print 'nbgqbg', soup
        family = 'equity_transfer'
        table_id = '45'
        values = {}
        json_list = []

        gd_th = soup.find_all('th')
        tr_element_list = soup.find_all('tr')[1:-1]
        iftr = tr_element_list

        cnt = 1
        for i in range(len(iftr)):
            if iftr[i].text.strip():
                gd_td = iftr[i].find_all('td')
                for j in range(len(gd_th)):
                    th = gd_th[j].text.strip()
                    td = gd_td[j].text.strip()
                    # print i,j,th,td
                    values[qiyenianbaoguquanbiangeng_column_dict[th]] = td
                values['rowkey'] = '%s_%s_%s_%d' % (self.cur_mc, self.y, table_id, cnt)
                values[family + ':registrationno'] = self.cur_zch
                values[family + ':enterprisename'] = self.cur_mc
                values[family + ':id'] = str(cnt)
                json_list.append(values)
                self.nbgqbg_list.append(values)
                values = {}
                cnt += 1
                # if json_list:
                #     print 'nbgqbg', json_list

    def get_nianbaoduiwaidanbao(self, soup):
        # print 'nbdwdb', soup
        family = 'guarantee'
        table_id = '44'
        values = {}
        json_list = []

        gd_th = soup.find_all('th')
        tr_element_list = soup.find_all('tr')[1:-1]
        iftr = tr_element_list

        cnt = 1
        for i in range(len(iftr)):
            if iftr[i].text.strip():
                gd_td = iftr[i].find_all('td')
                for j in range(len(gd_th)):
                    th = gd_th[j].text.strip()
                    td = gd_td[j].text.strip()
                    # print i,j,th,td
                    values[qiyenianbaoduiwaidanbao_column_dict[th]] = td
                values['rowkey'] = '%s_%s_%s_%d' % (self.cur_mc, self.y, table_id, cnt)
                values[family + ':registrationno'] = self.cur_zch
                values[family + ':enterprisename'] = self.cur_mc
                values[family + ':id'] = str(cnt)
                json_list.append(values)
                self.nbdwdb_list.append(values)
                values = {}
                cnt += 1
                # if json_list:
                #     print 'nbdwdb', json_list

    def get_nianbaoxiugai(self, soup):
        # print 'nbxg', soup
        family = 'modify'
        table_id = '46'
        values = {}
        json_list = []

        gd_th = soup.find_all('th')
        tr_element_list = soup.find_all('tr')[1:-1]
        iftr = tr_element_list

        cnt = 1
        for i in range(len(iftr)):
            if iftr[i].text.strip():
                gd_td = iftr[i].find_all('td')
                for j in range(len(gd_th)):
                    th = gd_th[j].text.strip()
                    td = gd_td[j].text.strip()
                    # print i,j,th,td
                    values[qiyenianbaoxiugaijilu_column_dict[th]] = td
                values['rowkey'] = '%s_%s_%s_%d' % (self.cur_mc, self.y, table_id, cnt)
                values[family + ':registrationno'] = self.cur_zch
                values[family + ':enterprisename'] = self.cur_mc
                values[family + ':id'] = str(cnt)
                json_list.append(values)
                self.nbxg_list.append(values)
                values = {}
                cnt += 1
                # if json_list:
                #     print 'nbxg', json_list

    def get_lock_id(self):
        if self.use_proxy:
            self.release_lock_id()
            self.lock_id = self.proxy_config.get_lock_id()
            self.release_id = self.lock_id

    def release_lock_id(self):
        if self.use_proxy and self.lock_id != '0':
            self.proxy_config.release_lock_id(self.lock_id)
            self.lock_id = '0'

            # def get_request(self, url, params={}, data={}, verify=True, t=0, release_lock_id=False):
            #     """
            #     发送get请求,包含添加代理,锁定ip与重试机制
            #     :param url: 请求的url
            #     :param params: 请求参数
            #     :param data: 请求数据
            #     :param verify: 忽略ssl
            #     :param t: 重试次数
            #     :param release_lock_id: 是否需要释放锁定的ip资源
            #     """
            #     try:
            #         if self.use_proxy:
            #             if not release_lock_id:
            #                 self.headers['Proxy-Authorization'] = self.proxy_config.get_auth_header(lock_id=self.lock_id)
            #             else:
            #                 self.headers['Proxy-Authorization'] = self.proxy_config.get_auth_header(lock_id=self.lock_id, release_id=self.lock_id)
            #         r = self.session.get(url=url, headers=self.headers, params=params, data=data, verify=verify)
            #         if r.status_code != 200:
            #             print u'错误的响应代码 -> %d' % r.status_code , url
            #             raise RequestException()
            #         return r
            #     except RequestException, e:
            #         if t == 15:
            #             raise e
            #         else:
            #             return self.get_request(url, params, data, verify, t+1, release_lock_id)
            #
            # def post_request(self, url, params={}, data={}, verify=True, t=0, release_lock_id=False):
            #     """
            #     发送post请求,包含添加代理,锁定ip与重试机制
            #     :param url: 请求的url
            #     :param params: 请求参数
            #     :param data: 请求数据
            #     :param verify: 忽略ssl
            #     :param t: 重试次数
            #     :param release_lock_id: 是否需要释放锁定的ip资源
            #     :return:
            #     """
            #     try:
            #         if self.use_proxy:
            #             if not release_lock_id:
            #                 self.headers['Proxy-Authorization'] = self.proxy_config.get_auth_header(lock_id=self.lock_id)
            #             else:
            #                 self.headers['Proxy-Authorization'] = self.proxy_config.get_auth_header(lock_id=self.lock_id, release_id=self.lock_id)
            #         r = self.session.post(url=url, headers=self.headers, params=params, data=data, verify=verify)
            #         if r.status_code != 200:
            #             print u'错误的响应代码 -> %d' % r.status_code , url
            #             raise RequestException()
            #         return r
            #     except RequestException, e:
            #         if t == 15:
            #             raise e
            #         else:
            #             return self.post_request(url, params, data, verify, t+1, release_lock_id)


if __name__ == '__main__':
    args_dict = get_args()
    searcher = SiChuan()
    # searcher.get_lock_id()
    # searcher.get_session_token()
    searcher.submit_search_request(u'中国核动力研究设计院印刷厂')  # 天顺橡胶化工有限公司')
    # searcher.release_lock_id()
    # searcher.submit_search_request(u'911302007356029939')#911302007356029939')#奇瑞')#清河县飘丝纺羊绒制品有限公司')
    # 上海益中亘泰物业管理有限公司廊坊分公司') #河北泰华实业集团有限公司')
    # searcher.submit_search_request(keyword=args_dict['companyName'], account_id=args_dict['accountId'], task_id=args_dict['taskId'])
    print json.dumps(searcher.json_result, ensure_ascii=False)
