# coding=utf-8

from gs.Searcher import Searcher
from gs import TimeUtils
import json
from geetest_broker.GeetestBroker import GeetestBrokerRealTime
from bs4 import BeautifulSoup
import re
import os
import sys
import time
from bei_jing.Tables_dict import *
from gs.TimeUtils import *
from gs import CompareStatus
from gs.KafkaAPI import KafkaAPI
import random


class BeiJing(Searcher, GeetestBrokerRealTime):

    xydm = None
    zch = None
    province = u'北京市'
    domain = 'http://bj.gsxt.gov.cn'
    tab_url_set = set()
    flag = True
    cur_time = None

    def __init__(self, dst_topic=None):
        super(BeiJing, self).__init__(use_proxy=True, dst_topic=dst_topic)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:45.0) Gecko/20100101 Firefox/45.0',
        }
        self.set_config()
        self.set_geetest_config()

    def set_config(self):
        # self.group = 'Crawler'  # 正式
        # self.kafka = KafkaAPI("GSCrawlerResult")  # 正式
        # self.group = 'CrawlerTest'  # 测试
        # self.kafka = KafkaAPI("GSCrawlerTest")  # 测试
        # self.topic = 'GsSrc11'
        self.province = u'北京市'
        # self.kafka.init_producer()

    def set_geetest_config(self):
        self.geetest_product = 'popup'
        self.geetest_referer = 'http://bj.gsxt.gov.cn/sydq/loginSydqAction!sydq.dhtml'

    def get_gt_challenge(self):
        url_1 = 'http://bj.gsxt.gov.cn/pc-geetest/register?t=%s' % TimeUtils.get_cur_ts_mil()
        # print url_1
        r_1 = self.get_request(url_1)
        self.challenge = str(json.loads(r_1.text)['challenge'])
        self.gt = str(json.loads(r_1.text)['gt'])

    def get_tag_a_from_db(self, keyword):
        # 无需tagA查询
        return []

    # 遇到公司名称不在首页的情况，手动输入公司编号和company_tags
    # def get_tag_a_from_page(self, keyword, flags=True):
    #     self.flag = flags
    #     gsbh = u'91110117666925640Y' # 公司编号 eg 恒信玺利实业股份有限公司
    #     company_tags = [u'http://bj.gsxt.gov.cn/gjjbj/gjjQueryCreditAction!queryEntIndexInfo.dhtml?entId=977D33FED83742D7B9D59B40F4319B44&clear=true&urltag=1&urlflag=0&credit_ticket=E0BD4AC63B1CD6E3E5BEB86B75122826']
    #     company_list = [keyword]
    #     company_code = [gsbh]
    #     self.xydm = ''
    #     self.zch = ''
    #     self.cur_mc = company_list[0]
    #     self.cur_code = company_code[0]
    #     self.cur_zch = company_code[0]
    #     self.tagA = company_tags[0]
    #     if len(self.cur_code) == 18:
    #         self.xydm = self.cur_code
    #     else:
    #         self.zch = self.cur_code
    #     # print 'name:', company_list[0], 'code:', company_code[0], 'tagA:', company_tags[0]
    #     name_link = company_tags[0]
    #
    #     ent_id = re.search(u'(?<=entId=).*?(?=&)', name_link).group()
    #     creditt = re.search(u'(?<=ket=).*', name_link).group()
    #     # print 'ent_id', ent_id, 'creditt', creditt
    #     self.entId = ent_id
    #     self.creditt = creditt
    #     # print '*.*'*100
    #     r = self.get_request(url=company_tags[0], params={})
    #     # print r.text, r.headers
    #     soup = BeautifulSoup(r.text, 'html5lib')
    #     list_tabs = soup.find(class_='bbox').find_all('a')
    #     self.tab_url = []
    #     for tab in list_tabs:
    #         url = self.domain + tab.get('href')
    #         # print 'tab*url', url
    #         self.tab_url.append(url)
    #
    #     # print '*。*'*100
    #     return company_tags[0]

    def get_tag_a_from_page(self, keyword, flags=True):
        self.get_lock_id()
        self.get_request('http://bj.gsxt.gov.cn/sydq/loginSydqAction!sydq.dhtml')
        validate = self.get_geetest_validate()
        for i in range(12):
            if validate=='':
                validate = self.get_geetest_validate()
            else:
                break
        # print validate
        # self.headers['Host'] = 'bj.gsxt.gov.cn'
        # self.headers['Referer'] = 'http://bj.gsxt.gov.cn/sydq/loginSydqAction!sydq.dhtml'

        url_1 = "http://bj.gsxt.gov.cn/pc-geetest/validate"
        params_1 = {
            'geetest_challenge': self.challenge,
            'geetest_validate': validate,
            'geetest_seccode': '%s|jordan' % validate,
        }
        # self.post_request(url=url_1, params=params_1)
        r_1=self.post_request(url=url_1,data=params_1)
        print r_1.text
        # for i in range(12):
        #     if r_1.status_code!=200:
        #         r_1 = self.post_request(url=url_1, params=params_1)
        #     else:
        #         break
        url_2 = "http://bj.gsxt.gov.cn/es/esAction!entlist.dhtml?urlflag=0&challenge="+self.challenge
        data_2 = {
            'keyword': keyword,
            'nowNum': '',
            'clear': '请输入企业名称、统一社会信用代码或注册号',
            'urlflag': '0',
        }
        r_2 = self.post_request_302(url_2, data=data_2)
        # for i in range(12):
        #     if r_2.status_code!=200:
        #         r_2 = self.post_request(url_2, params=data_2)
        #     else:
        #         break
        r_2.encoding = 'utf-8'
        soup = BeautifulSoup(r_2.text, 'html5lib')
        # print 'soup:', soup
        results = soup.select('div.search-result ul li')
        # print results
        if results==[]:         #查询无结果，循环请求
            for i in range(16):
                print '无结果，循环次数',i
                self.get_lock_id()
                self.get_request('http://bj.gsxt.gov.cn/sydq/loginSydqAction!sydq.dhtml')
                validate = self.get_geetest_validate()
                for i in range(12):
                    if validate == '':
                        validate = self.get_geetest_validate()
                    else:
                        break
                url_1 = "http://bj.gsxt.gov.cn/pc-geetest/validate"
                params_1 = {
                    'geetest_challenge': self.challenge,
                    'geetest_validate': validate,
                    'geetest_seccode': '%s|jordan' % validate,
                }
                r_1 = self.post_request(url=url_1, data=params_1)
                url_2 = "http://bj.gsxt.gov.cn/es/esAction!entlist.dhtml?urlflag=0&challenge=" + self.challenge
                data_2 = {
                    'keyword': keyword,
                    'nowNum': '',
                    'clear': '请输入企业名称、统一社会信用代码或注册号',
                    'urlflag': '0',
                }
                r_2 = self.post_request_302(url_2, data=data_2)
                r_2.encoding = 'utf-8'
                soup = BeautifulSoup(r_2.text, 'html5lib')
                results = soup.select('div.search-result ul li')
                if results!=[]:
                    break
                elif i==15:
                    raise Exception(u'频繁访问错误页面')
                else:
                    time.sleep(2)

        self.tagA = None
        # print len(results)
        for result in results:
            start_name = result.find('span').text.strip()
            handle_name = self.process_mc(start_name)
            if handle_name!=keyword:
                continue
            elif len(results) > 0 and u'查询到<span class="light">0</span>条信息'not in r_2.text:
                company_list = []
                company_code = []
                company_tags = []
                sort_index=[]
                # print u'有查询结果'
                self.info(u'查询有结果，开始解析')
                cnt = 1
                for result in results:
                    name = result.find('span').text.strip()
                    name = self.process_mc(name)
                    # print name, keyword
                    if name == keyword:
                        try:
                            company_status = result.find(class_="ent_state1").text.strip()
                        except:
                            company_status = result.find(class_="ent_state2").text.strip()
                        linko = result.find('table').get('onclick')
                        link = re.search(u'(?<=").*?(?=")', linko).group()
                        tagA = self.domain + link
                        code = result.find('td').contents[1].strip()
                        sort_index.append(company_status)
                        company_list.append(name)
                        company_tags.append(tagA)
                        company_code.append(code)
                        continue
                    else:
                        index_n=0

                if len(sort_index)>1:#判断出现同名情况
                    for company_status_i in sort_index:
                        if CompareStatus.status_dict[company_status_i]==1:
                            index_n=sort_index.index(company_status_i)
                else:
                    # pass
                    index_n=0
                self.cur_mc = company_list[index_n]
                self.cur_zch = company_code[index_n]
                self.cur_code = company_code[index_n]
                self.tagA = company_tags[index_n]
                if len(company_code[index_n]) == 18:
                    self.xydm = company_code[index_n]
                else:
                    self.zch = company_code[index_n]
                ent_id = re.search(u'(?<=entId=).*?(?=&)', company_tags[index_n]).group()
                creditt = re.search(u'(?<=ket=).*', company_tags[index_n]).group()
                # print 'ent_id', ent_id, 'creditt', creditt
                self.entId = ent_id
                self.creditt = creditt
                # print '*.*'*100
                r = self.get_request_302(url=company_tags[index_n], params={})
                # print r.text, r.headers
                soup = BeautifulSoup(r.text, 'html5lib')
                list_tabs = soup.find(class_='bbox').find_all('a')
                self.tab_url = []
                for tab in list_tabs:
                    url = self.domain + tab.get('href')
                    # print 'tab*url', url
                    self.tab_url.append(url)
            else:
                # print r_2.text
                if u'查询到<span class="light">0</span>条信息'in r_2.text:
                    print u'查无结果', keyword
                else:
                    print u'频繁访问错误页面'
                    raise Exception(u'错误页面')
        return self.tagA

    def get_search_args(self, tag_a, keyword):

        if self.flag:
            # print 'mc:', self.cur_mc, 'wd:',keyword,tag_a
            if not self.cur_mc and tag_a:
                self.get_tag_a_from_page(keyword, flags=True)
                return 1
            if self.cur_mc == keyword:
                return 1
            else:
                self.info(u'查询结果与输入不一致，保存公司名')
                self.save_company_name_to_db(self.cur_mc)
                return 0
        else:
            self.info(u'注册号对应公司名为:')
            self.info(self.cur_mc)
            return 1

    def parse_detail(self):
        """
        解析公司详情信息
        :param kwargs:
        :return:
        """
        self.info(u'解析基本信息')
        self.get_ji_ben()
        self.info(u'解析股东信息')
        self.get_gu_dong()
        self.get_zhu_guan_bu_men()
        self.info(u'解析变更信息')
        self.get_bian_geng()
        self.info(u'解析主要人员')
        self.get_zhu_yao_ren_yuan()
        # self.info(u'解析股权出质')
        # self.get_gu_quan_chu_zhi()
        # self.info(u'解析行政处罚')
        # self.get_xing_zheng_chu_fa()
        # self.info(u'解析经营异常')
        # self.get_jing_ying_yi_chang()
        # self.info(u'解析动产抵押')
        # self.get_dong_chan_di_ya()

        # print 'jb_step_json', self.json_result
        # self.info(u'解析分支机构')
        # self.get_fen_zhi_ji_gou()
        # self.get_gu_dong_chu_zi()           # New Gudong-details(temp)
        # print 'gd_step_json', self.json_result
        # print 'bg_step_json', self.json_result
        # self.get_qing_suan()
        # self.info(u'解析严重违法')
        # self.get_yan_zhong_wei_fa()
        # self.info(u'解析抽查检查')
        # self.get_chou_cha_jian_cha()
        # self.info(u'开始解析年报')
        # self.get_nian_bao()
        # print 'the_last_json_result', len(self.json_result), self.json_result
        # json_go = json.dumps(self.json_result, ensure_ascii=False)
        # print 'the_last_json_result:', len(self.json_result), get_cur_time()   ,  json_go
        self.release_lock_id()

    def get_ji_ben(self):
        """
        查询基本信息
        :return: 基本信息结果
        """
        self.tab_url_set.clear()
        json_list = []
        family = 'Registered_Info'
        table_id = '01'
        self.json_result[family] = []
        # url = 'http://qyxy.baic.gov.cn/gjjbj/gjjQueryCreditAction!openEntInfo.dhtml?' \
        #       'entId=%s&credit_ticket=%s&entNo=%s&timeStamp=%s' % (self.entId, self.creditt,  self.entNo, self.cur_time)
        url = 'http://bj.gsxt.gov.cn/gjjbj/gjjQueryCreditAction!openEntInfo.dhtml?entId=%s&clear=true&urltag=1&credit_ticket=%s' %(self.entId, self.creditt)
        # print 'jiben_url', url
        # params = {'credit_ticket':self.credit_ticket,'entId':self.entId,'entNo':self.entNo,'timeStamp':self.cur_time}

        r = self.get_request(url=url, params={})
        # self.proxy_config.release_lock_id(self.lock_id)
        # self.lock_id = '0'
        # r.encoding = 'gbk'
        # print r.status_code
        r.encoding = 'utf-8'
        soup = BeautifulSoup(r.text, 'lxml')
        # print 'jiben_soup', soup
        tab_list = soup.find_all('iframe')
        # print tab_list
        for t in tab_list:
            tab_url = t.get('src')
            self.tab_url_set.add('http://bj.gsxt.gov.cn' + tab_url)
        # print 'table_url', tab_url
        for t in self.tab_url:
            self.tab_url_set.add(t)
        # print 'tab_url_set', self.tab_url_set
        # print soup
        # print '*******ji_ben*******', soup
        tr_element_list = soup.find('table').find_all('tr')#(".//*[@id='jbxx']/table/tbody/tr")
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
        values['rowkey'] = '%s_%s_%s_' % (self.cur_mc, table_id, self.cur_zch)
        values[family + ':registrationno'] = self.cur_zch
        values[family + ':enterprisename'] = self.cur_mc
        values[family + ':tyshxy_code'] = self.xydm
        self.xydm=None
        values[family + ':zch'] = self.zch
        values[family + ':lastupdatetime'] = get_cur_time()
        values[family + ':province'] = u'北京市'
        json_list.append(values)
        self.json_result[family] = json_list
        # print 'jiben_values',values

    def get_gu_dong(self):
        """
        查询股东信息
        :param param_pripid:
        :param param_type:
        :return:
        """
        family = 'Shareholder_Info'
        table_id = '04'
        json_list = []
        col_desc_list = []
        # url = 'http://qyxy.baic.gov.cn/gjjbj/gjjQueryCreditAction!touzirenInfo.dhtml'
        url = self.domain + '/gjjbj/gjjQueryCreditAction!touzirenInfo.dhtml?ent_id=%s&clear=true&urltag=2&credit_ticket=%s' %(self.entId, self.creditt)
        # print self.tab_url_set
        # print 'gudongurl', url
        r = self.get_request(url=url, params={})
        # print r.status_code
        soup = BeautifulSoup(r.text, 'html5lib')
        # print 'gudong_soup', soup
        # print type(soup)
        if u'暂无股东信息' in soup.find('table').text or u'暂无股东名称' in soup.find('table').text:
            return
        elif u'暂无主管部门（出资人）信息' in soup.find('table').text:
            return
        try:
            turn_page_text = soup.find(class_='pages').contents[0]
            # print 'turn_page_text', turn_page_text
            turn_page = re.search(u'(?<=共)[^共]*?(?=页)', turn_page_text).group()
            # turn_page = re.search(u'(?<=共)\d*?(?=页)', turn_page_text).group()
            turn_page = int(turn_page)
            # print 'turn_page', turn_page
        except:
            # print u'无分页'
            self.info(u'无分页')
            turn_page = 1

        tr_list = soup.find('table').find_all('tr')
        # print '@@@@@@@',tr_list
        # print type(tr_list)
        th_list = soup.find('table').find_all('th')
        if len(tr_list) > 1:
            idx = 0
            for tr in tr_list[1:]:
                idx += 1
                json_dict = {}
                gd_td = tr.find_all('td')
                for j in range(len(gd_td)):
                    th = th_list[j].text.strip()
                    td = gd_td[j].text.strip()
                    if th == u'序号':
                        continue
                    if td == u'查看':
                        td = gd_td[j].a.get('onclick')
                        # print 'gudong', td
                        chr_id = re.search(u'(?<=[(]).*(?=[)])', td).group().split(u',')[1].strip("'")
                        bf = re.search(u'(?<=[(]).*(?=[)])', td).group().split(u',')[2].strip("'")
                        # print 'gudong_chr_id', chr_id, 'bf', bf,'count', idx
                        detail_url = 'http://bj.gsxt.gov.cn/gjjbjTab/gjjTabQueryCreditAction!gdczDetail.dhtml'
                        params = {'ajax': 'true', 'chr_id': chr_id, 'dateflag': bf, 'ent_id': self.entId, 'time': get_cur_ts_mil()}
                        # print 'params', params
                        # detail_url = 'http://qyxy.baic.gov.cn/gjjbj/gjjQueryCreditAction!touzirenInfo.dhtml?chr_id=%s&entName=&timeStamp=%s&fqr=' %(chr_id,self.cur_time)
                        r = self.post_request(url=detail_url, params=params)    # 股东详情网站响应慢，经常超时
                        # # r.encoding = 'gbk'
                        soup = BeautifulSoup(r.text, 'html5lib')
                        # print 'detail_url', detail_url
                        # td = detail_url
                        self.get_gu_dong_detail(soup, json_dict)
                        # self.load_func(td)  抓取详情页内容方法，见cnt分页内容
                    json_dict[gudong_column_dict[th]] = td
                json_dict['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.cur_zch, self.today, idx)
                json_dict[family + ':registrationno'] = self.cur_zch
                json_dict[family + ':enterprisename'] = self.cur_mc
                json_dict[family + ':id'] = str(idx)
                # print json.dumps(json_dict, ensure_ascii=False)
                json_list.append(json_dict)

            if turn_page > 1:
                for p in range(1,turn_page):
                    url = 'http://bj.gsxt.gov.cn/gjjbj/gjjQueryCreditAction!touzirenInfo.dhtml?chr_id=&credit_ticket=%s' % self.creditt
                    params = {'ent_id': self.entId, 'pageNo': p, 'pageNos': p+1, 'pageSize': 5, 'urltag': ''}
                    r = self.post_request_302(url, data=params)
                    # print r.status_code
                    soup = BeautifulSoup(r.text, 'html5lib')
                    # print 'gudong',p,soup
                    sto_list = soup.find('table').find_all('tr')
                    # print sto_list
                    if len(sto_list) > 1:
                        for tr in sto_list[1:]:
                            idx += 1
                            json_dict = {}
                            gd_td = tr.find_all('td')
                            for j in range(len(gd_td)):
                                th = th_list[j].text.strip()
                                td = gd_td[j].text.strip()
                                if th == u'序号':
                                    continue
                                if td == u'查看':
                                    td = gd_td[j].a.get('onclick')
                                    # print 'gudong', td
                                    chr_id = re.search(u'(?<=[(]).*(?=[)])', td).group().split(u',')[1].strip("'")
                                    bf = re.search(u'(?<=[(]).*(?=[)])', td).group().split(u',')[2].strip("'")
                                    # print 'gudong_chr_id', chr_id, 'bf', bf, 'count', idx
                                    detail_url = 'http://bj.gsxt.gov.cn/gjjbjTab/gjjTabQueryCreditAction!gdczDetail.dhtml'
                                    params = {'ajax':'true','chr_id':chr_id,'dateflag':bf,'ent_id':self.entId,'time':get_cur_ts_mil()}
                                    # detail_url = 'http://qyxy.baic.gov.cn/gjjbj/gjjQueryCreditAction!touzirenInfo.dhtml?chr_id=%s&entName=&timeStamp=%s&fqr=' %(chr_id,self.cur_time)
                                    # print 'detail_url', detail_url
                                    # td = detail_url
                                    r = self.post_request(url=detail_url, params=params)
                                    # r.encoding = 'gbk'
                                    soup = BeautifulSoup(r.text, 'html5lib')
                                    self.get_gu_dong_detail(soup, json_dict)
                                    # self.load_func(td)  抓取详情页内容方法，见cnt分页内容
                                json_dict[gudong_column_dict[th]] = td
                            json_dict['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.cur_zch, self.today, idx)
                            json_dict[family + ':registrationno'] = self.cur_zch
                            json_dict[family + ':enterprisename'] = self.cur_mc
                            json_dict[family + ':id'] = str(idx)
                            # print json.dumps(json_dict, ensure_ascii=False)
                            json_list.append(json_dict)

            if json_list:
                # print 'gudong_json', json_list
                self.json_result[family] = json_list

    def get_gu_dong_chu_zi(self):                   # New func in Beijing Site
        family = 'Shareholder_Info'
        table_id = '04'

        json_list = []
        values = {}
        detail_th_list = ['shareholder_temp','subscripted_capital','actualpaid_capital',\
                          'subscripted_method','subscripted_amount','subscripted_time','sub_date',\
                          'actualpaid_method','actualpaid_amount','actualpaid_time','act_date']
        detail_cn_list = [u'股东', u'认缴额（万元）', u'实缴额（万元）',\
                          u'认缴出资方式',u'认缴出资额（万元）',u'认缴出资日期',u'公示日期',\
                          u'实缴出资方式',u'实缴出资额（万元）',u'实缴出资日期',u'公示日期']
        url = 'http://bj.gsxt.gov.cn/newChange/newChangeAction!getTabForNB_new.dhtml?entId=%s&flag_num=1&clear=true&urltag=15&credit_ticket=%s' % (self.entId, self.creditt)
        r = self.get_request(url=url, params={})
        soup = BeautifulSoup(r.text, 'html5lib')
        table = soup.find(class_='table-result')
        tr_list = table.tbody.find_all('tr', recursive=False)
        if len(tr_list) > 2:              # 说明有结果
            cnt = 1
            for tr in tr_list[2:]:
                td_list1 = tr.find_all('td')[:3]
                td_list2 = tr.find_all('table')[0].find_all('td')
                td_list3 = tr.find_all('table')[1].find_all('td')
                td_list1.extend(td_list2)
                td_list1.extend(td_list3)
                td_list = td_list1
                # print td_list
                # print len(td_list)
                col_num = len(td_list)
                for i in range(col_num):
                    td = td_list[i].text.strip()
                    # print cnt, '*cn*', detail_cn_list[i], '*th*', detail_th_list[i], '*td*', td
                    values[detail_th_list[i]] = td
                json_list.append(values)
                values={}
                cnt += 1
            # if json_list:
            #     print 'gd_details_json_list', json.dumps(json_list, ensure_ascii=False)

        # pass

    def get_zhu_guan_bu_men(self):
        family = 'Shareholder_Info'
        table_id = '04'
        json_list = []
        col_desc_list = []
        url = 'http://qyxy.baic.gov.cn/gjjbj/gjjQueryCreditAction!zgbmFrame.dhtml'
        if url not in self.tab_url_set:
            return
        idx = 0
        i = -1
        while i < 1000:
            i += 1
            # self.info(u'股东第%d页' % i)
            if i == 0:
                params = {
                    'ent_id': self.entId,
                    'clear': 'true',
                    # 'timeStamp': self.cur_time
                }
            else:
                params = {
                    'clear': '',
                    'ent_id': self.entId,
                    'fqr': '',
                    'pageNo': str(i),
                    'pageNos': str(i + 1),
                    'pageSize': '5'
                }
            r = self.get_request(url=url, params=params)
            soup = BeautifulSoup(r.text, 'lxml')
            tr_list = soup.select('table tr')
            if i == 0:
                if len(tr_list) == 0:
                    i = -1
                    continue
                th_list = tr_list[1].select('th')
                for th in th_list:
                    col_desc_list.append(th.text.strip())
            if len(tr_list) > 2:
                for tr in tr_list[1:-1]:
                    idx += 1
                    json_dict = {}
                    gd_td = tr.select('td')
                    for j in range(len(gd_td)):
                        th = col_desc_list[j]
                        if th == u'序号':
                            continue
                        td = gd_td[j].text.strip()
                        json_dict[zhuguanbumen_column_dict[th]] = td
                    json_dict['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.cur_zch, self.today, idx)
                    json_dict[family + ':registrationno'] = self.cur_zch
                    json_dict[family + ':enterprisename'] = self.cur_mc
                    json_dict[family + ':id'] = str(idx)
                    # print json.dumps(json_dict, ensure_ascii=False)
                    json_list.append(json_dict)

                page_ele_list = tr_list[-1].select('th')[0].findChildren()
                last_page = '0'
                for page_ele in page_ele_list:
                    cur = page_ele.text.strip()
                    if cur == '>>':
                        # print last_page, cur
                        break
                    else:
                        last_page = cur
                if str(i + 1) == last_page:
                    break
            else:
                break

    def get_gu_dong_detail(self, soup, values):
        """
        查询股东详情
        :param param_pripid:
        :param param_invid:
        :return:
        """
        family = 'Shareholder_Info'
        table_id = '04'

        # r = self.get_request(url=url, params={})
        # # r.encoding = 'gbk'
        # soup = BeautifulSoup(r.text, 'lxml')
        # print '***__****gudong_detail*******', soup

        table_list = soup.find_all(class_='table-result')
        for table in table_list:
            th_list = table.find_all('th')
            try:
                td_list = table.find_all('td')
            except Exception as e:
                # print '****', e
                continue
            th_num = len(th_list)
            td_num = len(td_list)
            if th_num == td_num:
                for i in range(th_num):
                    th = th_list[i].text.strip()
                    td = td_list[i].text.strip()
                    if th == u'股东及出资人名称':
                        continue
                    values[gudong_column_dict[th]] = td

        # print 'gdl_values',len(values),values

        #
        # detail_tr_list = soup.find(class_='detailsList').find_all('tr')
        # detail_th_list = ['subscripted_capital','actualpaid_capital','subscripted_method','subscripted_amount','subscripted_time','actualpaid_method','actualpaid_amount','actualpaid_time']
        # detail_th_new_list=[family+':'+x for x in detail_th_list]
        # # print 'detail_th_new_list', detail_th_new_list
        # for tr_ele in detail_tr_list[3:-1]:
        #     td_ele_list = tr_ele.find_all('td')[1:]
        #     detail_col_nums = len(td_ele_list)
        #     # print detail_col_nums
        #     for m in range(detail_col_nums):
        #         col = detail_th_new_list[m]
        #         td = td_ele_list[m]
        #         val = td.text.strip()
        #         values[col] = val
        #         print col,val
        # print 'gdl_values',len(values),values

    def get_bian_geng(self):
        family = 'Changed_Announcement'
        table_id = '05'

        url = ''
        for ur in self.tab_url_set:
            if u'http://bj.gsxt.gov.cn/gjjbj/gjjQueryCreditAction!biangengFrame.dhtml' in ur:
                url = ur
        if not url:
            return
        # print 'biangeng_url', url
        r = self.post_request_302(url=url, params={})
        soup = BeautifulSoup(r.text, 'html5lib')
        # print 'biangeng_soup', soup
        if u'暂无变更信息' in soup.find('table').text:
            return
        try:
            turn_page_text = soup.find(class_='pages').find(id='pagescount')
            # print 'turn_page_text', turn_page_text
            # turn_page = re.search(u'(?<=共)[^共]*?(?=页)', turn_page_text).group()
            # turn_page = re.search(u'(?<=共)\d*?(?=页)', turn_page_text).group()
            turn_page = turn_page_text.get('value')
            turn_page = int(turn_page)
            # print 'turn_page', turn_page
        except Exception as e:
            # print u'无分页', e
            turn_page = 1

        json_list = []
        tr_list = soup.find('table').find_all('tr')
        th_list = soup.find('table').find_all('th')
        if len(tr_list) > 1:
            idx = 1
            th_list = [th.text.strip() for th in th_list]
            for tr in tr_list[1:]:

                json_dict = {}
                td_list = tr.find_all('td')

                if len(td_list) == 4:
                    linka = td_list[2].a.get('onclick')
                    sub_ling = re.search(u'(?<=[(]).*(?=[)])', linka).group().replace("'", '')
                    # sub_lin = sub_ling.split(',')[0].strip().replace("'", '')
                    link = self.domain+sub_ling
                    params = {'ajax':'true', 'time':get_cur_ts_mil()}
                    # print 'link', link, 'params', params
                    r2 = self.post_request(link, params=params)
                    sop = BeautifulSoup(r2.text, 'html5lib')
                    # print 'bgdetails_soup', sop
                    self.get_detail(sop)
                    json_dict[biangeng_column_dict[th_list[1]]] = td_list[1].text.strip()
                    json_dict[biangeng_column_dict[th_list[2]]] = self.bgq
                    json_dict[biangeng_column_dict[th_list[3]]] = self.bgh
                    json_dict[biangeng_column_dict[th_list[4]]] = td_list[3].text.strip()
                elif len(td_list) == 5:
                    for k in range(1, 5):
                        json_dict[biangeng_column_dict[th_list[k]]] = td_list[k].text.strip()
                json_dict['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.cur_zch, self.today, idx)
                json_dict[family + ':registrationno'] = self.cur_zch
                json_dict[family + ':enterprisename'] = self.cur_mc
                json_dict[family + ':id'] = str(idx)
                idx += 1
                json_list.append(json_dict)
                # print idx, json.dumps(json_dict, ensure_ascii=False)

            if turn_page > 1:
                # print u'快来DO变更翻页的开发'
                for p in range(2, turn_page+1):
                    # print 'cnt',p
                    url = 'http://bj.gsxt.gov.cn/gjjbj/gjjbj/gjjQueryCreditAction!biangengFrame.dhtml'
                    params = {'ent_id': self.entId, 'pageNo': p-1, 'pageNos': p, 'pageSize': 10,'urltag':5}
                    r = self.post_request_302(url=url, params=params)
                    # for i in range(12):
                    #     if r.status_code!=200:
                    #         r = self.post_request(url=url, params=params)
                    #     else:
                    #         break
                    soup = BeautifulSoup(r.text, 'html5lib')
                    # print 'subpage-bg', soup
                    tr_list = soup.find('table').find_all('tr')
                    # th_list = soup.find('table').find_all('th')
                    if len(tr_list) > 1:
                        # th_list = [th.text.strip() for th in th_list]
                        for tr in tr_list[1:]:

                            json_dict = {}
                            td_list = tr.find_all('td')

                            if len(td_list) == 4:
                                linka = td_list[2].a.get('onclick')
                                sub_ling = re.search(u'(?<=[(]).*(?=[)])', linka).group().replace("'", '')
                                # sub_lin = sub_ling.split(',')[0].strip().replace("'", '')
                                link = self.domain+sub_ling
                                params = {'ajax':'true', 'time':get_cur_ts_mil()}
                                # print 'link', link, 'params', params
                                r2 = self.post_request(link, params=params)
                                sop = BeautifulSoup(r2.text, 'html5lib')
                                # print 'bgdetails_soup', sop
                                self.get_detail(sop)
                                json_dict[biangeng_column_dict[th_list[1]]] = td_list[1].text.strip()
                                json_dict[biangeng_column_dict[th_list[2]]] = self.bgq
                                json_dict[biangeng_column_dict[th_list[3]]] = self.bgh
                                json_dict[biangeng_column_dict[th_list[4]]] = td_list[3].text.strip()
                            elif len(td_list) == 5:
                                for k in range(1, 5):
                                    json_dict[biangeng_column_dict[th_list[k]]] = td_list[k].text.strip()
                            json_dict['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.cur_zch, self.today, idx)
                            json_dict[family + ':registrationno'] = self.cur_zch
                            json_dict[family + ':enterprisename'] = self.cur_mc
                            json_dict[family + ':id'] = str(idx)
                            idx += 1
                            json_list.append(json_dict)
                            # print idx, json.dumps(json_dict, ensure_ascii=False)


            if json_list:
                self.json_result[family] = json_list
                # print 'biangeng_json', json.dumps(json_list, ensure_ascii=False)

        return

    def get_detail(self, sop):    # 变更详情专用
        row_data = []
        # tables=self.driver.find_elements_by_xpath("//*[@id='tableIdStyle']/tbody")
        tables = sop.find_all(class_='table-result')[1:]
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
                    if len(tds) == col_nums and u'无' not in tr.text:
                        td = tds[j]
                        val = td.text.strip()
                    else:
                        val = u'无'
                    row = col+u'：'+val
                    # print 'row', j, row
                    row_data.append(row)
            if u'变更前' in bt:
                self.bgq = u'；'.join(row_data)
                # print 'bgq',self.bgq
            elif u'变更后' in bt:
                self.bgh = u'；'.join(row_data)
                # print 'bgh',self.bgh
            row_data = []

    def get_zhu_yao_ren_yuan(self):
        """
        查询主要人员信息
        :param param_pripid:
        :param param_type:
        :return:
        """
        family = 'KeyPerson_Info'
        table_id = '06'
        # self.json_result[family] = []
        json_list = []
        values = {}
        # url = 'http://qyxy.baic.gov.cn/gjjbj/gjjQueryCreditAction!zyryFrame.dhtml'
        url = 'http://bj.gsxt.gov.cn/gjjbj/gjjQueryCreditAction!zyryFrame.dhtml?ent_id=%s&clear=true&urltag=3&credit_ticket=%s' %(self.entId, self.creditt)
        r = self.get_request(url, params={})
        soup = BeautifulSoup(r.text, 'html5lib')
        # print 'zhuyaorenyuan_soup',
        try:
            tb = len(soup.find_all('tbody'))
        except:
            tb = 0

        if tb > 1:
            tb_list = soup.find_all('tbody')
            cnt = 1
            for t in range(tb):
                tson = tb_list[t].find_all('tr')
                if len(tson):
                    name = tson[0].text.strip()
                    posn = tson[1].text.strip()
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

        if json_list:
            self.json_result[family] = json_list

    def get_fen_zhi_ji_gou(self):
        family = 'Branches'
        table_id = '08'
        # self.json_result[family] = []

        url = ''
        for ur in self.tab_url_set:
            if u'http://bj.gsxt.gov.cn/gjjbj/gjjQueryCreditAction!fzjgFrame.dhtml' in ur:
                url = ur
        if not url:
            return
        # print 'fenzhijigou_url', url
        r = self.get_request(url=url, params={})
        soup = BeautifulSoup(r.text, 'html5lib')
        # print 'fenzhijigou_soup', soup
        # print '*'*20
        # return

        tb_list = soup.find_all('table')
        if u'暂无分支机构信息' in soup.find('table').text:
            return
        else:
            numtext = soup.find('span', class_='more').text.strip()
            num = re.search(u'\d+',numtext).group()
            n = int(num)
            if n > 9:
                pagetext = soup.find('a', class_='more').get('onclick')
                url_sub = re.search(u'(?<=[(]).*(?=[)])', pagetext).group().replace("'", '')
                url = self.domain + url_sub
                # print 'url-fenzhijigou-fenye', url
                r = self.get_request(url=url,params={})
                soup = BeautifulSoup(r.text, 'html5lib')
                # print 'fenzhijigou-fenye-soup',soup
                tb_list = soup.find_all(class_='detailsList')
            if len(tb_list) > 0:
                # print 'kkk'
                json_list=[]
                values = {}
                idn = 1
                for tb in tb_list:

                    td_element_list = tb.find_all('td')

                    values[fenzhijigou_column_dict[u'名称']] = td_element_list[0].text.strip()
                    values[fenzhijigou_column_dict[u'注册号']] = td_element_list[1].text.strip().replace(u'·', '').split(u'：')[1]
                    values[fenzhijigou_column_dict[u'登记机关']] = td_element_list[2].text.strip().replace(u'·', '').split(u'：')[1]
                    values['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.cur_zch, self.today, idn)
                    values[family + ':registrationno'] = self.cur_zch
                    values[family + ':enterprisename'] = self.cur_mc
                    values[family + ':id'] = str(idn)
                    # print json.dumps(values, ensure_ascii=False)
                    json_list.append(values)
                    values = {}
                    idn += 1
                if json_list:
                    self.json_result[family] = json_list
                    # print '-,-**fenzhijigou_json_list', len(json_list), json_list

    def get_qing_suan(self):
        """
        查询清算信息
        :param param_pripid:
        :param param_type:
        :return:
        """
        family = 'liquidation_Information'
        table_id = '09'
        self.json_result[family] = []

        url = ''
        for ur in self.tab_url_set:
            if u'http://bj.gsxt.gov.cn/gjjbj/gjjQueryCreditAction!qsxxFrame.dhtml' in ur:
                url = ur
        if not url:
            return
        # print 'qingsuan_url', url
        r = self.get_request(url=url, params={})
        soup = BeautifulSoup(r.text, 'html5lib')
        # print 'qingsuan_soup', soup
        print '*'*20
        return

        url = 'http://qyxy.baic.gov.cn/gjjbj/gjjQueryCreditAction!qsxxFrame.dhtml'
        if url not in self.tab_url_set:
            return
        params = {'ent_id': self.entId}
        r = self.post_request(url=url, params=params)
        soup = BeautifulSoup(r.text, 'lxml')
        script_list = soup.select('html > head > script')
        if len(script_list) > 0:
            result_text = script_list[-1].text.strip()
            # print result_text
            result_text = result_text[len('$(document).ready(function()'):-2]

            start_idx = result_text.index('[')
            stop_idx = result_text.index(']') + len(']')
            result_text = result_text[start_idx:stop_idx]
            # print result_text
            result_json = json.loads(result_text)
        else:
            result_json = []
        cheng_yuan_list = []
        for j in result_json:
            cheng_yuan_list.append(j['liqmem'])
        cheng_yuan = ','.join(cheng_yuan_list)
        fu_ze_ren = ''
        fu_ze_ren_list = soup.select('html > body > table > thead > tr:nth-of-type(2) > td')
        if len(fu_ze_ren_list) > 0:
            fu_ze_ren = self.pattern.sub('', fu_ze_ren_list[0].text)
        result_json = []
        if cheng_yuan != '' and fu_ze_ren != '':
            result_json.append({'rowkey': '%s_%s_%s_' % (self.cur_mc, table_id, self.cur_zch),
                                family + ':' + 'liquidation_member': 'cheng_yuan',
                                family + ':' + 'liquidation_pic': 'fu_ze_ren',
                                family + ':registrationno': self.cur_zch,
                                family + ':enterprisename': self.cur_mc
                                })
            self.json_result[family].extend(result_json)

    def get_dong_chan_di_ya(self):
        """
        查询动产抵押信息
        :param param_pripid:
        :param param_type:
        :return:
        """
        family = 'Chattel_Mortgage'
        table_id = '11'
        # self.json_result[family] = []
        values={}
        json_list=[]
        # url = 'http://qyxy.baic.gov.cn/gjjbjTab/gjjTabQueryCreditAction!dcdyFrame.dhtml'
        url = 'http://bj.gsxt.gov.cn/gjjbjTab/gjjTabQueryCreditAction!dcdyFrame.dhtml?entId=%s&clear=true&urltag=12&credit_ticket=%s' %(self.entId, self.creditt)
        # if url not in self.tab_url_set:
        #     return
        # params = {
        #     'entId': self.entId,
        #     'clear': 'true',
        # }
        # print 'dongchandiya_url',self.cur_time,url
        r = self.get_request_302(url=url, params={})
        # r.encoding = 'gbk'
        soup = BeautifulSoup(r.text, 'html5lib')
        # print '*******dongchandiya*******', soup
        # return
        row_cnt = len(soup.find(class_="table-result").find_all('tr'))

        # self.dcdydj_list = []
        # self.dyqrgk_list = []
        # self.bdbzqgk_list = []
        # self.dywgk_list = []
        # self.dcdybg_list = []
        # self.dcdyzx_list = []

        if row_cnt >= 2 and u'暂无动产抵押登记信息' not in soup.find(class_="table-result").text:
            # print 'come_on_bb_not_OK'
            try:
                turn_page_text = soup.find(class_='pages').contents[0]
                print 'turn_page_text', turn_page_text
                turn_page = re.search(u'(?<=共)[^共]*?(?=页)', turn_page_text).group()
                # turn_page = re.search(u'(?<=共)\d*?(?=页)', turn_page_text).group()
                turn_page = int(turn_page)
                print 'turn_page', turn_page
            except:
                # print u'无分页'
                turn_page = 1

            tr_element_list = soup.find(class_="table-result").find_all('tr')
            th_element_list = soup.find(class_="table-result").find_all('tr')[0].find_all('th')
            idn = 1
            for tr_element in tr_element_list[1:]:
                td_element_list = tr_element.find_all('td')
                col_nums = len(th_element_list)
                for j in range(col_nums):
                    col_dec = th_element_list[j].text.strip().replace('\n','')
                    col = dongchandiyadengji_column_dict[col_dec]
                    td = td_element_list[j]
                    val = td.text.strip()
                    if val == u'查看':
                        link = re.findall("'(.*)'",td.a.get('onclick'))[0]
                        link = self.domain + link
                        detail_dict=self.get_dongchandiya_detail(link)
                        values[col] = detail_dict
                        # print 'dcdy_link', link
                        # self.get_dongchandiya_detail(link)
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

            if turn_page > 1:
                # print u'快来DO动产抵押翻页的开发'
                for p in range(2, turn_page+1):
                    purl = 'http://qyxy.baic.gov.cn/gjjbjTab/gjjbjTab/gjjTabQueryCreditAction!dcdyFrame.dhtml'
                    params = dict(clear='', entId=self.entId, pageNo=p-1, pageNos=p, pageSize=10)
                    try:
                        r = self.post_request(url=purl, params=params)
                    except:
                        self.info(u'internal error')
                        continue
                    # print '2nd',r.text
                    soup = BeautifulSoup(r.text, 'lxml')

                    tr_element_list = soup.find(class_="detailsList").find_all('tr')
                    for tr_element in tr_element_list[2:-1]:
                        td_element_list = tr_element.find_all('td')
                        col_nums = len(th_element_list)
                        for j in range(col_nums):
                            col_dec = th_element_list[j].text.strip().replace('\n','')
                            col = dongchandiyadengji_column_dict[col_dec]
                            td = td_element_list[j]
                            val = td.text.strip()
                            if val == u'详情':
                                link = re.findall("'(.*)'", td.a.get('onclick'))[0]
                                link = self.domain + link
                                detail_dict = self.get_dongchandiya_detail(link)
                                values[col] = detail_dict
                                # print 'dcdy_link', link
                                # self.get_dongchandiya_detail(link)
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
                self.json_result[family] = json_list
            # print '-,-**dongchandiya_json_list',len(json_list),json_list
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


    def get_gu_quan_chu_zhi(self):
        """
        查询股权出质信息
        :param param_pripid:
        :param param_type:
        :return:
        """
        family = 'Equity_Pledge'
        table_id = '12'
        # self.json_result[family] = []
        json_list = []
        values = {}
        # url = 'http://qyxy.baic.gov.cn/gdczdj/gdczdjAction!gdczdjFrame.dhtml'
        url = 'http://bj.gsxt.gov.cn/gdczdj/gdczdjAction!gdczdjFrame.dhtml?entId=%s&clear=true&urltag=13&credit_ticket=%s' %(self.entId, self.creditt)
        # print 'gudongchuzhi_url',self.cur_time,url
        # print 'gqcz***', self.tab_url_set
        # if url not in self.tab_url_set:
        #     return
        # params = {
        #     'entId': self.entId,
        #     'clear': 'true',
        # }
        r = self.get_request(url=url, params={})
        # r.encoding = 'gbk'
        soup = BeautifulSoup(r.text, 'html5lib')
        # print '*******guquanchuzhi*******', soup
        # return
        self.gqczbg_list = []
        self.gqczzx_list = []

        table_element = soup.find(class_="table-result")
        try:
            row_cnt = len(soup.find(class_="table-result").find_all('tr'))
        except AttributeError:
            return
        # print 'gqcz', row_cnt
        if row_cnt >= 2 and u'暂无' not in soup.find(class_="table-result").text:

            try:
                turn_page_text = soup.find(class_='pages').contents[0]
                # print 'turn_page_text', turn_page_text
                turn_page = re.search(u'(?<=共)[^共]*?(?=页)', turn_page_text).group()
                # turn_page = re.search(u'(?<=共)\d*?(?=页)', turn_page_text).group()
                turn_page = int(turn_page)
                # print 'turn_page', turn_page
            except:
                # print u'gqcz无分页'
                turn_page = 1

            tr_element_list = soup.find(class_="table-result").find_all('tr')
            th_element_list = soup.find(class_="table-result").find_all('tr')[0].find_all('th')
            idn = 1
            for tr_element in tr_element_list[1:]:
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
                        link = td.a.get('onclick')
                        link = re.search(u"(?<=').*(?=')", link).group()
                        link = self.domain + link
                        detail_dict=self.get_gu_quan_chu_zhi_detail(link)
                        values[col] = detail_dict
                        # print 'gqcz_link', link
                        # self.get_guquanchuzhi_detail(link)
                    else:
                        values[col]=val
                # values['RegistrationNo']=self.cur_code
                # values['EnterpriseName']=self.org_name
                # values['rowkey'] = values['EnterpriseName']+'_12_'+ values['RegistrationNo']+'_'+str(id)
                values['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.cur_zch, self.today, idn)
                values[family + ':registrationno'] = self.cur_zch
                values[family + ':enterprisename'] = self.cur_mc
                values[family + ':id'] = str(idn)
                json_list.append(values)
                # json_guquanchuzhidengji=json.dumps(values,ensure_ascii=False)
                # print 'json_guquanchuzhidengji', json_guquanchuzhidengji
                values = {}
                idn += 1

            if turn_page > 1:
                for p in range(2, turn_page+1):
                    # print '***',turn_page,'p',p
                    url = 'http://bj.gsxt.gov.cn/gdczdj/gdczdjAction!gdczdjFrame.dhtml?clear=true&entId='+self.entId+'&credit_ticket='+self.creditt
                    params = {'ent_id': '', 'pageNo': p-1, 'pageNos': p, 'pageSize': 5}
                    r = self.post_request(url=url, params=params)
                    soup = BeautifulSoup(r.text, 'html5lib')
                    # print 'subpage-gqcz', soup

                    tr_element_list = soup.find(class_="table-result").find_all('tr')
                    # th_element_list = soup.find(class_="table-result").find_all('tr')[0].find_all('th')
                    for tr_element in tr_element_list[1:]:
                        td_element_list = tr_element.find_all('td')
                        col_nums = len(th_element_list)
                        for j in range(col_nums):
                            col_dec = th_element_list[j].text.strip().replace('\n','')
                            # print 'col_dec',j,col_dec
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
                                link = td.a.get('onclick')
                                link = re.search(u"(?<=').*(?=')", link).group()
                                link = self.domain + link
                                detail_dict = self.get_gu_quan_chu_zhi_detail(link)
                                values[col] = detail_dict
                                # print 'gqcz_link', link
                                # self.get_guquanchuzhi_detail(link)
                            else:
                                values[col]=val
                        # values['RegistrationNo']=self.cur_code
                        # values['EnterpriseName']=self.org_name
                        # values['rowkey'] = values['EnterpriseName']+'_12_'+ values['RegistrationNo']+'_'+str(id)
                        values['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.cur_zch, self.today, idn)
                        values[family + ':registrationno'] = self.cur_zch
                        values[family + ':enterprisename'] = self.cur_mc
                        values[family + ':id'] = str(idn)
                        json_list.append(values)
                        # json_guquanchuzhidengji=json.dumps(values,ensure_ascii=False)
                        # print 'json_guquanchuzhidengji', json_guquanchuzhidengji
                        values = {}
                        idn += 1

            if json_list:
                self.json_result[family] = json_list
            # print '-,-**guquanchuzhi_json_list**',len(json_list),json_list
            # if self.gqczbg_list:
            #     self.json_result['gqczbg'] = self.gqczbg_list
            # if self.gqczzx_list:
            #     self.json_result['gqczzx'] = self.gqczzx_list

    def get_gu_quan_chu_zhi_detail(self,link):

        r = self.get_request(url=link, params={})
        soup = BeautifulSoup(r.text, 'html5lib')
        title=soup.find_all('h1')[1].text.strip()
        values={}

        th_element_list = soup.find_all('tr')
        if title=='股权出质注销信息':
            values[title] = {}
            for one_row in th_element_list:
                col=one_row.find('th').text.strip()
                val=one_row.find('td').text.strip()
                values[title][col]=val
        elif title=='股权出质变更信息':
            title_list=th_element_list[0].find_all('th')
            values[title] = []
            if len(th_element_list)==1:
                pass
            elif len(th_element_list)>1:
                tr_list = th_element_list[1:]
                for tre in tr_list:
                    one_col = {}
                    col_num = len(title_list)
                    td_list = tre.find_all('td')
                    for i in range(col_num):
                        col = title_list[i].text.strip()
                        val = td_list[i].text.strip()
                        # print u'γγ', col, val
                        one_col[col] = val
                    values[title].append(one_col)

        return values

    def get_xing_zheng_chu_fa(self):
        """
        查询行政处罚信息
        :param param_pripid:
        :param param_type:
        :return:
        """
        family = 'Administrative_Penalty'
        table_id = '13'
        # self.json_result[family] = []
        values = {}
        json_list = []

        url = ''
        # print 'xingzhengchufa', self.tab_url_set
        for ur in self.tab_url_set:
            if u'http://bj.gsxt.gov.cn/gdgq/gdgqAction!xj_qyxzcfFrame.dhtml' in ur:
                url = ur
        if not url:
            print 'sssss555555555555'
            return
        # print 'xingzhengchufai_url',self.cur_time,url

        r = self.get_request(url=url, params={})
        # r.encoding = 'gbk'
        soup = BeautifulSoup(r.text, 'html5lib')
        # print '*******xingzhengchufa*******', soup

        try:
            turn_page_text = soup.find(class_='pages').contents[0]
            # print 'turn_page_text', turn_page_text
            turn_page = re.search(u'(?<=共)[^共]*?(?=页)', turn_page_text).group()
            # turn_page = re.search(u'(?<=共)\d*?(?=页)', turn_page_text).group()
            turn_page = int(turn_page)
            # print 'turn_page', turn_page
        except:
            # print u'无分页'
            turn_page = 1

        row_cnt = len(soup.find(class_="table-result").find_all('tr'))
        if row_cnt >= 2 and u'暂无' not in soup.find(class_="table-result").text:
            tr_element_list = soup.find(class_="table-result").find_all('tr')
            th_element_list = soup.find(class_="table-result").find_all('tr')[0].find_all('th')
            idn = 1
            for tr_element in tr_element_list[1:]:
                td_element_list = tr_element.find_all('td')
                col_nums = len(th_element_list)
                for j in range(col_nums):
                    col_dec = th_element_list[j].text.strip().replace('\n','')
                    col=xingzhengchufa_column_dict[col_dec]
                    td = td_element_list[j]
                    val = td.text.strip()
                    if val == u'查看':
                        val = self.domain+td.a.get('href')
                        # print 'xingzhengchufa_details', val
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

            if turn_page>1:
                for p in range(1, turn_page):
                    # url = 'http://qyxy.baic.gov.cn/gsgs/gsxzcfAction!list.dhtml?entId='+self.entId
                    # url = 'http://bj.gsxt.gov.cn/gdgq/gdgqAction!xj_qyxzcfFrame.dhtml?entId=948C13E290484EF4BA1CB9C8DA516145&regno=110105003319557&uniscid=911101057263777049&clear=true&urltag=14'
                    # params = {'clear':'','pageNo':p+1,'pageSize':10}
                    params = {'pageNo': p, 'pageNos': p+1, 'pageSize': 5, 'urltag': 14}
                    r = self.post_request(url=url, params=params)
                    soup = BeautifulSoup(r.text,'html5lib')
                    # print '2p',p, soup
                    tr_element_list = soup.find(class_="table-result").find_all('tr')
                    # th_element_list = soup.find(class_="detailsList").find_all('tr')[1].find_all('th')

                    for tr_element in tr_element_list[1:]:
                        td_element_list = tr_element.find_all('td')
                        col_nums = len(th_element_list)
                        for j in range(col_nums):
                            col_dec = th_element_list[j].text.strip().replace('\n','')
                            col=xingzhengchufa_column_dict[col_dec]
                            td = td_element_list[j]
                            val = td.text.strip()
                            if val == u'查看':
                                val = self.domain+td.a.get('href')
                                # print 'xzcf_details_link', val
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
            print json_list
            if json_list:
                self.json_result[family] = json_list
            # print '-,-**xingzhengchufa_jsonlist***', len(json_list), json_list

    def get_jing_ying_yi_chang(self):
        """
        查询经营异常信息
        :param param_pripid:
        :param param_type:
        :return:
        """
        family = 'Business_Abnormal'
        table_id = '14'
        # self.json_result[family] = []
        values = {}
        json_list = []
        # url = 'http://qyxy.baic.gov.cn/gsgs/gsxzcfAction!list_jyycxx.dhtml'
        url = 'http://bj.gsxt.gov.cn/gsgs/gsxzcfAction!list_jyycxx.dhtml?entId=%s&clear=true&urltag=8' % self.entId
        # print 'jingyingyichang_url',self.cur_time,url
        # if url not in self.tab_url_set:
        #     return
        # params = {
        #     'entId': self.entId,
        #     'clear': 'true',
        #     'timeStamp': get_cur_ts_mil()
        # }
        r = self.get_request(url=url, params={})
        # r.encoding = 'gbk'
        soup = BeautifulSoup(r.text, 'html5lib')
        # print '*******jingyingyichang*******', soup
        try:
            row_cnt = len(soup.find(class_="table-result").find_all('tr'))
        except AttributeError:
            return
        if row_cnt >= 2 and u'暂无' not in soup.find(class_="table-result").text:
            idn = 1
            tr_element_list = soup.find(class_="table-result").find_all('tr')
            th_element_list = soup.find(class_="table-result").find_all('tr')[0].find_all('th')
            for tr_element in tr_element_list[1:]:
                td_element_list = tr_element.find_all('td')
                col_nums = len(th_element_list)
                for j in range(col_nums):
                    col_dec = th_element_list[j].text.strip().replace('\n','')
                    # print 'col_dec',col_dec
                    col=jingyingyichang_column_dict[col_dec]
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
            if json_list:
                self.json_result[family] = json_list
            # print '-,-**jingyingyichang',json_list

        # params = {'pripid': param_pripid, 'type': param_type}
        # result_json = self.get_result_json(url, params)
        # for j in result_json:
        #     self.json_result[family].append({})
        #     for k in j:
        #         if k in jing_ying_yi_chang_dict:
        #             col = family + ':' + jing_ying_yi_chang_dict[k]
        #             val = j[k]
        #             self.json_result[family][-1][col] = val
        # for i in range(len(self.json_result[family])):
        #     self.json_result[family][i]['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.cur_zch, self.today, i)
        #     self.json_result[family][i][family + ':registrationno'] = self.cur_zch
        #     self.json_result[family][i][family + ':enterprisename'] = self.cur_mc
        # print json.dumps(result_json_2, ensure_ascii=False)

    def get_yan_zhong_wei_fa(self):
        """
        查询严重违法信息
        :param param_pripid:
        :param param_type:
        :return:
        """
        family = 'Serious_Violations'
        table_id = '15'
        # self.json_result[family] = []
        values = {}
        json_list = []
        # url = 'http://qyxy.baic.gov.cn/gsgs/gsxzcfAction!list_yzwfxx.dhtml'
        url = 'http://bj.gsxt.gov.cn/gsgs/gsxzcfAction!list_yzwfxx.dhtml?ent_id=%s&clear=true&urltag=9' % self.entId
        # if url not in self.tab_url_set:
        #     return
        # params = {
        #     'ent_id': self.entId,
        #     'clear': 'true',
        # }
        # print 'yanzhongweifa_url',self.cur_time,url
        r = self.get_request(url=url, params={})
        # r.encoding = 'gbk'
        soup = BeautifulSoup(r.text, 'html5lib')
        # print '*******yanzhongweifa*******',soup
        try:
            row_cnt = len(soup.find(class_="table-result").find_all('tr'))
        except AttributeError:
            return
        if row_cnt >= 2 and u'暂无' not in soup.find(class_="table-result").text:
            tr_element_list = soup.find(class_="table-result").find_all('tr')
            th_element_list = soup.find(class_="table-result").find_all('tr')[0].find_all('th')
            idn = 1
            for tr_element in tr_element_list[1:]:
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
            if json_list:
                self.json_result[family] = json_list
            # print '-,-**yanzhongweifa_json_list', len(json_list), json_list

    def get_chou_cha_jian_cha(self):
        """
        查询抽查检查信息
        :param param_pripid:
        :param param_type:
        :return:
        """
        family = 'Spot_Check'
        table_id = '16'
        # self.json_result[family] = []
        values = {}
        json_list = []
        # url = 'http://qyxy.baic.gov.cn/gsgs/gsxzcfAction!list_ccjcxx.dhtml'
        url = 'http://bj.gsxt.gov.cn/gsgs/gsxzcfAction!list_ccjcxx.dhtml?ent_id=%s&clear=true&urltag=10&credit_ticket=%s' %(self.entId, self.creditt)
        # print 'chouchajiancha_url',self.cur_time,url
        # if url not in self.tab_url_set:
        #     return
        # params = {
        #     'ent_id': self.entId,
        #     'clear': 'true',
        #     'entName': '',
        # }
        r = self.get_request(url=url, params={})
        # r.encoding = 'gbk'
        soup = BeautifulSoup(r.text, 'html5lib')
        # print '*******chouchajiancha*******', soup

        # row_cnt = len(soup.find_all('tbody'))  #结构和之前稍微不一样，不是tr，是3个tbody
        try:
            row_cnt = len(soup.find_all('tbody')[-1].find_all('tr'))
        except AttributeError:
            return
        # print 'ccjc_row_cnt',row_cnt

        if row_cnt >1 and u'暂无' not in soup.find(class_="table-result").text:
            # print '*****mmmm****'
            tr_element_list = soup.find_all('tbody')[1].find_all('tr')
            th_element_list = soup.find(id="tableChoucha").find_all('th')
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
            if json_list:
                self.json_result[family] = json_list
            # print '-,-**chouchajiancha', len(json_list), json_list

    def get_nian_bao(self):

        family = 'annual_report'
        table_id = '39'

        url = 'http://qyxy.baic.gov.cn/qynb/entinfoAction!qyxx.dhtml?entid='+self.entId+'&clear=true&timeStamp='+self.cur_time
        # print 'nianbaourl:', url
        self.get_lock_id()
        r = self.get_request(url=url)
        r.encoding = 'utf-8'
        soup = BeautifulSoup(r.text, 'lxml')
        # print 'nianbao*soup:', soup
        nblist = soup.find(id='qiyenianbao').find_all('tr')
        json_list = []
        json_dict = {}
        link_list = []
        year_list = []
        cid_dict = {}
        if len(nblist) > 2:
            th_list = nblist[1].find_all('th')
            tr_list = nblist[2:]
            tr_recent = nblist[-1]

            for tr in tr_list:
                idn = 1
                if tr.text.strip():
                    td_list = tr.find_all('td')
                    for t in range(len(td_list)):
                        col_dec = th_list[t].text.strip()
                        col = qiyenianbao_column_dict[col_dec]
                        td = td_list[t].text.strip()
                        if col_dec == u'报送年度':
                            try:
                                href = td_list[t].a.get('href')
                            except AttributeError as e:
                                # print u'个体户年报不做处理', e
                                self.info(u'个体户年报不做处理')
                                return
                            link = 'http://qyxy.baic.gov.cn' + href
                            # print 'nianbao_link:', td, link
                            self.y = td[:4]
                            cid = re.search(r'(?<=cid=).*(?=&entid)', link).group()
                            # print '***cid***:', cid
                            cid_dict[td] = cid
                            year_list.append(td)
                            link_list.append(link)
                            json_dict[qiyenianbao_column_dict[u'详情']] = link
                        json_dict[col] = td
                    json_dict['rowkey'] = '%s_%s_%s_%d' %(self.cur_mc, self.y, table_id, idn)
                    json_dict[family + ':registrationno'] = self.cur_zch
                    json_dict[family + ':enterprisename'] = self.cur_mc
                    json_dict[family + ':id'] = str(idn)
                    json_list.append(json_dict)
                    json_dict = {}
                    idn += 1
            if json_list:
                # print 'json_list:', json_list
                self.json_result[family] = json_list

        # 年报详情解析
            if link_list:
                # print 'link_list:', link_list
                # 年报年份
                cnt = 0
                iyear_dict = {}  # 年份容器
                idata_dict = {}  # 年份数据容器

                self.nbjb_list = []  # 年报基本信息
                self.nbzczk_list = []  # 年报资产状况

                self.nbdwdb_list = []
                self.nbgdcz_list = []
                self.nbgqbg_list = []
                self.nbwz_list = []
                self.nbxg_list = []
                self.nbdwtz_list = []

                # 此部分需要锁定IP
                for l in link_list:
                    # print 'refer-link:', url
                    r = self.get_request(url=l)  #包含基本信息和企业资产状况信息
                    r.encoding = 'utf-8'
                    soup = BeautifulSoup(r.text, 'lxml')
                    # print '****-nianbaodetail--soup-****', soup
                    no_iframe = soup.find_all(id='qufenkuang')[0]#.find_all(class_='detailsList')
                    yes_iframe = soup.find_all('iframe')
                    # print '*'*100
                    self.info(u'获取年报基本信息**'+year_list[cnt])
                    self.get_nianbaojiben(no_iframe)  # 获取年报基本信息
                    self.info(u'获取年报资产状况信息**'+year_list[cnt])
                    self.get_nianbaozichanzhuangkuang(no_iframe)  # 获取年报资产状况信息
                    # print '*'*150

                    for i in range(len(yes_iframe)):
                        yes_id = yes_iframe[i].get('id')
                        yes_src = yes_iframe[i].get('src')
                        yes_link = self.domain + yes_src
                        # print '*'*50, i, year_list[cnt], yes_id, yes_src, yes_link
                        idata_dict[yes_id] = yes_link
                    iyear_dict[year_list[cnt]] = idata_dict
                    idata_dict = {}
                    cnt += 1

                # print '***---***', iyear_dict
                # 对不用锁定IP的iframe进行单独处理
                for y, d in iyear_dict.items():
                    # print 'show_me_the_data:', y, d  # y为年份，d为年份对应的iframe的id和url
                    self.y = y[:4]
                    self.cid = cid_dict[y]
                    for lid, lurl in d.items():
                        # print '*-'*50, lid, lurl

                        if lid == 'dwdbFrame':
                            # print u'对外提供保证担保信息', y
                            self.info(u'对外提供保证担保信息**' + y)
                            self.get_nianbaoduiwaidanbao(lurl)
                        elif lid == 'gdczFrame':
                            # print u'股东及出资信息', y
                            self.info(u'股东及出资信息**' + y)
                            self.get_nianbaogudongchuzi(lurl)
                        elif lid == 'gdzrFrame':
                            # print u'股权变更信息', y
                            self.info(u'股权变更信息**' + y)
                            self.get_nianbaoguquanbiangeng(lurl)
                        elif lid == 'wzFrame':
                            # print u'网站或网店信息', y
                            self.info(u'网站或网店信息**' + y)
                            self.get_nianbaowangzhan(lurl)
                        elif lid == 'xgFrame':
                            # print u'修改记录', y
                            self.info(u'修改记录**' + y)
                            self.get_nianbaoxiugai(lurl)
                        elif lid == 'dwtzFrame':
                            # print u'对外投资信息', y
                            self.info(u'对外投资信息**' + y)
                            self.get_nianbaoduiwaitouzi(lurl)
                        else:
                            # print '******$$$**unknown_iframe***', lid, lurl
                            self.info(u'******$$$**unknown_iframe***iframeID:' + lid + u'iframeURL:' + lurl)
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


                    # for j in no_iframe:
                    #     print '******soup_basic:', j
                    # iframes = soup.find_all(id='qufenkuang')[0].find_all('iframe')
                    # for j in iframes:
                    #     print '))))))iframe_show:', j

#  基本页面加载成功包含基本信息和企业资产状况信息,网站结构为table，锁IP
    def get_nianbaojiben(self, soup):
        family = 'report_base'
        table_id = '40'
        table = soup.find_all(class_='detailsList')[0]
        tr_element_list = table.find_all("tr")
        values = {}
        json_list = []
        for tr_element in tr_element_list[2:]:
            th_element_list = tr_element.find_all('th')
            td_element_list = tr_element.find_all('td')
            if len(th_element_list) == len(td_element_list):
                col_nums = len(th_element_list)
                for i in range(col_nums):
                    col = th_element_list[i].get_text().strip().replace('\n','')
                    val = td_element_list[i].get_text().strip().replace('\n','')
                    if col != u'':
                        values[qiyenianbaojiben_column_dict[col]] = val
                        # print col,val
        values['rowkey'] = '%s_%s_%s_' %(self.cur_mc, self.y, table_id)
        values[family + ':registrationno'] = self.cur_zch
        values[family + ':enterprisename'] = self.cur_mc
        json_list.append(values)
        self.nbjb_list.append(values)
        # if json_list:
        #     # print 'nianbaojibenxinxi', json_list
        #     self.json_result[family] = json_list

    def get_nianbaozichanzhuangkuang(self, soup):
        family = 'industry_status'
        table_id = '43'

        table = soup.find_all(class_='detailsList')[1]
        tr_element_list = table.find_all("tr")
        values = {}
        json_list = []
        for tr_element in tr_element_list:
            th_element_list = tr_element.find_all('th')
            td_element_list = tr_element.find_all('td')
            if len(th_element_list) == len(td_element_list):
                col_nums = len(th_element_list)
                for i in range(col_nums):
                    col = th_element_list[i].get_text().strip().replace('\n','')
                    val = td_element_list[i].get_text().strip().replace('\n','')
                    if col != u'':
                        values[qiyenianbaozichanzhuangkuang_column_dict[col]] = val
#                     print col,val
#         values[u'注册号']=self.cur_code
#         values[u'省份']=self.province
#         values[u'报送年度']=self.nianbaotitle
        values['rowkey'] = '%s_%s_%s_' %(self.cur_mc, self.y, table_id)
        values[family + ':registrationno'] = self.cur_zch
        values[family + ':enterprisename'] = self.cur_mc
        json_list.append(values)
        self.nbzczk_list.append(values)
        # if json_list:
            # json_nianbaozichan=json.dumps(values,ensure_ascii=False)
            # print 'json_nianbaozichan', json_list
            # self.json_result[family] = json_list

    def get_nianbaoduiwaidanbao(self, url):
        family = 'guarantee'
        table_id = '44'
        values = {}
        json_list = []
        r = self.get_request(url=url)
        r.encoding = 'utf-8'
        soup = BeautifulSoup(r.text, 'lxml')
        # print 'nianbaoduiwaidanbao', soup

        sp = soup.find(id='touziren').find_all('tr')
        # print 'lendwdbsp', len(sp)
        if len(sp) > 3:
            idn = 1
            tr_element_list = sp
            th_element_list = sp[1].find_all('th')
            for tr_element in tr_element_list[2:-1]:
                td_element_list = tr_element.find_all('td')
                col_nums = len(th_element_list)
                for j in range(col_nums):
                    col = th_element_list[j].text.strip().replace('\n','')
                    td = td_element_list[j]
                    val = td.text.strip()
                    values[qiyenianbaoduiwaidanbao_column_dict[col]] = val
                # values[u'注册号']=self.cur_code
                # values[u'省份']=self.province
                # values[u'报送年度']=self.nianbaotitle
                values['rowkey'] = '%s_%s_%s_%d' %(self.cur_mc, self.y, table_id, idn)
                values[family + ':registrationno'] = self.cur_zch
                values[family + ':enterprisename'] = self.cur_mc
                values[family + ':id'] = str(idn)
                json_list.append(values)
                self.nbdwdb_list.append(values)
                values = {}
                # print 'dwdb****'
                idn += 1

            page_tr = sp[-1].find_all('a')
            if page_tr:
                ncnt = len(page_tr)
                if ncnt > 3:
                    # print u'股东出资分页抓取'
                    for p in range(1, ncnt-1):
                        # url = 'http://qyxy.baic.gov.cn/entPub/entPubAction!dwtz_bj.dhtml'
                        url = 'http://qyxy.baic.gov.cn/entPub/entPubAction!qydwdb_bj.dhtml'
                        params = {
                            'cid': self.cid,
                            'clear': '',
                            'entid': '',
                            'pageNo': p,
                            'pageNos': p+1,
                            'pageSize': 5
                        }
                        # print 'params:', params
                        r = self.post_request(url=url, data=params)
                        r.encoding = 'utf-8'
                        soup = BeautifulSoup(r.text, 'lxml')
                        # print '***dwtzfenye***', p+1,
                        sp = soup.find(id='touziren').find_all('tr')
                        tr_element_list = sp
                        th_element_list = sp[1].find_all('th')
                        for tr_element in tr_element_list[2:-1]:
                            td_element_list = tr_element.find_all('td')
                            col_nums = len(th_element_list)
                            for j in range(col_nums):
                                col = th_element_list[j].text.strip().replace('\n','')
                                td = td_element_list[j]
                                val = td.text.strip()
                                # print 'dwdb', p+1, idn, val
                                values[qiyenianbaoduiwaidanbao_column_dict[col]] = val
                            # values[u'注册号']=self.cur_code
                            # values[u'省份']=self.province
                            # values[u'报送年度']=self.nianbaotitle
                            # values['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.cur_zch, self.today, idn)
                            values['rowkey'] = '%s_%s_%s_%d' %(self.cur_mc, self.y, table_id, idn)
                            values[family + ':registrationno'] = self.cur_zch
                            values[family + ':enterprisename'] = self.cur_mc
                            values[family + ':id'] = str(idn)
                            json_list.append(values)
                            self.nbdwdb_list.append(values)
                            values = {}
                            idn += 1
            # if json_list:
            #     # print 'nianbaoduiwandanbao:', json_list
            #     self.json_result[family] = json_list

    def get_nianbaogudongchuzi(self, url):
        family = 'enterprise_shareholder'
        table_id = '42'
        values = {}
        json_list = []
        r = self.get_request(url=url)
        r.encoding = 'utf-8'
        soup = BeautifulSoup(r.text, 'lxml')
        # print 'nianbaogudongchuzisoup', soup

        sp = soup.find(id='touziren').find_all('tr')
        # print 'lengdczsp', len(sp)
        if len(sp) > 3:
            idn = 1
            tr_element_list = sp
            th_element_list = sp[1].find_all('th')
            for tr_element in tr_element_list[2:-1]:
                td_element_list = tr_element.find_all('td')
                col_nums = len(th_element_list)
                for j in range(col_nums):
                    col = th_element_list[j].text.strip().replace('\n','')
                    td = td_element_list[j]
                    val = td.text.strip()
                    values[qiyenianbaogudong_column_dict[col]] = val
                values['rowkey'] = '%s_%s_%s_%d' %(self.cur_mc, self.y, table_id, idn)
                values[family + ':registrationno'] = self.cur_zch
                values[family + ':enterprisename'] = self.cur_mc
                values[family + ':id'] = str(idn)
                json_list.append(values)
                self.nbgdcz_list.append(values)
                values = {}
                # print 'wzwz****'
                idn += 1

            page_tr = sp[-1].find_all('a')
            if page_tr:
                ncnt = len(page_tr)
                if ncnt > 3:
                    # print u'股东出资分页抓取'
                    for p in range(1, ncnt-1):
                        # url = 'http://qyxy.baic.gov.cn/entPub/entPubAction!dwtz_bj.dhtml'
                        url = 'http://qyxy.baic.gov.cn/entPub/entPubAction!gdcz_bj.dhtml'
                        params = {
                            'cid': self.cid,
                            'clear': '',
                            'entid': '',
                            'pageNo': p,
                            'pageNos': p+1,
                            'pageSize': 5
                        }
                        # print 'params:', params
                        r = self.post_request(url=url, params=params)
                        r.encoding = 'utf-8'
                        soup = BeautifulSoup(r.text, 'lxml')
                        # print '***dwtzfenye***', p+1,
                        sp = soup.find(id='touziren').find_all('tr')
                        tr_element_list = sp
                        th_element_list = sp[1].find_all('th')
                        for tr_element in tr_element_list[2:-1]:
                            td_element_list = tr_element.find_all('td')
                            col_nums = len(th_element_list)
                            for j in range(col_nums):
                                col = th_element_list[j].text.strip().replace('\n','')
                                td = td_element_list[j]
                                val = td.text.strip()
                                # print 'gdcz', p+1, idn, val
                                values[qiyenianbaogudong_column_dict[col]] = val
                            # values[u'注册号']=self.cur_code
                            # values[u'省份']=self.province
                            # values[u'报送年度']=self.nianbaotitle
                            # values['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.cur_zch, self.today, idn)
                            values['rowkey'] = '%s_%s_%s_%d' %(self.cur_mc, self.y, table_id, idn)
                            values[family + ':registrationno'] = self.cur_zch
                            values[family + ':enterprisename'] = self.cur_mc
                            values[family + ':id'] = str(idn)
                            json_list.append(values)
                            self.nbgdcz_list.append(values)
                            values = {}
                            idn += 1

            # if json_list:
            #     # print 'nianbaogudongchuzi:', json_list
            #     self.json_result[family] = json_list

    def get_nianbaoguquanbiangeng(self, url):
        family = 'equity_transfer'
        table_id = '45'
        values = {}
        json_list = []
        r = self.get_request(url=url)
        r.encoding = 'utf-8'
        soup = BeautifulSoup(r.text, 'lxml')
        # print 'nianbaoguquanbiangeng', soup

        sp = soup.find(id='touziren').find_all('tr')
        # print 'lengqbgsp', len(sp)
        if len(sp) > 3:
            idn = 1
            tr_element_list = sp
            th_element_list = sp[1].find_all('th')
            for tr_element in tr_element_list[2:-1]:
                td_element_list = tr_element.find_all('td')
                col_nums = len(th_element_list)
                for j in range(col_nums):
                    col = th_element_list[j].text.strip().replace('\n','')
                    td = td_element_list[j]
                    val = td.text.strip()
                    values[qiyenianbaoguquanbiangeng_column_dict[col]] = val
                values['rowkey'] = '%s_%s_%s_%d' %(self.cur_mc, self.y, table_id, idn)
                values[family + ':registrationno'] = self.cur_zch
                values[family + ':enterprisename'] = self.cur_mc
                values[family + ':id'] = str(idn)
                json_list.append(values)
                self.nbgqbg_list.append(values)
                values = {}
                # print 'wzwz****'
                idn += 1

            page_tr = sp[-1].find_all('a')
            if page_tr:
                ncnt = len(page_tr)
                if ncnt > 3:
                    # print u'股权变更分页抓取'
                    for p in range(1, ncnt-1):
                        # url = 'http://qyxy.baic.gov.cn/entPub/entPubAction!dwtz_bj.dhtml'
                        url = 'http://qyxy.baic.gov.cn/entPub/entPubAction!gdzr_bj.dhtml'
                        params = {
                            'cid': self.cid,
                            'clear': '',
                            'entid': '',
                            'pageNo': p,
                            'pageNos': p+1,
                            'pageSize': 5
                        }
                        # print 'params:', params
                        r = self.post_request(url=url, data=params)
                        r.encoding = 'utf-8'
                        soup = BeautifulSoup(r.text, 'lxml')
                        # print '***dwtzfenye***', p+1,
                        sp = soup.find(id='touziren').find_all('tr')
                        tr_element_list = sp
                        th_element_list = sp[1].find_all('th')
                        for tr_element in tr_element_list[2:-1]:
                            td_element_list = tr_element.find_all('td')
                            col_nums = len(th_element_list)
                            for j in range(col_nums):
                                col = th_element_list[j].text.strip().replace('\n','')
                                td = td_element_list[j]
                                val = td.text.strip()
                                # print 'gqbg', p+1, idn, val
                                values[qiyenianbaoguquanbiangeng_column_dict[col]] = val
                            # values[u'注册号']=self.cur_code
                            # values[u'省份']=self.province
                            # values[u'报送年度']=self.nianbaotitle
                            # values['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.cur_zch, self.today, idn)
                            values['rowkey'] = '%s_%s_%s_%d' %(self.cur_mc, self.y, table_id, idn)
                            values[family + ':registrationno'] = self.cur_zch
                            values[family + ':enterprisename'] = self.cur_mc
                            values[family + ':id'] = str(idn)
                            json_list.append(values)
                            self.nbgqbg_list.append(values)
                            values = {}
                            idn += 1

            # if json_list:
            #     # print 'nianbaoguquanbiangeng:', json_list
            #     self.json_result[family] = json_list

    def get_nianbaowangzhan(self, url):
        family = 'web_site'
        table_id = '41'
        values = {}
        json_list = []
        r = self.get_request(url=url)
        r.encoding = 'utf-8'
        soup = BeautifulSoup(r.text, 'lxml')
        # print 'nianbaowangzhansoup', soup

        sp = soup.find(id='touziren').find_all('tr')
        # print 'lenwzsp', len(sp)
        if len(sp) > 3:
            idn = 1
            tr_element_list = sp
            th_element_list = sp[1].find_all('th')
            for tr_element in tr_element_list[2:-1]:
                td_element_list = tr_element.find_all('td')
                col_nums = len(th_element_list)
                for j in range(col_nums):
                    col = th_element_list[j].text.strip().replace('\n','')
                    td = td_element_list[j]
                    val = td.text.strip()
                    values[qiyenianbaowangzhan_column_dict[col]] = val
                values['rowkey'] = '%s_%s_%s_%d' %(self.cur_mc, self.y, table_id, idn)
                values[family + ':registrationno'] = self.cur_zch
                values[family + ':enterprisename'] = self.cur_mc
                values[family + ':id'] = str(idn)
                json_list.append(values)
                self.nbwz_list.append(values)
                values = {}
                idn += 1
                # print 'wzwz****'

            page_tr = sp[-1].find_all('a')
            if page_tr:
                ncnt = len(page_tr)
                if ncnt > 3:
                    # print u'网站或网店分页抓取'
                    for p in range(1, ncnt-1):
                        # url = 'http://qyxy.baic.gov.cn/entPub/entPubAction!dwtz_bj.dhtml'
                        url = 'http://qyxy.baic.gov.cn//entPub/entPubAction!wz_bj.dhtml'
                        params = {
                            'cid': self.cid,
                            'clear': '',
                            'entid': '',
                            'pageNo': p,
                            'pageNos': p+1,
                            'pageSize': 5
                        }
                        # print 'params:', params
                        r = self.post_request(url=url, data=params)
                        r.encoding = 'utf-8'
                        soup = BeautifulSoup(r.text, 'lxml')
                        # print '***dwtzfenye***', p+1,
                        sp = soup.find(id='touziren').find_all('tr')
                        tr_element_list = sp
                        th_element_list = sp[1].find_all('th')
                        for tr_element in tr_element_list[2:-1]:
                            td_element_list = tr_element.find_all('td')
                            col_nums = len(th_element_list)
                            for j in range(col_nums):
                                col = th_element_list[j].text.strip().replace('\n','')
                                td = td_element_list[j]
                                val = td.text.strip()
                                # print 'wz', p+1, idn, val
                                values[qiyenianbaowangzhan_column_dict[col]] = val
                            # values[u'注册号']=self.cur_code
                            # values[u'省份']=self.province
                            # values[u'报送年度']=self.nianbaotitle
                            # values['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.cur_zch, self.today, idn)
                            values['rowkey'] = '%s_%s_%s_%d' %(self.cur_mc, self.y, table_id, idn)
                            values[family + ':registrationno'] = self.cur_zch
                            values[family + ':enterprisename'] = self.cur_mc
                            values[family + ':id'] = str(idn)
                            json_list.append(values)
                            self.nbwz_list.append(values)
                            values = {}
                            idn += 1

            # if json_list:
            #     # print 'nianbaowangzhan:', json_list
            #     self.json_result[family] = json_list

    def get_nianbaoxiugai(self, url):
        family = 'modify'
        table_id = '46'
        values = {}
        json_list = []
        r = self.get_request(url=url)
        r.encoding = 'utf-8'
        soup = BeautifulSoup(r.text, 'lxml')
        # print 'nianbaowangzhansoup', soup

        sp = soup.find(id='touziren').find_all('tr')
        # print 'lenxgsp', len(sp)
        if len(sp) > 3:
            idn = 1
            tr_element_list = sp
            th_element_list = sp[1].find_all('th')
            for tr_element in tr_element_list[2:-1]:
                td_element_list = tr_element.find_all('td')
                col_nums = len(th_element_list)
                for j in range(col_nums):
                    col = th_element_list[j].text.strip().replace('\n','')
                    td = td_element_list[j]
                    val = td.text.strip()
                    values[qiyenianbaoxiugaijilu_column_dict[col]] = val
                values['rowkey'] = '%s_%s_%s_%d' %(self.cur_mc, self.y, table_id, idn)
                values[family + ':registrationno'] = self.cur_zch
                values[family + ':enterprisename'] = self.cur_mc
                values[family + ':id'] = str(idn)
                json_list.append(values)
                self.nbxg_list.append(values)
                values = {}
                idn += 1
                # print 'xg****'

            page_tr = sp[-1].find_all('a')
            if page_tr:
                ncnt = len(page_tr)
                if ncnt > 3:
                    # print u'修改分页抓取'
                    for p in range(1, ncnt-1):
                        # url = 'http://qyxy.baic.gov.cn/entPub/entPubAction!dwtz_bj.dhtml'
                        url = 'http://qyxy.baic.gov.cn/entPub/entPubAction!qybg_bj.dhtml'
                        params = {
                            'cid': self.cid,
                            'clear': '',
                            'entid': '',
                            'pageNo': p,
                            'pageNos': p+1,
                            'pageSize': 5
                        }
                        # print 'params:', params
                        r = self.post_request(url=url, data=params)
                        r.encoding = 'utf-8'
                        soup = BeautifulSoup(r.text, 'lxml')
                        # print '***dwtzfenye***', p+1,
                        sp = soup.find(id='touziren').find_all('tr')
                        tr_element_list = sp
                        th_element_list = sp[1].find_all('th')
                        for tr_element in tr_element_list[2:-1]:
                            td_element_list = tr_element.find_all('td')
                            col_nums = len(th_element_list)
                            for j in range(col_nums):
                                col = th_element_list[j].text.strip().replace('\n','')
                                td = td_element_list[j]
                                val = td.text.strip()
                                # print 'xg', p+1, idn, val
                                values[qiyenianbaoxiugaijilu_column_dict[col]] = val
                            # values[u'注册号']=self.cur_code
                            # values[u'省份']=self.province
                            # values[u'报送年度']=self.nianbaotitle
                            # values['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.cur_zch, self.today, idn)
                            values['rowkey'] = '%s_%s_%s_%d' %(self.cur_mc, self.y, table_id, idn)
                            values[family + ':registrationno'] = self.cur_zch
                            values[family + ':enterprisename'] = self.cur_mc
                            values[family + ':id'] = str(idn)
                            json_list.append(values)
                            self.nbxg_list.append(values)
                            values = {}
                            idn += 1
            # if json_list:
            #     # print 'nianbaoxiugai:', json_list
            #     self.json_result[family] = json_list

    def get_nianbaoduiwaitouzi(self, url):
        family = 'investment'
        table_id = '47'
        values = {}
        json_list = []
        r = self.get_request(url=url)
        r.encoding = 'utf-8'
        soup = BeautifulSoup(r.text, 'lxml')
        # print 'nianbaoduiwaitouzisoup', soup

        sp = soup.find(id='touziren').find_all('tr')
        # print 'lendwtzsp', len(sp)
        if len(sp) > 3:
            idn = 1
            tr_element_list = sp
            th_element_list = sp[1].find_all('th')
            for tr_element in tr_element_list[2:-1]:
                td_element_list = tr_element.find_all('td')
                col_nums = len(th_element_list)
                for j in range(col_nums):
                    col = th_element_list[j].text.strip().replace('\n','')
                    td = td_element_list[j]
                    val = td.text.strip()
                    values[qiyenianbaoduiwaitouzi_column_dict[col]] = val
                # values[u'注册号']=self.cur_code
                # values[u'省份']=self.province
                # values[u'报送年度']=self.nianbaotitle
                # json_list.append(values)
                # values['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.cur_zch, self.today, idn)
                values['rowkey'] = '%s_%s_%s_%d' %(self.cur_mc, self.y, table_id, idn)
                values[family + ':id'] = str(idn)
                json_list.append(values)
                self.nbdwtz_list.append(values)
                values = {}
                idn += 1
                # print 'wzwz****'

            page_tr = sp[-1].find_all('a')
            if page_tr:
                ncnt = len(page_tr)
                if ncnt > 3:
                    # print u'对外投资分页抓取'
                    for p in range(1, ncnt-1):
                        url = 'http://qyxy.baic.gov.cn/entPub/entPubAction!dwtz_bj.dhtml'
                        params = {
                            'cid': self.cid,
                            'clear': '',
                            'entid': '',
                            'pageNo': p,
                            'pageNos': p+1,
                            'pageSize': 5
                        }
                        # print 'params:', params
                        r = self.post_request(url=url, data=params)
                        r.encoding = 'utf-8'
                        soup = BeautifulSoup(r.text, 'lxml')
                        # print '***dwtzfenye***', p+1,
                        sp = soup.find(id='touziren').find_all('tr')
                        tr_element_list = sp
                        th_element_list = sp[1].find_all('th')
                        for tr_element in tr_element_list[2:-1]:
                            td_element_list = tr_element.find_all('td')
                            col_nums = len(th_element_list)
                            for j in range(col_nums):
                                col = th_element_list[j].text.strip().replace('\n','')
                                td = td_element_list[j]
                                val = td.text.strip()
                                # print 'dwtz', p+1, idn, val
                                values[qiyenianbaoduiwaitouzi_column_dict[col]] = val
                            # values[u'注册号']=self.cur_code
                            # values[u'省份']=self.province
                            # values[u'报送年度']=self.nianbaotitle
                            # values['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.cur_zch, self.today, idn)
                            values['rowkey'] = '%s_%s_%s_%d' %(self.cur_mc, self.y, table_id, idn)
                            values[family + ':registrationno'] = self.cur_zch
                            values[family + ':enterprisename'] = self.cur_mc
                            values[family + ':id'] = str(idn)
                            json_list.append(values)
                            self.nbdwtz_list.append(values)
                            values = {}
                            idn += 1
            # if json_list:
            #     # print 'nianbaoduiwaitouzi:', json_list
            #     self.json_result[family] = json_list

    def get_guquanchuzhi_detail(self, url):
        try:
            r = self.get_request(url=url)
        except Exception as e:
            # self.info(u'%s' %e)
            return
        soup = BeautifulSoup(r.text, 'lxml')
        table_list = soup.find_all('table')
        for tb in table_list:
            tig = tb.find_all('tr')[0].text
            if tig == u'变更':
                tr_list = tb.find_all('tr')
                th_list = tb.find_all('tr')[1].find_all('th')
                if len(tr_list) > 2:
                    dyn = 1

                    family = 'gqczbg'
                    tableID = '61'

                    json_list = []
                    values = {}
                    for tre in tr_list[2:-1]:
                        col_num = len(th_list)
                        td_list = tre.find_all('td')
                        for i in range(col_num):
                            col = th_list[i].text.strip()
                            val = td_list[i].text.strip()
                            # print u'gqbg', col, val
                            values[gqcz_biangeng_column_dict[col]] = val
                        values['rowkey'] = '%s_%s_%s_%s%d' %(self.cur_mc, self.djbh, self.djrq, tableID, dyn)
                        values[family + ':registrationno'] = self.cur_zch
                        values[family + ':enterprisename'] = self.cur_mc
                        values[family + ':id'] = str(dyn)
                        try:
                            values.pop(u'序号')
                        except KeyError as e:
                            # self.info(u'*%s' % e)
                            pass
                        json_list.append(values)
                        self.gqczbg_list.append(values)
                        values = {}
                        dyn += 1
                    # if json_list:
                    #     self.json_result[family] = json_list
            elif tig == u'注销':
                tr_list = tb.find_all('tr')
                th_list = tb.find_all('tr')[1].find_all('th')
                if len(tr_list) > 2:

                    family = 'gqczzx'
                    tableID = '60'

                    json_list = []
                    values = {}

                    dyn = 1
                    for tre in tr_list[2:-1]:
                        col_num = len(th_list)
                        td_list = tre.find_all('td')
                        for i in range(col_num):
                            col = th_list[i].text.strip()
                            val = td_list[i].text.strip()
                            # print u'gqzx', col, val
                            values[gqcz_zhuxiao_column_dict[col]] = val
                        values['rowkey'] = '%s_%s_%s_%s%d' %(self.cur_mc, self.djbh, self.djrq, tableID, dyn)
                        values[family + ':registrationno'] = self.cur_zch
                        values[family + ':enterprisename'] = self.cur_mc
                        values[family + ':id'] = str(dyn)
                        try:
                            values.pop(u'序号')
                        except KeyError as e:
                            # self.info(u'*%s' % e)
                            pass
                        json_list.append(values)
                        self.gqczzx_list.append(values)
                        values = {}
                        dyn += 1
                    # if json_list:
                    #     self.json_result[family] = json_list

    def get_dongchandiya_detail(self, url):
        zxb = {'dyqrgkFrame': u'抵押权人概况', 'dywgkFrame':u'抵押物概况', 'dcdybgFrame': u'变更'}  # iframe id参数
        data={
            'ajax':'true',
            'time':time.time()*1000
        }
        try:
            r = self.post_request(url=url,data=data)
        except Exception as e:
            print '---------'
            self.info(u'%s' %e)
            return
        chr = re.search(r'(?<=chr_id=).*', url).group()
        soup = BeautifulSoup(r.text, 'lxml')
        # print '**__**', soup
        table_list = soup.find_all('table')
        iframe_list = soup.find_all('iframe')
        h1_list = soup.find_all('h1')[1:]
        values = {}
        for x in range(len(table_list)):
            tb=table_list[x]
            tig = h1_list[x].text.strip()
            # print 'dcdy**bb', tig
            if tig == u'动产抵押登记信息':
                values[tig] = {}
                tr_list = tb.find_all('tr')
                for tre in tr_list:
                    th_list = tre.find_all('th')
                    td_list = tre.find_all('td')
                    col_num = len(th_list)
                    for i in range(col_num):
                        col = th_list[i].text.strip()
                        val = td_list[i].text.strip()
                        # print 'dc**djxx', col, val
                        values[tig][col] = val


            elif tig == u'被担保债权概况信息':
                values[tig] = {}
                tr_list = tb.find_all('tr')
                for tre in tr_list:
                    th_list = tre.find_all('th')
                    td_list = tre.find_all('td')
                    col_num = len(th_list)
                    for i in range(col_num):
                        col = th_list[i].text.strip()
                        val = td_list[i].text.strip()
                        # print 'dc**bdbrgk', col, val
                        values[tig][col] = val

            elif tig == u'注销信息':
                values[tig] = {}
                tr_list = tb.find_all('tr')
                for tre in tr_list:
                    th_list = tre.find_all('th')
                    td_list = tre.find_all('td')
                    col_num = len(th_list)
                    for i in range(col_num):
                        col = th_list[i].text.strip()
                        val = td_list[i].text.strip()
                        # print 'dc**zx', col, val
                        values[tig][col] = val
            else:
                self.info('unknown_title:'+tig)

        cur_time=str(int(time.time()*1000))
        for fm in iframe_list:
            fid = fm.get('id')  # iframe对应id
            trg = zxb[fid]  # id对应表名
            if trg == u'抵押权人概况':
                values[trg] = []
                url = 'http://bj.gsxt.gov.cn/gjjbjTab/gjjTabQueryCreditAction!dyqrgkFrame.dhtml?'\
                'ent_id='+self.entId+'&chr_id='+chr+'&clear=true&timeStamp='+cur_time
                # print u'抵押权人概况url', url
                r = self.get_request(url=url)
                soup = BeautifulSoup(r.text, 'lxml')
                # print 'dyqrgk', soup
                tb_list = soup.find_all(class_='table-result')
                # print 'len@', len(tb_list)
                try:
                    tr_list = tb_list[0].find_all('tr')
                except:
                    self.info(u'抵押权人概况加载失败')
                    continue
                th_list = tb_list[0].find_all('tr')[0].find_all('th')
                if len(tr_list) > 1:
                    td_len = len(tr_list[1].find_all('td'))
                    if td_len>1:
                        for tre in tr_list[1:]:
                            one_row = {}
                            col_num = len(th_list)
                            td_list = tre.find_all('td')
                            for i in range(col_num):
                                col = th_list[i].text.strip()
                                val = td_list[i].text.strip()
                                # print u'@@', col, val
                                one_row[col] = val
                            values[trg].append(one_row)


            elif trg == u'抵押物概况':
                values[trg] = []

                url = 'http://bj.gsxt.gov.cn/gjjbjTab/gjjTabQueryCreditAction!dywgkFrame.dhtml?'\
                'chr_id='+chr+'&chr_id='+chr+'&clear=true&timeStamp='+cur_time
                # print u'抵押物概况url', url
                r = self.get_request(url=url)
                soup = BeautifulSoup(r.text, 'lxml')
                # print 'dywgk', soup
                tb_list = soup.find_all(class_='table-result')
                # print 'lenβ', len(tb_list)
                try:
                    tr_list = tb_list[0].find_all('tr')
                except:
                    self.info(u'抵押物概况table加载失败，访问频繁')
                    continue
                th_list = tr_list[0].find_all('th')
                if len(tr_list) > 1:
                    td_len = len(tr_list[1].find_all('td'))
                    if td_len>1:
                        for tre in tr_list[1:]:
                            one_row = {}
                            col_num = len(th_list)
                            td_list = tre.find_all('td')
                            for i in range(col_num):
                                col = th_list[i].text.strip()
                                val = td_list[i].text.strip()
                                # print u'@@', col, val
                                one_row[col] = val
                            values[trg].append(one_row)


            elif trg == u'变更':
                values[trg] = []

                url = 'http://bj.gsxt.gov.cn/gjjbjTab/gjjTabQueryCreditAction!dcdybgFrame.dhtml?'\
                'chr_id='+chr+'&chr_id='+chr+'&clear=true&timeStamp='+cur_time
                # print u'变更url', url
                r = self.get_request(url=url)
                soup = BeautifulSoup(r.text, 'lxml')
                # print 'dybg', soup
                tb_list = soup.find_all(class_='table-result')
                # print 'lenγ', len(tb_list)
                try:
                    tr_list = tb_list[0].find_all('tr')
                except:
                    self.info(u'动产抵押变更加载失败')
                    continue
                th_list = tr_list[0].find_all('th')
                if len(tr_list) > 1:
                    td_len = len(tr_list[1].find_all('td'))
                    if td_len>1:
                        for tre in tr_list[1:]:
                            one_row = {}
                            col_num = len(th_list)
                            td_list = tre.find_all('td')
                            for i in range(col_num):
                                col = th_list[i].text.strip()
                                val = td_list[i].text.strip()
                                # print u'@@', col, val
                                one_row[col] = val
                            values[trg].append(one_row)
        return values
# if __name__ == '__main__':
#     searcher = BeiJing()
#     f = open('E:\\bj50.txt','r').readlines()
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
#         # searcher.submit_search_request(u"北京链家房地产经纪有限公司")#北京众旺达汽车租赁有限公司")#北京京东尚科信息技术有限公司")  # 阿里巴巴（北京）软件服务有限公司")
#         # 北京幻想纵横网络技术有限公司")#北京百代彩虹激光技术有限责任公司")#北京北斗兴业信息技术股份有限公司") # 北京中益优胜投资管理有限公司
#         # 北京三宝阁图书销售中心")#北京百度网讯科技有限公司")# 北京一搏星徽商贸中心")#北京链家房地产经纪有限公司")#北斗中科卫士物联科技（北京）有限公司")#北京兴盛建业机电设备有限公司")
#         # 乐视网信息技术（北京）股份有限公司")#北京中视乾元文化发展有限公司")中国机械工业集团有限公司 北京世纪卓越信息技术有限公司
#         # 北京链家房地产经纪有限公司")#中信国安黄金有限责任公司")  # 北京正北经贸有限公司 本草汇（北京）环境治理有限公司"))  北京京东叁佰陆拾度电子商务有限公司
#             print cnt, json.dumps(searcher.json_result, ensure_ascii=False)
#         except:
#             pass
#         cnt += 1

if __name__ == '__main__':
    searcher = BeiJing()
    # searcher.get_lock_id()
    searcher.submit_search_request(u'北京博顿电气有限公司')#北京链家房地产经纪有限公司')
    print json.dumps(searcher.json_result, ensure_ascii=False)
    # searcher.submit_search_request(u'北京华美天祥贸易有限责任公司（集体股）')  # 北京链家房地产经纪有限公司')
    # print json.dumps(searcher.json_result, ensure_ascii=False)
