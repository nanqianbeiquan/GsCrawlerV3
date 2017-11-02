# coding=utf-8

import PackageTool

from gs.Searcher import Searcher
# from gs.Searcher import get_args
from gs import TimeUtils
from bs4 import BeautifulSoup
import requests
from gs.CompareStatus import *
import time
import json
from geetest_broker.GeetestBroker import GeetestBrokerOffline
from HuBeiConfig import *
import re
import urllib


class HuBeiSearcher(Searcher, GeetestBrokerOffline):
    load_func_dict = {}

    def __init__(self, dst_topic=None):
        super(HuBeiSearcher, self).__init__(use_proxy=True, dst_topic=dst_topic)
        self.headers = {"User-Agent":  'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0',
                        # "Host": "hb.gsxt.gov.cn",
                        # "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                        # "Accept-Encoding": "gzip, deflate",
                        # "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
                        # "Connection": "keep-alive",
                        # # "Referer": "http://sh.gsxt.gov.cn/notice/search/ent_info_list",
                        # "Upgrade-Insecure-Requests": "1",
                        # "X-Requested-With": "XMLHttpRequest"
        }
        # self.s = set()
        self.set_config()
        self.set_geetest_config()
        self.ent_id = ''
        self.log_name = 'hu_bei'
        self.time = time.strftime('%Y%m%d')
        self.load_func_dict[u'营业执照信息'] = self.load_jiben
        self.load_func_dict[u'股东及出资信息'] = self.load_gudong
        self.load_func_dict[u'发起人及出资信息'] = self.load_gudong
        self.load_func_dict[u'变更信息'] = self.load_biangeng
        self.load_func_dict[u'主要人员信息'] = self.load_zhuyaorenyuan
        # self.load_func_dict[u'参加经营的家庭成员姓名'] = self.load_jiatingchengyuan     # Modified by Jing
        self.load_func_dict[u'投资人信息'] = self.load_touziren     #Modified by Jing
        self.load_func_dict[u'合伙人信息'] = self.load_gudong     #Modified by Jing
        self.load_func_dict[u'成员名册信息'] = self.load_chengyuanmingce     #Modified by Jing
        self.load_func_dict[u'主管部门（出资人）信息'] = self.load_gudong

    def set_config(self):
        self.province = u'湖北省'

    def set_geetest_config(self):
        self.geetest_referer = "http://hb.gsxt.gov.cn/index.jspx"
        self.geetest_product = "popup"

    def get_gt_challenge(self, t=0):
        if t == 15:
            raise Exception(u'获取gt和challenge失败')
        url_1 = 'http://hb.gsxt.gov.cn/registerValidate.jspx?t=%s' % TimeUtils.get_cur_ts_mil()
        r_1 = self.get_request(url_1)
        # print r_1.text, r_1.text.strip().startswith('{'), r_1.text.strip().endswith('}')
        if r_1.text.strip().startswith('{') and r_1.text.strip().endswith('}'):
            self.challenge = str(json.loads(r_1.text)['challenge'])
            self.gt = str(json.loads(r_1.text)['gt'])
        else:
            time.sleep(1)
            self.reset_session()
            self.get_gt_challenge(t + 1)

    def get_tag_a_from_page(self, keyword, flags=True):
        self.get_lock_id()
        best_djzt = None
        validate = self.get_geetest_validate()
        # print 'validate',validate
        # print 'self.challenge',self.challenge
        url_1 = "http://dfp2.bangruitech.com/public/generate/jsonp?algID=DxbncDlc3j&hashCode=47DEQpj8HBSa-_TImW-5JCeuQeRkm5NMpJWZG3hSuFU&FMQw=0&q4f3=zh-CN&VPIf=1&custID=51&VEek=unknown&dzuS=27.0%20r0&yD16=0&EOQP=49a9fbfe2beb0490836324ceb234fef4&lEnu=3232235916&jp76=bb5032aedcaa9cca45f29e44506d1288&hAqN=Win32&platform=WEB&ks0Q=93b5994b1daea02ec4a30a4f9c1a569c&TeRS=1040x1920&tOHY=24xx1080x1920&Fvje=i1l1o1s1&q5aJ=-8&wNLf=99115dfb07133750ba677d055874de87&0aew=Mozilla/5.0%20"
        r_1 = self.get_request(url=url_1, headers=self.headers)
        # print r_1.text
        _cookie = r_1.text.split('dfp":"')[1].split('"')[0]
        self.cookie ={'BSFIT_DEVICEID' : _cookie}
        # print _cookie
        url_3 = "http://hb.gsxt.gov.cn/validateSecond.jspx"
        params_3 = {
            'geetest_challenge': self.challenge,
            'geetest_validate': validate,
            'geetest_seccode': '%s|jordan' % validate,
            'searchText': keyword
        }
        self.post_request(url=url_3, data=params_3)
        # r_3 = self.post_request(url=url_3, data=params_3)
        # print '#'*100
        # print r_3.text
        obj = None
        for i in range(15):
            r_3 = self.post_request(url_3, data=params_3)
            if r_3.text.strip().startswith('{') and r_3.text.strip().endswith('}'):
                obj = json.loads(r_3.text)['obj']
                if obj:
                    break
        self.headers['Referer']='http://hb.gsxt.gov.cn/index.jspx'
        self.headers['X-BR-Antispider-ServiceURL']='http://hb.gsxt.gov.cn/searchList.jspx'
        keyword_b = urllib.quote(urllib.quote(keyword.encode('utf-8')))
        url_4 = 'http://hb.gsxt.gov.cn/searchList.jspx?top=top&checkNo=%s&searchType=1&entName=%s' %(validate,keyword_b)
        r_4 = self.get_request(url=url_4, headers=self.headers,cookies=self.cookie)
        r_4.encoding='utf8'
        # print '%'*100
        # print r_4.text
        soup = BeautifulSoup(r_4.text, 'html5lib')
        # results = soup.find(id='contentList')
        results = soup.find(id='contentList', class_='contentList').find_all('div', id='gggscpnamebox')
        self.xydm_if = ''
        self.zch_if = ''
        cnt = 0
        company_list = []
        company_code = []
        company_tags = []
        # print 'len(results)', len(results)
        if len(results) > 0:
            keyword_tran = keyword.replace('(', u'（').replace(')', u'）')
            for r in results:
                cnt += 1
                name = r.find('span', class_='qiyeEntName').text.strip()
                name = name.split('\n')[0]
                status = r.find('span', class_='qiyezhuangtai fillet').text.strip()
                # print 'status', status
                code = r.find(class_='gggscpnametext').find('span', class_='tongyi').find_all('span')[1].text.strip()
                tagA = r.find(class_='gggscpnametitle').find_all('span')[-1].get('id')
                # print cnt, name, code, tagA,type(tagA)
                company_list.append(name)
                company_code.append(code)
                company_tags.append(tagA)
            # print 'company_list', company_list
            for i, item in enumerate(company_list):
                item_tran = item.replace('(', u'（').replace(')', u'）')
                # print "item", i, item_tran, keyword_tran
                if keyword_tran == item_tran:
                    if compare_status(status, best_djzt) >= 0:
                        best_djzt = status
                        self.cur_mc = item_tran
                        self.cur_code = company_code[i]
                        self.cur_zch = company_code[i]
                        self.tagA = company_tags[i]
                        if len(self.cur_code) == 18:
                            self.xydm_if = self.cur_code
                        else:
                            self.zch_if = self.cur_code
            try:
                if self.tagA:
                    return self.tagA
            except:
                return None
        else:
            self.info(u'查询无结果')
            return None

    def get_search_args(self, tag_a, keyword):
        self.tag_a = tag_a
        if tag_a:
            return 1
        else:
            return 0

    def parse_detail(self):
        # html = open('C:/Users/huaixuan.guan/Desktop/hb.html')
        # data = html.read().decode('gbk')
        # html.close()
        # resdetail = data
        # # print 'r.text', data
        # soup = BeautifulSoup(resdetail, 'html5lib')
        self.get_lock_id()
        url_1 = "http://dfp2.bangruitech.com/public/generate/jsonp?algID=DxbncDlc3j&hashCode=47DEQpj8HBSa-_TImW-5JCeuQeRkm5NMpJWZG3hSuFU&FMQw=0&q4f3=zh-CN&VPIf=1&custID=51&VEek=unknown&dzuS=27.0%20r0&yD16=0&EOQP=49a9fbfe2beb0490836324ceb234fef4&lEnu=3232235916&jp76=bb5032aedcaa9cca45f29e44506d1288&hAqN=Win32&platform=WEB&ks0Q=93b5994b1daea02ec4a30a4f9c1a569c&TeRS=1040x1920&tOHY=24xx1080x1920&Fvje=i1l1o1s1&q5aJ=-8&wNLf=99115dfb07133750ba677d055874de87&0aew=Mozilla/5.0%20"
        r_1 = self.get_request(url=url_1, headers=self.headers)
        # print r_1.text
        _cookie = r_1.text.split('dfp":"')[1].split('"')[0]
        self.cookie ={'BSFIT_DEVICEID' :_cookie}
        date3 = time.strftime('%a %b %d %Y %X GMT+0800', time.localtime())
        date_tran = date3.replace(" ", '%20')
        url = 'http://hb.gsxt.gov.cn/business/JCXX.jspx?id='+self.tag_a+'&date='+date_tran
        # print 'parse_detail_url', url
        # cookies={
        #     'BSFIT_DEVICEID' :'cF30T1dM1X2IaWbE69hRfE_gytWPzMtwBEBvtXi8w4mh2zc-xiv-Fs9AdI9iormkuLJBWsWkRVmnnF7ZpfVcNCsC_L5HqPHIW2wW-4FZZSy9TJYnkOEETNHGWz1yUV-jSQapGIDn4v8WfOLyRkUKndV0TuyRu0dg',
        #     # 'BSFIT_OkLJUJ' :'FDOYEcTM57aH9t6fuUmah7E4a1Y31ZgG',
        #     # 'BSFIT_EXPIRATION' : '1506722388762'
        # }
        # print 'self.cookie', self.cookie
        ss = 0
        for i in range(10):
            try:
                r2 = self.get_request(url, headers=self.headers, cookies=self.cookie)
                # r2 = requests.get(url, headers=self.headers)
                if r2.status_code != 200:
                    ss += 1
                    print u'第%s次尝试搜索' %ss
                    continue
                # elif ss == 8:
                #     raise Exception(u'网页打不开，需要重试')
                else:
                    break
            except Exception, e:
                pass
        # print '*'*100
        # print r2.text
        soup = BeautifulSoup(r2.text, 'html5lib')
        div_element_list = soup.find_all(class_='baseinfo')
        for div_element in div_element_list[:12]:
            table_desc = div_element.find("span").contents[0].strip().split('\n')[0]
            # print 'table_desc', table_desc
            # if table_desc in (u'分支机构信息', u'清算信息', u'动产抵押登记信息',u'股权出质登记信息',\
            #   u'知识产权出质登记信息', u'商标注册信息',  u'抽查检查结果信息',  u'司法协助信息',u'参加经营的家庭成员姓名'):
            #     continue
            if table_desc in (u'营业执照信息', u'变更信息', u'主要人员信息'):
                table_element = div_element.find_all('div')[1]
                if table_desc == u'主要人员信息' :
                    try:
                        branch_num = soup.find(class_="baseinfo",style='padding-bottom:8px;').find_all('span')[1].text.strip()
                        try:
                            self.item = int(branch_num.split(u'共计')[1].split(u'条信息')[0])
                        except:
                            self.item = ''
                        if self.item > 16:
                            branch_uuid = soup.find(class_="baseinfo",style='padding-bottom:8px;').find_all('span')[1].a['onclick']
                            self.branch_uuid = branch_uuid .split("?id=")[1].split("')")[0]
                            self.branch_num = str(self.item//16)
                            # print "self.branch_num", self.branch_uuid, self.branch_num
                        else:
                            self.branch_num = ''
                    except:
                        self.branch_num = ''
                self.load_func_dict[table_desc](table_element)
            elif table_desc in (u'股东及出资信息', u'发起人及出资信息',u'投资人信息', u'合伙人信息', u'主管部门（出资人）信息'):
                table_element = div_element.find_all('div')[2]
                self.load_func_dict[table_desc](table_element)
            elif table_desc == u'成员名册信息':
                table_element = div_element
                self.load_func_dict[table_desc](table_element)
            else:
                pass

    def load_jiben(self, table_element):
        self.info(u'解析基本信息...')
        jsonarray = []
        tr_element_list = table_element.find_all("tr")
        values = {}
        for tr_element in tr_element_list:
            td_element_list = tr_element.find_all('td')
            col_nums = len(td_element_list)
            for i in range(col_nums):
                col_dec_1 = td_element_list[i].contents
                if col_dec_1:
                    col_dec_2 = td_element_list[i].contents[0].strip().split('\n')[0]
                    col_dec_2.encode('utf-8')
                    col_dec = col_dec_2.replace(u'·', '').replace(u'：', '').strip().replace('', '')
                    # print 'col_dec', col_dec
                    if col_dec != u'':
                        col = jiben_column_dict[col_dec]
                        val = td_element_list[i].contents[1].text.strip()
                        values[col] = val
                        if col == 'Registered_Info:registrationno':
                            if len(val) == 18:
                                values['Registered_Info:tyshxy_code'] = val
                            else:
                                values['Registered_Info:zch'] = val
                            self.cur_code = val
                        if col == 'Registered_Info:enterprisename':
                            self.cur_mc = val
                        if col == 'Registered_Info:registrationno':
                            self.cur_zch = val
        try:
            if u'范围 ' in table_element.text or table_element.find(class_='jingyingfanwei'):
                values['Registered_Info:businessscope'] = \
                table_element.find(class_='jingyingfanwei').contents[1].text.strip().replace('\n', '')
        except:
            values['Registered_Info:businessscope'] = ''
        values['Registered_Info:province'] = self.province
        values['rowkey'] = self.cur_mc+'_01_'+self.cur_code+'_'
        jsonarray.append(values)
        self.json_result['Registered_Info'] = jsonarray
        # json_jiben =json.dumps(jsonarray, ensure_ascii=False)
        # print 'json_jiben', json_jiben

    def load_gudong(self, table_element):
        self.info(u'解析股东信息...')
        self.values_before = {}
        self.json_result['Shareholder_Info'] = []
        # print table_element
        if u'共查询' in table_element.text or u'页' in table_element.text:
            pages = table_element.find(class_="ax_image fenye").find_all('li')[1].text.strip()
            page_num = int(pages.replace(u'共', '').replace(u'页', ''))
            # print 'page_num', page_num
            self.parse_gudong(table_element)
            if page_num > 1:
                for p in range(page_num-1):
                    url = "http://hb.gsxt.gov.cn/business/QueryInvList.jspx?pno="+str(p+2)+'&order=0&mainId=' + self.tag_a
                    for i in range(8):
                        try:
                            r = self.get_request(url, headers=self.headers)
                            if r.status_code != 200 or u'序号' not in r.text:
                                continue
                            else:
                                break
                        except Exception, e:
                            pass
                    soup = BeautifulSoup(r.text, 'html5lib')
                    table_element = soup.find(class_='ax_table liebiaoxinxin')
                    # print u'股东多页', table_element
                    self.parse_gudong(table_element)

    def parse_gudong(self, table_element):
        tr_element_list = table_element.find_all("tr")
        th_element_list = table_element.find_all('th')[1:]
        id = 1
        for tr_element in tr_element_list[1:]:
            td_element_list = tr_element.find_all('td')[1:]
            col_nums = len(th_element_list)
            for i in range(col_nums):
                col_dec = th_element_list[i].get_text().strip().replace('\n', '')
                col = gudong_column_dict[col_dec]
                # print 'col_dec', col_dec, col
                td = td_element_list[i]
                val = td.get_text().strip()
                self.values_before[col] = val
            # print '%'*10, len(td_element_list), self.values_before
            if len(td_element_list) == 5:
                if td_element_list[4].text.strip() == u'查看' or td_element_list[4].text.strip() == u'详情':
                    link_1 = td_element_list[4].a['onclick']
                    link = link_1.split("('")[1].split("',")[0]
                    # print 'link:', self.values_before, link
                    detail_list = self.get_gu_dong_detail(link)
                    # print 'detail_list:', detail_list
                    self.values_before.update(detail_list)
                    # print "values_before:", values_before
                    self.json_result['Shareholder_Info'].append({})
                    self.json_result['Shareholder_Info'][-1] = self.values_before
                    self.values_before = {}
                elif th_element_list[4].text.strip() == u'公示日期':
                    self.json_result['Shareholder_Info'].append({})
                    self.values_before.pop('Shareholder_Info:announceddate')
                    self.json_result['Shareholder_Info'][-1] = self.values_before
                    self.values_before = {}
                else:
                    self.json_result['Shareholder_Info'].append({})
                    self.json_result['Shareholder_Info'][-1] = self.values_before
                    self.values_before = {}
                # for detail_json in detail_list:
                #     for k in detail_json:
                #         if k == 'Shareholder_Info:subscripted_capital':
                #             values_before['Shareholder_Info:subscripted_capital'] = detail_json[k]
                #         elif k == 'Shareholder_Info:actualpaid_capital':
                #             values_before['Shareholder_Info:actualpaid_capital'] = detail_json[k]
            else:
                self.json_result['Shareholder_Info'].append({})
                self.json_result['Shareholder_Info'][-1] = self.values_before
                self.values_before = {}
            for i in range(len(self.json_result['Shareholder_Info'])):
                self.json_result['Shareholder_Info'][i]['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc,  '04', self.cur_zch, self.today, i+1)
                self.json_result['Shareholder_Info'][i]['Shareholder_Info' + ':registrationno'] = self.cur_zch
                self.json_result['Shareholder_Info'][i]['Shareholder_Info' + ':enterprisename'] = self.cur_mc
                self.json_result['Shareholder_Info'][i]['Shareholder_Info' + ':id'] = i+1
            # print "self.json_result['Shareholder_Info']", self.json_result['Shareholder_Info']

    def get_gu_dong_detail(self, link):
        """
        查询股东详情信息
        :param link:
        :return:
        """
        value = {}
        detail_dict_list = []
        rjmx_list = []
        sjmx_list = []
        rjmx_dict = dict()
        sjmx_dict = dict()
        t = 1
        # cookies={
        #     'BSFIT_DEVICEID' :' cF30T1dM1X2IaWbE69hRfE_gytWPzMtwBEBvtXi8w4mh2zc-xiv-Fs9AdI9iormkuLJBWsWkRVmnnF7ZpfVcNCsC_L5HqPHIW2wW-4FZZSy9TJYnkOEETNHGWz1yUV-jSQapGIDn4v8WfOLyRkUKndV0TuyRu0dg',
        #     # 'BSFIT_OkLJUJ' :'FDOYEcTM57aH9t6fuUmah7E4a1Y31ZgG',
        #     # 'BSFIT_EXPIRATION' : '1506722388762'
        # }
        url = 'http://hb.gsxt.gov.cn/queryInvDetailAction.jspx?invId='+link
        # print 'gudong_url', url
        for i in range(5):
            try:
                r = self.get_request(url, headers=self.headers, cookies=self.cookie)
                if u'认缴额' not in r.text:
                    t += 1
                    self.info(u'第%d次获取股东详情。。。' % t)
                    continue
                else:
                    break
            except Exception, e:
                if '-> 500' in str(e):
                    return value
                pass
        # print u'股东详情',r.text
        soup = BeautifulSoup(r.text, 'lxml')
        gudong_table = soup.find('table', class_='detailsList')
        table_element_num = len(soup.find_all(class_='detailsList'))
        # print 'gudong_table', gudong_table
        gudong_tr_element_list = gudong_table.find_all('tr')
        if len(gudong_tr_element_list) == 3:
            value['Shareholder_Info:shareholder_name'] = gudong_tr_element_list[0].find('td').text.strip()
            value['Shareholder_Info:subscripted_capital'] = gudong_tr_element_list[1].find('td').text.strip()
            if value['Shareholder_Info:subscripted_capital']:
                if u'美元' in value['Shareholder_Info:subscripted_capital']:
                    value['Shareholder_Info:subscripted_capital'] = value['Shareholder_Info:subscripted_capital'] +  u'万美元'
                elif u'港元' in value['Shareholder_Info:subscripted_capital']:
                    value['Shareholder_Info:subscripted_capital'] = value['Shareholder_Info:subscripted_capital'] +  u'万港元'
                else:
                    value['Shareholder_Info:subscripted_capital'] = value['Shareholder_Info:subscripted_capital'] +  u'万元'
            value['Shareholder_Info:actualpaid_capital'] = gudong_tr_element_list[2].find('td').text.strip()
        # print "value['Shareholder_Info:actualpaid_capital']", value['Shareholder_Info:actualpaid_capital']
        if table_element_num > 1:
            renjiao_table = soup.find_all(class_='detailsList')[1]
            renjiao_tr_list = renjiao_table.find_all('tr')[1:]
            renjiao_th_list = renjiao_table.find_all('th')
            try:
                if renjiao_tr_list[0].find_all('td'):
                    value['Shareholder_Info:subscripted_method'] = renjiao_tr_list[0].find_all('td')[0].text.strip()
                    value['Shareholder_Info:subscripted_amount'] = renjiao_tr_list[0].find_all('td')[1].text.strip()
                    value['Shareholder_Info:subscripted_time'] = renjiao_tr_list[0].find_all('td')[2].text.strip()
            except:
                pass
            for tr_element in renjiao_tr_list:
                td_element_list = tr_element.find_all('td')
                col_nums = len(td_element_list)
                for j in range(col_nums):
                    col_dec = renjiao_th_list[j].text.strip().replace('\n', '')
                    col = gudong_column_dict[col_dec]
                    val = td_element_list[j].text.strip().replace('\n', '')
                    rjmx_dict[col] = val
                    if u'相关数据' in rjmx_dict[u'认缴出资方式']:
                       rjmx_dict[u'认缴出资方式'] = ''
                       rjmx_dict[u'认缴出资额（万元）']= ''
                       rjmx_dict[u'认缴出资日期']= ''
                    else:
                        rjmx_dict[col] = val
                rjmx_list.append(rjmx_dict)
                rjmx_dict = {}
        value['Shareholder_Info:rjmx'] = rjmx_list    # 认缴明细信息
        if table_element_num == 3:
            shijiao_table = soup.find_all(class_='detailsList')[2]
            shijiao_tr_list = shijiao_table.find_all('tr')[1:]
            shijiao_th_list = shijiao_table.find_all('th')
            try:
                if shijiao_tr_list[0].find_all('td'):
                    td_list = shijiao_tr_list[0].find_all('td')
                    value['Shareholder_Info:actualpaid_method'] = td_list[0].text.strip()
                    value['Shareholder_Info:actualpaid_amount'] = td_list[1].text.strip()
                    value['Shareholder_Info:actualpaid_time'] = td_list[2].text.strip()
            except:
                pass
            for tr_element in shijiao_tr_list:
                td_element_list = tr_element.find_all('td')
                col_nums = len(td_element_list)
                for j in range(col_nums):
                    col_dec = shijiao_th_list[j].text.strip().replace('\n', '')
                    col = gudong_column_dict[col_dec]
                    val = td_element_list[j].text.strip().replace('\n', '')
                    sjmx_dict[col] = val
                    if u'相关数据' in sjmx_dict[u'实缴出资方式']:
                       sjmx_dict[u'实缴出资方式'] = ''
                       sjmx_dict[u'实缴出资额（万元）']= ''
                       sjmx_dict[u'实缴出资日期']= ''
                    else:
                        sjmx_dict[col] = val
                sjmx_list.append(sjmx_dict)
                sjmx_dict = {}
        value['Shareholder_Info:sjmx'] = sjmx_list
        return value

    def load_touziren(self, table_element):
        tr_element_list = table_element.find_all("tr")
        th_element_list = table_element.find_all('th')[1:]
        jsonarray = []
        values = {}
        id = 1
        for tr_element in tr_element_list[1:]:
            td_element_list = tr_element.find_all('td')[1:]
            col_nums = len(th_element_list)
            for i in range(col_nums):
                col_dec = th_element_list[i].get_text().strip().replace('\n', '')
                col = touziren_column_dict[col_dec]
                # print 'col_dec', i, col_dec, col
                td = td_element_list[i]
                val = td.get_text().strip()
                values[col] = val
            values['Shareholder_Info:registrationno'] = self.cur_code
            values['Shareholder_Info:enterprisename'] = self.cur_mc
            values['Shareholder_Info:id'] = str(id)
            values['rowkey']=self.cur_mc+'_02_'+self.cur_code+'_'+self.time+str(id)
            jsonarray.append(values)
            values = {}
            id += 1
        self.json_result['Shareholder_Info'] = jsonarray
#         json_touziren=json.dumps(jsonarray,ensure_ascii=False)
#         print 'json_touziren',json_touziren

    def load_biangeng(self, table_element):
        self.info(u'解析变更信息...')
        # print table_element
        if u'共查询' in table_element.text or u'页' in table_element.text:
            pages = table_element.find(class_="ax_image fenye").find_all('li')[1].text.strip()
            page_num = int(pages.replace(u'共', '').replace(u'页', ''))
            print 'page_num', page_num
            tr_element_list = table_element.find_all("tr")[1:]
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
                    if val.endswith(u'更多'):
                        valmore=td.find(id='allWords').get_text().strip().replace('\n','')
                        values[col] = valmore
                    else:
                        values[col] = val
                values['Changed_Announcement:registrationno']=self.cur_code
                values['Changed_Announcement:enterprisename']=self.cur_mc
                values['Changed_Announcement:id']=str(id)
                values['rowkey']=self.cur_mc+'_05_'+self.cur_code+'_'+self.time+str(id)
                jsonarray.append(values)
                values = {}
                id += 1
            if page_num > 1:
                # Ref = 'http://hb.gsxt.gov.cn/company/detail.jspx?id='+self.tag_a+'&jyzk=jyzc'
                # print 'Ref', Ref
                # headers = {"User-Agent":  'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0',
                #            "Referer":Ref,}
                # url_1 = "http://dfp2.bangruitech.com/public/generate/jsonp?algID=DxbncDlc3j&hashCode=47DEQpj8HBSa-_TImW-5JCeuQeRkm5NMpJWZG3hSuFU&FMQw=0&q4f3=zh-CN&VPIf=1&custID=51&VEek=unknown&dzuS=27.0%20r0&yD16=0&EOQP=49a9fbfe2beb0490836324ceb234fef4&lEnu=3232235916&jp76=bb5032aedcaa9cca45f29e44506d1288&hAqN=Win32&platform=WEB&ks0Q=93b5994b1daea02ec4a30a4f9c1a569c&TeRS=1040x1920&tOHY=24xx1080x1920&Fvje=i1l1o1s1&q5aJ=-8&wNLf=99115dfb07133750ba677d055874de87&0aew=Mozilla/5.0%20"
                # r_1 = self.get_request(url=url_1, headers=self.headers)
                # # print r_1.text
                # _cookie = r_1.text.split('dfp":"')[1].split('"')[0]
                # cookie ={'BSFIT_DEVICEID' :_cookie}
                cookie ={'BSFIT_DEVICEID' :'bw_VVhhywG9PWeDD5SwTkik0GMxRmDQ75sTw-RpqvWdiDC069No1MmaGPgZQ9B2Ci5W8UzgApsMKi-TdxZXZsOdOi-M5rePoe-BzaSuOBr2mxOObjuGSotK62af9xkX-p45InO926n-slPbbKUJ2vR5FtUb1uamM'}
                for p in range(page_num-1):
                    url = "http://hb.gsxt.gov.cn/business/QueryAltList.jspx?pno="+str(p+2)+'&order=0&mainId=' + self.tag_a
                    for i in range(20):
                        r = self.get_request(url, cookies=self.cookie)
                        if r.status_code != 200:
                            continue
                    # print u'变更多页url',url
                    soup = BeautifulSoup(r.text, 'html5lib')
                    table_element = soup.find(class_='ax_table liebiaoxinxin')
                    # print u'变更多页内容',table_element
                    tr_element_list = table_element.find_all("tr")[1:]
                    th_element_list = table_element.find_all('th')[1:]
                    id = 5*(p+1)+1
                    for tr_element in tr_element_list:
                        td_element_list = tr_element.find_all('td')[1:]
                        col_nums = len(th_element_list)
                        for i in range(col_nums):
                            col_dec = th_element_list[i].text.strip().replace('\n', '')
                            col = biangeng_column_dict[col_dec]
                            td = td_element_list[i]
                            val = td.get_text().strip()
                            if val.endswith(u'更多'):
                                valmore=td.find(id='allWords').get_text().strip().replace('\n','')
                                values[col] = valmore
                            else:
                                values[col] = val
                        values['Changed_Announcement:registrationno']=self.cur_code
                        values['Changed_Announcement:enterprisename']=self.cur_mc
                        values['Changed_Announcement:id']=str(id)
                        values['rowkey']=self.cur_mc+'_05_'+self.cur_code+'_'+self.time+str(id)
                        jsonarray.append(values)
                        values = {}
                        id += 1
            self.json_result['Changed_Announcement'] = jsonarray
        else:
            return None
#         json_biangeng=json.dumps(jsonarray,ensure_ascii=False)
#         print 'json_biangeng',json_biangeng

    def load_chengyuanmingce(self, table_element):
        self.info(u'解析成员名册信息...')
        # print table_element
        jsonarray = []
        values = {}
        if u'共计' in table_element.text or u'条信息' in table_element.text:
            items = table_element.find("p").find_all('span')[1].text.strip()
            item_num = int(items.split(u'共计')[1].split(u'条信息')[0])
            # print 'item_num', item_num
            if item_num <= 16:
                tr_element_list = table_element.find_all(class_="keyPerInfo")
                id = 1
                for tr_element in tr_element_list:
                    values['KeyPerson_Info:keyperson_name'] = tr_element.find('span').text.strip().replace('\n', '')
                    # print 'keyperson_name', tr_element.find('span')
                    values['KeyPerson_Info:registrationno'] = self.cur_code
                    values['KeyPerson_Info:enterprisename'] = self.cur_mc
                    values['KeyPerson_Info:id'] = str(id)
                    values['rowkey'] = self.cur_mc+'_06_'+self.cur_code+'_'+self.time+str(id)
                    jsonarray.append(values)
                    values = {}
                    id += 1
            else:
                # print 'table_element', table_element
                # print 'branch_uuid_1', type(table_element.find(class_='channelone')), table_element.find(class_='channelone')
                # branch_uuid_1 = table_element.find('a', class_='channelone').a['onclick']
                branch_uuid_1 = table_element.find('a', class_='channelone').get('onclick')
                branch_uuid = branch_uuid_1.split("?id=")[1].split("')")[0]
                branch_num = str(item_num//16)
                host = 'http://hb.gsxt.gov.cn/business/loadMoreMainStaff.jspx?uuid='
                href = host+branch_uuid+'&order='+branch_num
                # print u'主要人员url', href
                for i in range(8):
                    r = self.get_request(href, headers=self.headers)
                    if r.status_code != 200:
                        continue
                soup = BeautifulSoup(r.text, 'lxml')
                tr_element_list = soup.find_all(class_="keyPerInfo")
                id = 1
                for tr_element in tr_element_list:
                    values['KeyPerson_Info:keyperson_name'] = tr_element.find('span').text.strip().replace('\n', '')
                    values['KeyPerson_Info:registrationno'] = self.cur_code
                    values['KeyPerson_Info:enterprisename'] = self.cur_mc
                    values['KeyPerson_Info:id'] = str(id)
                    values['rowkey'] = self.cur_mc+'_06_'+self.cur_code+'_'+self.time+str(id)
                    jsonarray.append(values)
                    values = {}
                    id += 1
            self.json_result['KeyPerson_Info'] = jsonarray
        else:
            return None

    def load_zhuyaorenyuan(self, table_element):
        self.info(u'解析主要人员信息...')
        # print u'主要人员', table_element
        jsonarray = []
        values = {}
        if self.item:
            id = 1
            if self.item <= 16:
                tr_element_list = table_element.find_all(class_="keyPerInfo")
                for tr_element in tr_element_list:
                    values['KeyPerson_Info:keyperson_name'] = tr_element.find_all('p')[0].text.strip().replace('\n', '')
                    values['KeyPerson_Info:keyperson_position'] = tr_element.find_all('p')[1].text.strip().replace('\n', '')
                    values['KeyPerson_Info:registrationno'] = self.cur_code
                    values['KeyPerson_Info:enterprisename'] = self.cur_mc
                    values['KeyPerson_Info:id'] = str(id)
                    values['rowkey'] = self.cur_mc+'_06_'+self.cur_code+'_'+self.time+str(id)
                    jsonarray.append(values)
                    values = {}
                    id += 1
            else:
                host = 'http://hb.gsxt.gov.cn/business/loadMoreMainStaff.jspx?uuid='
                href = host+self.branch_uuid+'&order=' + self.branch_num
                # print u'主要人员url', href
                for i in range(8):
                    r = self.get_request(href, headers=self.headers)
                    if r.status_code != 200:
                        continue
                soup = BeautifulSoup(r.text, 'lxml')
                tr_element_list = soup.find_all(class_="keyPerInfo")
                for tr_element in tr_element_list:
                    values['KeyPerson_Info:keyperson_name'] = tr_element.find_all('p')[0].text.strip().replace('\n', '')
                    values['KeyPerson_Info:keyperson_position'] = tr_element.find_all('p')[1].text.strip().replace('\n', '')
                    values['KeyPerson_Info:registrationno'] = self.cur_code
                    values['KeyPerson_Info:enterprisename'] = self.cur_mc
                    values['KeyPerson_Info:id'] = str(id)
                    values['rowkey'] = self.cur_mc+'_06_'+self.cur_code+'_'+self.time+str(id)
                    jsonarray.append(values)
                    values = {}
                    id += 1
            self.json_result['KeyPerson_Info'] = jsonarray
        else:
            return None
        # json_zhuyaorenyuan=json.dumps(jsonarray,ensure_ascii=False)
        # print 'json_zhuyaorenyuan',json_zhuyaorenyuan

if __name__ == "__main__":
    searcher = HuBeiSearcher()
    # args_dict = get_args(湖北中牛建设有限公司)
    # searcher.delete_tag_a_from_db(u'武汉斯博兰花园酒店管理有限公司')
    searcher.submit_search_request(u"武汉斯博兰花园酒店管理有限公司")
    # print json.dumps(searcher.json_result, ensure_ascii=False)
