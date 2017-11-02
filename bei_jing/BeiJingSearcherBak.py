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

    def get_tag_a_from_page(self, keyword, flags=True):
        self.get_lock_id()
        self.get_request('http://bj.gsxt.gov.cn/sydq/loginSydqAction!sydq.dhtml')
        validate = self.get_geetest_validate()
        # print validate
        # self.headers['Host'] = 'bj.gsxt.gov.cn'
        # self.headers['Referer'] = 'http://bj.gsxt.gov.cn/sydq/loginSydqAction!sydq.dhtml'

        url_1 = "http://bj.gsxt.gov.cn/pc-geetest/validate"
        params_1 = {
            'geetest_challenge': self.challenge,
            'geetest_validate': validate,
            'geetest_seccode': '%s|jordan' % validate,
        }
        self.post_request(url=url_1, params=params_1)
        url_2 = "http://bj.gsxt.gov.cn/es/esAction!entlist.dhtml?urlflag=0&challenge="+self.challenge
        data_2 = {
            'keyword': keyword,
            'nowNum': '',
            'clear': '请输入企业名称、统一社会信用代码或注册号',
            'urlflag': '0',
        }

        r_2 = self.post_request(url_2, params=data_2)
        r_2.encoding = 'utf-8'
        soup = BeautifulSoup(r_2.text, 'html5lib')
        # print 'soup:', soup
        results = soup.select('div.search-result ul')
        self.tagA = None
        if len(results) > 0:
            company_list = []
            company_code = []
            company_tags = []
            # print u'有查询结果'
            self.info(u'查询有结果，开始解析')
            cnt = 1
            for result in results:
                name = result.find('span').text.strip()
                name = self.process_mc(name)
                print name, keyword
                if name == keyword:
                    linko = result.find('table').get('onclick')
                    link = re.search(u'(?<=").*?(?=")', linko).group()
                    tagA = self.domain + link
                    code = result.find('td').contents[1].strip()
                    self.cur_mc = name
                    self.cur_zch = code
                    self.cur_code = code
                    self.tagA = tagA
                    if len(self.cur_code) == 18:
                        self.xydm = self.cur_code
                    else:
                        self.zch = self.cur_code
                    ent_id = re.search(u'(?<=entId=).*?(?=&)', tagA).group()
                    creditt = re.search(u'(?<=ket=).*', tagA).group()
                    # print 'ent_id', ent_id, 'creditt', creditt
                    self.entId = ent_id
                    self.creditt = creditt
                    # print '*.*'*100
                    r = self.get_request(url=tagA, params={})
                    # print r.text, r.headers
                    soup = BeautifulSoup(r.text, 'html5lib')
                    list_tabs = soup.find(class_='bbox').find_all('a')
                    self.tab_url = []
                    #hhh
                    for tab in list_tabs:
                        url = self.domain + tab.get('href')
                        # print 'tab*url', url
                        self.tab_url.append(url)
                    break
        else:
            # print r_2.text
            if u'查询到0条信息' not in r_2.text:
                print u'频繁访问错误页面'
                raise Exception(u'错误页面')
            else:
                print u'查无结果', keyword
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
        # self.get_gu_dong_chu_zi()           # New Gudong-details(temp)
        self.get_zhu_guan_bu_men()
        # print 'gd_step_json', self.json_result
        self.info(u'解析变更信息')
        self.get_bian_geng()
        # print 'bg_step_json', self.json_result
        self.info(u'解析主要人员')
        self.get_zhu_yao_ren_yuan()
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
        soup = BeautifulSoup(r.text, 'html5lib')
        # print 'gudong_soup', soup
        if u'暂无股东信息' in soup.find('table').text or u'暂无股东名称' in soup.find('table').text:
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
                    r = self.post_request(url, params=params)
                    soup = BeautifulSoup(r.text, 'html5lib')
                    # print 'gudong',p,soup
                    tr_list = soup.find('table').find_all('tr')
                    if len(tr_list) > 1:
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
        r = self.get_request(url=url, params={})
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
                    r = self.post_request(url=url, params=params)
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
        # print 'zhuyaorenyuan_soup', soup
        try:
            tb = len(soup.find_all('tbody'))
        except:
            tb = 0

        if tb > 0:
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
        try:
            r = self.get_request(url=url)
        except Exception as e:
            self.info(u'%s' %e)
            return
        chr = re.search(r'(?<=chr_id=).*', url).group()
        soup = BeautifulSoup(r.text, 'lxml')
        # print '**__**', soup
        table_list = soup.find_all('table')
        iframe_list = soup.find_all('iframe')
        dcnt = 0
        for tb in table_list:
            tig = tb.find_all('tr')[0].text
            # print 'dcdy**bb', tig
            if tig == u'动产抵押登记信息':

                family = 'dcdydj'
                tableID = '63'

                json_list = []
                values = {}
                djbh = u''
                djrq = u''
                tr_list = tb.find_all('tr')[1:]
                for tre in tr_list:
                    th_list = tre.find_all('th')
                    td_list = tre.find_all('td')
                    col_num = len(th_list)
                    for i in range(col_num):
                        col = th_list[i].text.strip()
                        val = td_list[i].text.strip()
                        # print 'dc**djxx', col, val
                        values[dcdy_dengji_column_dict[col]] = val
                        if col == u'登记编号':
                            djbh = val
                            self.djbh = djbh
                        if col == u'登记日期':
                            djrq = val
                            self.djrq = djrq
                values['rowkey'] = '%s_%s_%s_%s' %(self.cur_mc, self.djbh, self.djrq, tableID)
                values[family + ':registrationno'] = self.cur_zch
                values[family + ':enterprisename'] = self.cur_mc
                # json_list.append(values)
                self.dcdydj_list.append(values)

                # self.json_result[family] = json_list

            elif tig == u'被担保债权概况':
                family = 'bdbzqgk'
                tableID = '56'

                json_list = []
                values = {}

                tr_list = tb.find_all('tr')[1:]
                for tre in tr_list:
                    th_list = tre.find_all('th')
                    td_list = tre.find_all('td')
                    col_num = len(th_list)
                    for i in range(col_num):
                        col = th_list[i].text.strip()
                        val = td_list[i].text.strip()
                        # print 'dc**bdbrgk', col, val
                        values[dcdy_beidanbaozhaiquan_column_dict[col]] = val
                values['rowkey'] = '%s_%s_%s_%s' %(self.cur_mc, self.djbh, self.djrq, tableID)
                values[family + ':registrationno'] = self.cur_zch
                values[family + ':enterprisename'] = self.cur_mc
                # json_list.append(values)
                self.bdbzqgk_list.append(values)
                # self.json_result[family] = json_list

            elif tig == u'注销':
                family = 'dcdyzx'
                tableID = '59'

                json_list = []
                values = {}
                tr_list = tb.find_all('tr')[1:]
                for tre in tr_list:
                    th_list = tre.find_all('th')
                    td_list = tre.find_all('td')
                    col_num = len(th_list)
                    for i in range(col_num):
                        col = th_list[i].text.strip()
                        val = td_list[i].text.strip()
                        # print 'dc**zx', col, val
                        values[dcdy_zhuxiao_column_dict[col]] = val
                values['rowkey'] = '%s_%s_%s_%s' %(self.cur_mc, self.djbh, self.djrq, tableID)
                values[family + ':registrationno'] = self.cur_zch
                values[family + ':enterprisename'] = self.cur_mc
                # json_list.append(values)
                self.dcdyzx_list.append(values)
                # self.json_result[family] = json_list

            else:
                self.info('unknown_title:'+tig)


        for fm in iframe_list:
            # print '**'*100
            fid = fm.get('id')  # iframe对应id
            trg = zxb[fid]  # id对应表名
            # print 'dcdy**ff', fid, trg, '**',  self.entId, 'm', chr
            if trg == u'抵押权人概况':
                family = 'dyqrgk'
                tableID = '55'
                json_list = []
                values = {}

                url = 'http://qyxy.baic.gov.cn/gjjbjTab/gjjTabQueryCreditAction!dyqrgkFrame.dhtml?'\
                'ent_id='+self.entId+'&chr_id='+chr+'&clear=true&timeStamp='+self.cur_time
                # print u'抵押权人概况url', url
                r = self.get_request(url=url)
                soup = BeautifulSoup(r.text, 'lxml')
                # print 'dyqrgk', soup
                tb_list = soup.find_all(class_='detailsList')
                # print 'len@', len(tb_list)
                try:
                    tr_list = tb_list[0].find_all('tr')
                except:
                    self.info(u'抵押权人概况加载失败')
                    continue
                th_list = tb_list[0].find_all('tr')[1].find_all('th')
                gkn = 1  # 概况递增id
                if len(tr_list) > 3:
                    for tre in tr_list[2:-1]:
                        col_num = len(th_list)
                        td_list = tre.find_all('td')
                        for i in range(col_num):
                            col = th_list[i].text.strip()
                            val = td_list[i].text.strip()
                            # print u'@@', col, val
                            values[dcdy_diyaquanren_column_dict[col]] = val
                        values['rowkey'] = '%s_%s_%s_%s%d' %(self.cur_mc, self.djbh, self.djrq, tableID, gkn)
                        values[family + ':registrationno'] = self.cur_zch
                        values[family + ':enterprisename'] = self.cur_mc
                        values[family + ':id'] = str(gkn)
                        try:
                            values.pop(dcdy_diyaquanren_column_dict[u'序号'])
                        except KeyError as e:
                            # self.info(u'%s' % e)
                            pass
                        # json_list.append(values)
                        self.dyqrgk_list.append(values)
                        values = {}
                        gkn += 1
                    # if json_list:
                    #     self.json_result[family] = json_list

            elif trg == u'抵押物概况':
                family = 'dywgk'
                tableID = '57'

                json_list = []
                values = {}

                url = 'http://qyxy.baic.gov.cn/gjjbjTab/gjjTabQueryCreditAction!dywgkFrame.dhtml?'\
                'chr_id='+chr+'&chr_id='+chr+'&clear=true&timeStamp='+self.cur_time
                # print u'抵押物概况url', url
                r = self.get_request(url=url)
                soup = BeautifulSoup(r.text, 'lxml')
                # print 'dywgk', soup
                tb_list = soup.find_all(class_='detailsList')
                # print 'lenβ', len(tb_list)
                try:
                    tr_list = tb_list[0].find_all('tr')
                except:
                    self.info(u'抵押物概况table加载失败，访问频繁')
                    continue
                th_list = tb_list[0].find_all('tr')[1].find_all('th')
                pgn = tr_list[-1].find_all('a')
                try:
                    pagescnt = int(soup.find(id='pagescount').get('value'))
                    # print '@'*20, 'gk', pagescnt
                except:
                    pagescnt = 1
                # print 'pgn', len(pgn)

                dyn = 1
                if len(tr_list) > 3:
                    for tre in tr_list[2:-1]:
                        col_num = len(th_list)
                        td_list = tre.find_all('td')
                        for i in range(col_num):
                            col = th_list[i].text.strip()
                            val = td_list[i].text.strip()
                            # print u'ββ', col, val
                            values[dcdy_diyawu_column_dict[col]] = val
                        values['rowkey'] = '%s_%s_%s_%s%d' %(self.cur_mc, self.djbh, self.djrq, tableID, dyn)
                        values[family + ':registrationno'] = self.cur_zch
                        values[family + ':enterprisename'] = self.cur_mc
                        values[family + ':id'] = str(dyn)
                        try:
                            values.pop(dcdy_diyawu_column_dict[u'序号'])
                        except KeyError as e:
                            # self.info(u'%s' % e)
                            pass
                        # json_list.append(values)
                        self.dywgk_list.append(values)
                        values = {}
                        dyn += 1

                    # 有翻页情况
                    if len(pgn) > 2:

                        for p in range(2, pagescnt+1):
                            url = 'http://qyxy.baic.gov.cn/gjjbjTab/gjjbjTab/gjjTabQueryCreditAction!dywgkFrame.dhtml'
                            params = dict(chr_id=chr, clear='', ent_id='', pageNo=p-1, pageNos=p, pageSize=5)
                            # print 'wgk**', params
                            try:
                                r = self.post_request(url=url, params=params)
                            except:
                                # self.info(u'网站内部internal Error访问频繁')
                                continue
                            soup = BeautifulSoup(r.text, 'lxml')
                            # print 'dywgksub', soup
                            tb_list = soup.find_all(class_='detailsList')
                            try:
                                tr_list = tb_list[0].find_all('tr')
                            except:
                                # self.info(u'翻页太频繁,ip临时被封')
                                continue
                            pgn = tr_list[-1].find_all('a')

                            for tre in tr_list[2:-1]:
                                col_num = len(th_list)
                                td_list = tre.find_all('td')
                                for i in range(col_num):
                                    col = th_list[i].text.strip()
                                    val = td_list[i].text.strip()
                                    # print u'ββsub', p, col, val
                                    values[dcdy_diyawu_column_dict[col]] = val
                                values['rowkey'] = '%s_%s_%s_%s%d' %(self.cur_mc, self.djbh, self.djrq, tableID, dyn)
                                values[family + ':registrationno'] = self.cur_zch
                                values[family + ':enterprisename'] = self.cur_mc
                                values[family + ':id'] = str(dyn)
                                try:
                                    values.pop(dcdy_diyawu_column_dict[u'序号'])
                                except KeyError as e:
                                    # self.info(u'*%s' % e)
                                    pass
                                json_list.append(values)
                                self.dywgk_list.append(values)
                                values = {}
                                dyn += 1
                            # 下面跳出逻辑最多指定10页抓取，有1000多页 e.g.北京恒嘉国际融资租赁有限公司
                            if p == 10:
                                # print u'页数过多，只取前10页', pagescnt
                                self.info(u'页数过多，只取前10页')
                                break
                    # if json_list:
                    #     self.json_result[family] = json_list

            elif trg == u'变更':
                family = 'dcdybg'
                tableID = '58'

                json_list = []
                values = {}

                url = 'http://qyxy.baic.gov.cn/gjjbjTab/gjjTabQueryCreditAction!dcdybgFrame.dhtml?'\
                'chr_id='+chr+'&chr_id='+chr+'&clear=true&timeStamp='+self.cur_time
                # print u'变更url', url
                r = self.get_request(url=url)
                soup = BeautifulSoup(r.text, 'lxml')
                # print 'dybg', soup
                tb_list = soup.find_all(class_='detailsList')
                # print 'lenγ', len(tb_list)
                try:
                    tr_list = tb_list[0].find_all('tr')
                except:
                    self.info(u'动产抵押变更加载失败')
                    continue
                th_list = tb_list[0].find_all('tr')[1].find_all('th')
                if len(tr_list) > 2:
                    dyn = 1
                    for tre in tr_list[2:-1]:
                        col_num = len(th_list)
                        td_list = tre.find_all('td')
                        for i in range(col_num):
                            col = th_list[i].text.strip()
                            val = td_list[i].text.strip()
                            # print u'γγ', col, val
                            values[dcdy_biangeng_column_dict[col]] = val
                        values['rowkey'] = '%s_%s_%s_%s%d' %(self.cur_mc, self.djbh, self.djrq, tableID, dyn)
                        values[family + ':registrationno'] = self.cur_zch
                        values[family + ':enterprisename'] = self.cur_mc
                        values[family + ':id'] = str(dyn)
                        try:
                            values.pop(dcdy_biangeng_column_dict[u'序号'])
                        except KeyError as e:
                            # self.info(u'*%s' % e)
                            pass
                        json_list.append(values)
                        self.dcdybg_list.append(values)
                        values = {}
                        dyn += 1
                    # if json_list:
                    #     self.json_result[family] = json_list
            else:
                # print u'未知表格', trg
                self.info(u'未知表格'+trg)

        dcnt += 1


if __name__ == '__main__':
    searcher = BeiJing()
    # searcher.get_lock_id()
    searcher.submit_search_request(u'北京云图微动科技有限公司')#北京链家房地产经纪有限公司')
    print json.dumps(searcher.json_result, ensure_ascii=False)
