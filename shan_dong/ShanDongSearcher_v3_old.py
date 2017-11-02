#coding=utf-8
import PackageTool
import requests
import os
from PIL import Image
from bs4 import BeautifulSoup
import json
import re
from ShanDongConfig import *
import datetime
from requests.exceptions import RequestException
import sys
import time
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from gs import MSSQL
import random
import urllib
import subprocess
# from Tables_dict import *
from gs.Searcher import Searcher
from gs.Searcher import get_args
from gs.KafkaAPI import KafkaAPI
import requests
from gs.TimeUtils import *
import hashlib
import uuid
requests.packages.urllib3.disable_warnings()
m = hashlib.md5()
reload(sys)
sys.setdefaultencoding('utf-8')


class ShanDongSearcher(Searcher):
    json_result = {}
    load_func_dict = {}
    pattern = re.compile("\s")
    cur_mc = ''
    cur_zch = ''
    code = ''
    save_tag_a = True
    tag_a = None
    resdetail = None
    # token = None

    def __init__(self):
        super(ShanDongSearcher, self).__init__(use_proxy=False)
        # super(ShanDongSearcher, self).__init__(use_proxy=True)
        self.headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Accept-Encoding': 'gzip, deflate',
                        'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'Connection': 'keep-alive',
                        'Host': '218.57.139.24',
                        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0'}
        self.host = 'http://218.57.139.24/pub/gsgsdetail/'
        # enttype = ''
        self.set_config()
        self.log_name = self.topic + "_" + str(uuid.uuid1())
        self.corp_id = ''
        self.corp_org = ''
        self.enttype = ''
        self.encrptpripid = ''

    def set_config(self):
        self.plugin_path = os.path.join(sys.path[0], r'..\shan_dong\ocr\shandong.bat')
        self.group = 'Crawler'  # 正式
        self.kafka = KafkaAPI("GSCrawlerResult")  # 正式
        # self.group = 'CrawlerTest'  # 测试
        # self.kafka = KafkaAPI("GSCrawlerTest")  # 测试
        self.topic = 'GsSrc37'
        self.province = u'山东省'
        self.kafka.init_producer()

    def get_tag_a_from_page(self, keyword, flags=True):
        for t in range(10):
            yzm = self.get_yzm()
            secode = hashlib.md5(yzm).hexdigest()
            # print 'secode',secode
            self.headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                            'Accept-Encoding': 'gzip, deflate',
                            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                            'Content-Type': 'application/x-www-form-urlencoded',
                            'Connection': 'keep-alive',
                            'Host': '218.57.139.24',
                            'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0'}
            url1 = 'http://218.57.139.24/'
            r = self.get_request(url1)
            bs1 = BeautifulSoup(r.text, 'lxml')
            token = bs1.select('meta')[3].attrs['content']
            url3 = 'http://218.57.139.24/pub/indsearch'
            params = {'_csrf': token, 'kw': keyword, 'secode': secode}
            # print 'params',params
            self.headers['Referer'] = 'http://218.57.139.24/pub/indsearch'
            r = self.post_request(url3, data=params)
            r.encoding = 'utf8'
            if u'计算错误' not in r.text:
                bs = BeautifulSoup(r.text, 'lxml').text.strip()
                if re.search(u'(?<=enckeyword).*(?=;)', bs):
                    code = re.search(u'(?<=enckeyword).*(?=;)', bs).group().replace('=','').replace("'",'').replace("'",'')
                    break
                else:
                    continue
        params1 = {'param': code}
        self.headers['X-CSRF-TOKEN'] = token
        url4 = 'http://218.57.139.24/pub/search'
        r = self.post_request(url4, data=params1)
        r.encoding = 'utf8'
        soup = BeautifulSoup(r.text, 'lxml')
        search_result_text = soup.text.strip()
        tag_content = json.loads(search_result_text)
        if len(tag_content) > 0:
            self.cur_mc = tag_content[0].get('entname', '').replace('(', u'（').replace(')', u'）')
            regno = tag_content[0].get('regno', '')
            if flags:
                if keyword == self.cur_mc:
                    self.cur_zch = tag_content[0].get('regno', '')
                    encrptpripid = tag_content[0].get('encrptpripid', '')
                    enttype = tag_content[0].get('enttype', '')
                    self.encrptpripid = encrptpripid
                    tag_a = self.host + enttype + '/' + encrptpripid
                    self.tag_a = tag_a
                    return tag_a
            elif keyword == regno:
                self.cur_mc = keyword
                self.cur_zch = tag_content[0].get('regno', '')
                encrptpripid = tag_content[0].get('encrptpripid', '')
                enttype = tag_content[0].get('enttype', '')
                self.encrptpripid = encrptpripid
                tag_a = self.host + enttype + '/' + encrptpripid
                self.tag_a = tag_a
                return tag_a
        else:
            return None

    def get_search_args(self, tag_a, keyword):
        self.tag_a = tag_a
        if tag_a:
            return 1
        else:
            return 0

    def download_yzm(self):
        image_url = 'http://218.57.139.24/securitycode'
        r = self.get_request(image_url)
        yzm_path = self.get_yzm_path()
        with open(yzm_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
                    f.flush()
            f.close()
        return yzm_path

    def parse_detail(self):
        tag_a = self.tag_a
        self.headers['Referer'] = 'http://218.57.139.24/pub/indsearch'
        # params = {'pripid': param_pripid, 'type': param_type}
        r = self.get_request(url=tag_a)
        self.resdetail = BeautifulSoup(r.text, 'lxml')
        # print 'parse_detail', self.resdetail
        self.get_ji_ben(tag_a)
        self.get_gu_dong(tag_a)
        self.get_bian_geng(tag_a)
        if u'主要人员信息' in self.resdetail.text:
            token = self.resdetail.select('meta')[3].attrs['content']
            self.token = token
            self.get_zhu_yao_ren_yuan(tag_a)
        elif u'主管部门（出资人）信息' in self.resdetail.text:
            token = self.resdetail.select('meta')[2].attrs['content']
            self.token = token
            self.get_zhu_guan_bu_men(tag_a)
        self.get_fen_zhi_ji_gou(tag_a)
        self.get_qing_suan(tag_a)
        self.get_dong_chan_di_ya(tag_a)
        self.get_gu_quan_chu_zhi(tag_a)
        self.get_xing_zheng_chu_fa(tag_a)
        self.get_jing_ying_yi_chang(tag_a)
        self.get_yan_zhong_wei_fa(tag_a)
        self.get_chou_cha_jian_cha(tag_a)

    def get_ji_ben(self, tag_a):
        """
        查询基本信息
        :param tag_a:
        :return:
        """
        self.info(u'解析基本信息...')
        family = 'Registered_Info'
        table_id = '01'
        self.json_result[family] = []
        soup = self.resdetail
        token = soup.select('meta')[3].attrs['content']
        self.token = token
        table_element = soup.find(id='jibenxinxi').find(class_='detailsList')
        td_list = table_element.select('tr > td')
        th_list = table_element.select('tr > th')[1:]
        result_json = [{}]
        for i in range(len(td_list)):
            th = th_list[i]
            td = td_list[i]
            desc = self.pattern.sub('', th.text)
            val = self.pattern.sub('', td.text)
            if len(desc) > 0:
                if u'注册号/统一社会信用代码' in desc and len(val) == 18 or u'注册号' in desc and len(val) == 18:
                    result_json[0][u'社会信用代码'] = val
                    result_json[0][u'注册号/统一社会信用代码'] = val
                    self.cur_zch = val
                    result_json[0][u'注册号'] = ''
                if u'注册号/统一社会信用代码' in desc and len(val) != 18 or u'注册号' in desc and len(val) != 18:
                    result_json[0][u'社会信用代码'] = ''
                    result_json[0][u'注册号'] = val
                    result_json[0][u'注册号/统一社会信用代码'] = val
                    self.cur_zch = val
                result_json[0][desc] = val
        # print 'result_json',result_json
        for j in result_json:
            self.json_result[family].append({})
            self.cur_mc = j[u'名称']
            for k in j:
                col = family + ':' + ji_ben_dict[k]
                val = j[k]
                self.json_result[family][-1][col] = val
        self.json_result[family][-1]['rowkey'] = '%s_%s_%s_' % (self.cur_mc, table_id, self.cur_zch)
        self.json_result[family][-1][family + ':registrationno'] = self.cur_zch
        self.json_result[family][-1][family + ':enterprisename'] = self.cur_mc
        self.json_result[family][-1][family + ':province'] = u'山东省'
        self.json_result[family][-1][family + ':lastupdatetime'] = get_cur_time()
        # print json.dumps(self.json_result[family], ensure_ascii=False)

    def get_gu_dong(self, tag_a):
        """
        查询股东信息
        :param tag_a:
        :return:
        """
        self.info(u'解析股东信息...')
        family = 'Shareholder_Info'
        table_id = '04'
        self.json_result[family] = []
        soup = self.resdetail
        script_list = soup.select('html > head > script')
        result_text = script_list[-2]
        if 'var czxxliststr' in result_text.text.strip():
            start_idx = result_text.text.index('$(document)')
            result_text = result_text.text[:start_idx]
            gudong_text1 = result_text.split('\n')[1].replace("var czxxliststr ='", '').replace("';", '')
            # print 'gudong_text1', type(gudong_text1) , gudong_text1
            gudong_text = json.loads(gudong_text1)
            # print 'gudong_text', type(gudong_text) , gudong_text
            for j in gudong_text:
                param_invid = j['recid']
                self.param_invid = param_invid
                if param_invid != '':
                    detail_list = self.get_gu_dong_detail(param_invid, tag_a)
                # if len(detail_list) > 0:
                    for detail_json in detail_list:
                        self.json_result[family].append({})
                        for k in detail_json:
                            if k in gu_dong_dict:
                                col = family + ':' + gu_dong_dict[k]
                                val = detail_json[k]
                                self.json_result[family][-1][col] = val
                        for k in j:
                            if k in gu_dong_dict:
                                col = family + ':' + gu_dong_dict[k]
                                val = j[k]
                                if detail_list[0]['lisubconam'] == '':
                                    self.json_result['Shareholder_Info:subscripted_capital'] = ''
                                if detail_list[0]['liacconam'] == '':
                                    self.json_result['Shareholder_Info:actualpaid_capital'] = ''
                                self.json_result[family][-1][col] = val
                else:
                    self.json_result[family].append({})
                    for k in j:
                        if k in gu_dong_dict:
                            col = family + ':' + gu_dong_dict[k]
                            val = j[k]
                            self.json_result[family][-1][col] = val
            for i in range(len(self.json_result[family])):
                self.json_result[family][i]['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.cur_zch, self.today, i+1)
                self.json_result[family][i][family + ':registrationno'] = self.cur_zch
                self.json_result[family][i][family + ':enterprisename'] = self.cur_mc
                self.json_result[family][i][family + ':id'] = self.today+str(i+1)
                # print json.dumps(self.json_result[family][i], ensure_ascii=False)
            # print json.dumps(self.json_result[family], ensure_ascii=False)

    def get_gu_dong_detail(self, param_invid, tag_a):
        """
        查询股东详情
        :param tag_a:
        :param param_invid:
        :return:
        """
        detail_dict_list = []
        self.headers['Referer'] = tag_a
        encrptpripid = tag_a.split('/', 7)[6]
        gudongdetai_url = 'http://218.57.139.24/pub/gsnzczxxdetail/'
        url = gudongdetai_url+encrptpripid+'/'+self.param_invid
        # print "url:",url
        r = self.get_request(url=url)
        soup = BeautifulSoup(r.text, 'lxml')
        # print soup
        soup2 = soup.text.strip()
        detail1 = re.findall(r"(?<=[=']).*(?=[';])", soup2)     #寻找对应的值
        czxxstr = detail1[4].strip().replace("'[", '').replace("]'", '')
        czxxstr = json.loads(czxxstr)
        czxxrjstr = detail1[10].strip().replace("'[", '').replace("]'", '')
        czxxrjstr = json.loads(czxxrjstr)
        # print 'czxxrjstr',czxxrjstr
        czxxsjstr = detail1[14].strip().replace("'[", '').replace("]'", '')
        czxxsjstr = json.loads(czxxsjstr)
        # print 'czxxsjstr', czxxsjstr
        if czxxstr:
            if czxxrjstr:
                year1 = czxxrjstr["condate"]["year"]
                year2 = '%d' % year1
                mon1 = czxxrjstr["condate"]["month"]+1
                mon = '%d' % mon1
                day1 = czxxrjstr["condate"]["date"]
                day = '%d' % day1
                if len(year2) == 2:          # 如果是2位数，则是‘19’年，如果是3位数，则是‘20’年
                    year = '19'+year2
                elif len(year2) == 3:
                    year = '20'+year2[1:]
                date = year + u'年'+mon + u'月'+day + u'日'
                # print 'date:', date
                czxxstr['subtime'] = date
                czxxstr['subconform'] = czxxrjstr["conform"]
                czxxstr['subconam'] = czxxrjstr["subconam"]
            elif not czxxrjstr:
                # print u'认缴为空'
                czxxstr['lisubconam'] = ''
                # print u'czxxstr认缴',czxxstr['lisubconam']
            if czxxsjstr:
                year1 = czxxsjstr["condate"]["year"]
                year2 = '%d' % year1
                mon1 = czxxsjstr["condate"]["month"]+1
                mon = '%d' % mon1
                day1 = czxxsjstr["condate"]["date"]
                day = '%d' % day1
                if len(year2) == 2:          # 如果是2位数，则是‘19’年，如果是3位数，则是‘20’年
                    year = '19'+year2
                elif len(year2) == 3:
                    year = '20'+year2[1:]
                date = year + u'年'+mon+u'月'+day + u'日'
                czxxstr['acttime'] = date
                czxxstr['actconform'] = czxxsjstr["conform"]
                czxxstr['actconam'] = czxxsjstr["acconam"]
            elif not czxxsjstr:
                # print u'实际出资为空'
                czxxstr['liacconam'] = ''
                # print u'czxxstr实际出资',czxxstr['liacconam']
        detail_dict_list.append(czxxstr)
        # print 'detail_dict_list' ,detail_dict_list
        return detail_dict_list

    def get_bian_geng(self, tag_a):
        """
        查询变更信息
        :param tag_a:
        :return:
        """
        self.info(u'解析变更信息...')
        family = 'Changed_Announcement'
        table_id = '05'
        self.json_result[family] = []
        soup = self.resdetail
        script_list = soup.select('html > head > script')
        result_text = script_list[-2]
        # print u'查询变更信息',result_text
        if 'var bgsxliststr' in result_text.text.strip() and 'var czxxliststr' in result_text.text.strip():
            start_idx = result_text.text.index('$(document)')
            result_text = result_text.text[:start_idx]
            biangeng_text1 = result_text.split('\n')[2]
            biangeng_text = biangeng_text1.replace("var bgsxliststr ='",'').replace("';",'')
            biangeng_text = json . loads(biangeng_text)
        elif 'var bgsxliststr' in result_text.text.strip() and 'var czxxliststr' not in result_text.text.strip():
            start_idx = result_text.text.index('$(document)')
            result_text = result_text.text[:start_idx]
            biangeng_text1 = result_text.split('\n')[1]
            biangeng_text = biangeng_text1.replace("var bgsxliststr ='",'').replace("';",'')
            biangeng_text = json .loads(biangeng_text)
        result_json = biangeng_text
        if result_json != '[]':
            for j in result_json:
                self.json_result[family].append({})
                year1 = j["altdate"]["year"]
                year2 = '%d' % year1
                mon1 = j["altdate"]["month"]+1
                mon = '%d' % mon1
                day1 = j["altdate"]["date"]
                day = '%d' % day1
                if len(year2) == 2:          # 如果是2位数，则是‘19’年，如果是3位数，则是‘20’年
                    year = '19' + year2
                elif len(year2) == 3:
                    year = '20' + year2[1:]
                date = year + u'年'+mon+u'月'+day + u'日'
                j['altdate'] = date
                for k in j:
                    if k in bian_geng_dict:
                        col = family + ':' + bian_geng_dict[k]
                        val = j[k]
                        self.json_result[family][-1][col] = val
            for i in range(len(self.json_result[family])):
                self.json_result[family][i]['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.cur_zch, self.today, i+1)
                self.json_result[family][i][family + ':registrationno'] = self.cur_zch
                self.json_result[family][i][family + ':enterprisename'] = self.cur_mc
                self.json_result[family][i][family + ':id'] = self.today + str(i + 1)
            # print json.dumps(self.json_result[family], ensure_ascii=False)

    def get_zhu_yao_ren_yuan(self, tag_a):
        """
        查询主要人员信息
        :param tag_a:
        :return:
        """
        self.info(u'解析主要人员信息...')
        family = 'KeyPerson_Info'
        table_id = '06'
        self.json_result[family] = []
        self.headers['X-CSRF-TOKEN'] = self.token
        zyry_url = 'http://218.57.139.24/pub/gsryxx/'
        enttype = tag_a.split('/', 7)[5]
        url = zyry_url + enttype
        encrptpripid = tag_a.split('/', 7)[6]
        params = {'encrpripid': encrptpripid}
        r = self.post_request(url=url, data=params)
        soup = BeautifulSoup(r.text, 'lxml')
        # print  soup
        zhuyaorenyuan_text = soup.text.strip()
        zhuyaorenyuan_text = json.loads(zhuyaorenyuan_text)
        for j in zhuyaorenyuan_text:
            self.json_result[family].append({})
            for k in j:
                if k in zhu_yao_ren_yuan_dict:
                    col = family + ':' + zhu_yao_ren_yuan_dict[k]
                    val = j[k]
                    self.json_result[family][-1][col] = val
        for i in range(len(self.json_result[family])):
            self.json_result[family][i]['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.cur_zch, self.today, i+1)
            self.json_result[family][i][family + ':registrationno'] = self.cur_zch
            self.json_result[family][i][family + ':enterprisename'] = self.cur_mc
            self.json_result[family][i][family + ':id'] = self.today + str(i + 1)
            self.json_result[family][i][family + ':keyperson_no'] = str(i + 1)
            # print json.dumps(self.json_result[family][i], ensure_ascii=False)
        # print json.dumps(self.json_result[family], ensure_ascii=False)

    def get_zhu_guan_bu_men(self, tag_a):
        """
        查询主管部门信息
        :param tag_a:
        :return:
        """
        family = 'DIC_Info'
        table_id = '10'
        self.json_result[family] = []
        self.headers['X-CSRF-TOKEN'] = self.token
        url = 'http://218.57.139.24/pub/gsczxx'
        encrptpripid = tag_a.split('/', 7)[6]
        params = {'encrpripid': encrptpripid}
        # print u'主管部门url', url
        # print u'主管部门params', params
        r = self.post_request(url=url, data=params)
        soup = BeautifulSoup(r.text, 'lxml')
        # print  soup
        zhuguanbumen_text = soup.text.strip()
        zhuguanbumen_text = json.loads(zhuguanbumen_text)
        # print u'主管部门' ,  zhuguanbumen_text
        for j in zhuguanbumen_text:
            self.json_result[family].append({})
            for k in j:
                if k in DICInfo_column_dict:
                    col = family + ':' + DICInfo_column_dict[k]
                    val = j[k]
                    self.json_result[family][-1][col] = val
        for i in range(len(self.json_result[family])):
            self.json_result[family][i]['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.cur_zch, self.today, i+1)
            self.json_result[family][i][family + ':registrationno'] = self.cur_zch
            self.json_result[family][i][family + ':enterprisename'] = self.cur_mc
            self.json_result[family][i][family + ':id'] = self.today + str(i + 1)
            self.json_result[family][i][family + ':dic_no'] = str(i + 1)
            # print json.dumps(self.json_result[family][i], ensure_ascii=False)
        # print json.dumps(self.json_result[family], ensure_ascii=False)

    def get_fen_zhi_ji_gou(self, tag_a):
        """
        查询分支机构信息
        :param tag_a:
        :return:
        """
        self.info(u'解析分支机构信息...')
        family = 'Branches'
        table_id = '08'
        self.json_result[family] = []
        self.headers['X-CSRF-TOKEN'] = self.token
        fenzhijg_url = 'http://218.57.139.24/pub/gsfzjg/'
        enttype = tag_a.split('/', 7)[5]
        url = fenzhijg_url + enttype
        encrptpripid = tag_a.split('/', 7)[6]
        params = {'encrpripid': encrptpripid}
        r = self.post_request(url=url, data=params)
        if r.text == u'':
            return None
        soup = BeautifulSoup(r.text, 'lxml')
        if soup:
            fenzhijg_text = soup.text.strip()
            fenzhijg_text = json.loads(fenzhijg_text)
            # print u'分支机构网站', fenzhijg_text
            for j in fenzhijg_text:
                self.json_result[family].append({})
                for k in j:
                    if k in fen_zhi_ji_gou_dict:
                        col = family + ':' + fen_zhi_ji_gou_dict[k]
                        val = j[k]
                        self.json_result[family][-1][col] = val
            for i in range(len(self.json_result[family])):
                self.json_result[family][i]['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.cur_zch, self.today, i+1)
                self.json_result[family][i][family + ':registrationno'] = self.cur_zch
                self.json_result[family][i][family + ':enterprisename'] = self.cur_mc
                self.json_result[family][i][family + ':id'] = self.today + str(i + 1)
                self.json_result[family][i][family + ':branch_no'] = str(i + 1)
                # print json.dumps(self.json_result[family][i], ensure_ascii=False)
            # print json.dumps(self.json_result[family], ensure_ascii=False)

    def get_qing_suan(self, tag_a):
        pass

    def get_dong_chan_di_ya(self, tag_a):
        """
        查询动产抵押信息
        :param tag_a:
        :return:
        """
        self.info(u'解析动产抵押信息...')
        family = 'Chattel_Mortgage'
        table_id = '11'
        self.json_result[family] = []
        self.headers['X-CSRF-TOKEN'] = self.token
        url = 'http://218.57.139.24/pub/gsdcdy'
        encrptpripid = tag_a.split('/', 7)[6]
        params = {'encrpripid': encrptpripid}
        r = self.post_request(url=url, data=params)
        soup = BeautifulSoup(r.text, 'lxml')
        # print soup
        dongchandy_text = soup.text.strip()
        dongchandy_text = json.loads(dongchandy_text)
        for j in dongchandy_text:
            self.json_result[family].append({})
            year1 = j["regidate"]["year"]
            year2 = '%d' % year1
            mon1 = j["regidate"]["month"]+1
            mon = '%d' % mon1
            day1 = j["regidate"]["date"]
            day = '%d' % day1
            if len(year2) == 2:          # 如果是2位数，则是‘19’年，如果是3位数，则是‘20’年
                year = '19'+year2
            elif len(year2) == 3:
                year = '20'+year2[1:]
            date = year + u'年'+mon+u'月'+day + u'日'
            j['regidate'] = date
            type1 = json.loads(j['type'] )
            if type1 == 1:
                j['type'] = u'有效'
            elif type1 == 2:
                j['type'] = u'无效'
            djbh = j['morregcno']
            diya_detail = self.get_diya_detail(djbh, encrptpripid)
            for k in j:
                if k in dong_chan_di_ya_dict:
                    col = family + ':' + dong_chan_di_ya_dict[k]
                    val = j[k]
                    self.json_result[family][-1][col] = val
                    self.json_result[family][-1].update(diya_detail)
            self.json_result[family][-1]['Chattel_Mortgage:chattelmortgage_guaranteedamount'] = str(self.json_result[family][-1]['Chattel_Mortgage:chattelmortgage_guaranteedamount'])+ u'万元'
        for i in range(len(self.json_result[family])):
            self.json_result[family][i]['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.cur_zch, self.today, i+1)
            self.json_result[family][i][family + ':registrationno'] = self.cur_zch
            self.json_result[family][i][family + ':enterprisename'] = self.cur_mc
            self.json_result[family][i][family + ':id'] = self.today + str(i + 1)
            self.json_result[family][i][family + ':chattelmortgage_no'] = str(i + 1)
        # print json.dumps(self.json_result[family], ensure_ascii=False)

    def get_diya_detail(self, djbh, encrptpripid):
        values = dict()
        diya_detail_new = {'Chattel_Mortgage:dywgk': [{'dywgk:enterprisename': '', 'dywgk:id': '', 'dywgk:registrationno': '', 'rowkey': ''}],\
         'Chattel_Mortgage:dyqrgk': [{'dyqrgk:enterprisename': '', 'dyqrgk:registrationno': '', 'dyqrgk:id': '', 'rowkey': ''}],\
         'Chattel_Mortgage:dcdydj': [{'dcdyzx:dcdy_bdbzqzl': '', 'dcdyzx:dcdy_dbfw': '', 'rowkey': '', 'dcdyzx:dcdy_djjg': '', 'dcdydj:enterprisename': '', 'dcdyzx:dcdy_lxqx': '', 'dcdyzx:dcdy_bz': '', 'dcdyzx:dcdy_djbh': '', 'dcdyzx:dcdy_bdbzqsl': '', 'dcdydj:registrationno': '', 'dcdyzx:dcdy_djrq': ''}],\
          'Chattel_Mortgage:bdbzqgk': [{'bdbzqgk:dbzq_bz': '', 'bdbzqgk:dbzq_fw': '', 'bdbzqgk:dbzq_zl': '', 'bdbzqgk:dbzq_qx': '', 'bdbzqgk:registrationno': '', 'rowkey': '', 'bdbzqgk:enterprisename': '', 'bdbzqgk:dbzq_sl': ''}],'Chattel_Mortgage:dcdybg': [{'dcdybg:dcdy_bgrq': '', 'dcdybg:dcdy_bgnr': ''}]}

        djbh_tran = urllib.quote(djbh.encode('utf8')).replace('%', '%25')
        url = 'http://218.57.139.24/pub/gsdcdydetail/'+encrptpripid+'/'+djbh_tran+'/1'
        try:
            r_1 = self.get_request(url)
            """动产抵押登记信息"""
            dcdydj = list()
            dcdydj_table_id = '63'
            family = 'dcdydj'
            dcdydj_dict = dict()
            soup = BeautifulSoup(r_1.text, 'lxml')
            table_element = soup.find_all(id='qufenkuang')
            dcdydj_table = table_element[0].find_all(class_='detailsList')[0]
            # print 'dcdydj_table', dcdydj_table
            dcdydj_tr_list = dcdydj_table.find_all('tr')
            for tr_element in dcdydj_tr_list[1:]:
                th_element_list = tr_element.find_all('th')
                td_element_list = tr_element.find_all('td')
                col_nums = len(td_element_list)
                for i in range(col_nums):
                    col_dec = th_element_list[i].get_text().strip().replace('\n', '')
                    col = dcdydj_column_dict[col_dec]
                    val = td_element_list[i].get_text().strip().replace('\n', '').replace('\t', '').replace('\r', '')
                    dcdydj_dict[col] = val
            mot_no = dcdydj_dict['dcdyzx:dcdy_djbh']
            mot_date = dcdydj_dict['dcdyzx:dcdy_djrq']
            dcdydj_dict['rowkey'] = '%s_%s_%s_%s' % (self.cur_mc, mot_no,mot_date, dcdydj_table_id)
            dcdydj_dict[family + ':registrationno'] = self.cur_zch
            dcdydj_dict[family + ':enterprisename'] = self.cur_mc
            dcdydj.append(dcdydj_dict)
            values['Chattel_Mortgage:dcdydj'] = dcdydj # 动产抵押登记信息

            """抵押权人概况"""
            family = 'dyqrgk'
            dyqrgk = list()
            dyqrgk_values = dict()
            dyqrgk_table_id = '55' # 抵押权人概况表格
            k = 1
            dyqrgk_table = table_element[0].find_all(class_='detailsList')[1]
            dyqrgk_tr_list = dyqrgk_table.find_all('tr')
            dyqrgk_th_list = dyqrgk_table.find_all('th')[1:-1]
            for tr_element in dyqrgk_tr_list[1:]:
                td_element_list = tr_element.find_all('td')
                col_nums = len(td_element_list)
                for i in range(col_nums):
                    col_dec = dyqrgk_th_list[i].get_text().strip().replace('\n', '')
                    col = dyqrgk_column_dict[col_dec]
                    val = td_element_list[i].get_text().strip().replace('\n', '').replace(' ', '')
                    dyqrgk_values[col] = val
            dyqrgk_values['rowkey'] = '%s_%s_%s_%s_%d' % (self.cur_mc, mot_no,mot_date, dyqrgk_table_id, k)
            dyqrgk_values[family + ':registrationno'] = self.cur_zch
            dyqrgk_values[family + ':enterprisename'] = self.cur_mc
            dyqrgk_values[family + ':id'] = k
            dyqrgk.append(dyqrgk_values)
            k += 1
            values['Chattel_Mortgage:dyqrgk'] = dyqrgk # 抵押权人概况

            """被担保债券概况"""
            family = 'bdbzqgk'
            bdbzqgk = list()
            bdbzqgk_table_id = '56'
            bdbzqgk_dict = dict()
            bdbzqgk_table = table_element[0].find_all(class_='detailsList')[2]
            bdbzqgk_tr_list = bdbzqgk_table.find_all('tr')
            for tr_element in bdbzqgk_tr_list[1:]:
                th_element_list = tr_element.find_all('th')
                td_element_list = tr_element.find_all('td')
                col_nums = len(td_element_list)
                for i in range(col_nums):
                    col_dec = th_element_list[i].get_text().strip().replace('\n', '')
                    col = bdbzqgk_column_dict[col_dec]
                    val = td_element_list[i].get_text().strip().replace('\n', '').replace('\t', '').replace('\r', '')
                    bdbzqgk_dict[col] = val
            bdbzqgk_dict['rowkey'] = '%s_%s_%s_%s' % (self.cur_mc, mot_no,mot_date, bdbzqgk_table_id)
            bdbzqgk_dict[family + ':registrationno'] = self.cur_zch
            bdbzqgk_dict[family + ':enterprisename'] = self.cur_mc
            bdbzqgk.append(bdbzqgk_dict)
            values['Chattel_Mortgage:bdbzqgk'] = bdbzqgk # 被担保债券概况

            """抵押物概况"""
            family = 'dywgk'
            dywgk = list()
            dywgk_table_id = '57'
            dywgk_values = dict()
            k = 1
            dywgk_table = table_element[0].find_all(class_='detailsList')[3]
            dywgk_tr_list = dywgk_table.find_all('tr')
            dywgk_th_list = dywgk_table.find_all('th')[1:-1]
            for tr_element in dywgk_tr_list[1:]:
                td_element_list = tr_element.find_all('td')
                col_nums = len(td_element_list)
                for i in range(col_nums):
                    col_dec = dywgk_th_list[i].get_text().strip().replace('\n', '')
                    col = dywgk_column_dict[col_dec]
                    val = td_element_list[i].get_text().strip().replace('\n', '').replace(' ', '')
                    dywgk_values[col] = val
            dywgk_values['rowkey'] = '%s_%s_%s_%s_%d' % (self.cur_mc, mot_no,mot_date, dywgk_table_id, k)
            dywgk_values[family + ':registrationno'] = self.cur_zch
            dywgk_values[family + ':enterprisename'] = self.cur_mc
            dywgk_values[family + ':id'] = k
            dywgk.append(dywgk_values)
            k += 1
            values['Chattel_Mortgage:dywgk'] = dywgk  # 抵押物概况

            """变更"""
            family = 'dcdybg'
            dybg = list()
            dybg_table_id = '58'
            dybg_values = dict()
            k = 1
            dybg_table = soup.find_all(id='qufenkuang')[1].find(class_='detailsList')
            dybg_tr_list = dybg_table.find_all('tr')
            dybg_th_list = dybg_table.find_all('th')[1:-1]
            for tr_element in dybg_tr_list[1:]:
                td_element_list = tr_element.find_all('td')
                col_nums = len(td_element_list)
                for i in range(col_nums):
                    col_dec = dybg_th_list[i].get_text().strip().replace('\n', '')
                    col = dcdybg_column_dict[col_dec]
                    val = td_element_list[i].get_text().strip().replace('\n', '').replace(' ', '')
                    dybg_values[col] = val
            dybg_values['rowkey'] = '%s_%s_%s_%s_%d' % (self.cur_mc, mot_no,mot_date, dybg_table_id, k)
            dybg_values[family + ':registrationno'] = self.cur_zch
            dybg_values[family + ':enterprisename'] = self.cur_mc
            dybg_values[family + ':id'] = k
            dybg.append(dybg_values)
            k += 1
            values['Chattel_Mortgage:dcdybg'] = dybg  # 抵押物概况
            return values
        except:
            return diya_detail_new

    def get_gu_quan_chu_zhi(self, tag_a):
        """
        查询股权出置信息
        :param tag_a:
        :return:
        """
        self.info(u'解析股权出质信息...')
        family = 'Equity_Pledge'
        table_id = '12'
        self.json_result[family] = []
        self.headers['X-CSRF-TOKEN'] = self.token
        url = 'http://218.57.139.24/pub/gsgqcz'
        encrptpripid = tag_a.split('/', 7)[6]
        params = {'encrpripid': encrptpripid}
        r = self.post_request(url=url, data=params)
        soup = BeautifulSoup(r.text, 'lxml')
        guquancz_text = json.loads(soup.text.strip())
        # print u'股权出资网站', guquancz_text
        for j in guquancz_text:
            self.json_result[family].append({})
            year1 = j["equpledate"]["year"]
            year2 = '%d' % year1
            mon1 = j["equpledate"]["month"]+1
            mon = '%d' % mon1
            day1  = j["equpledate"]["date"]
            day = '%d' % day1
            if len(year2) == 2:          # 如果是2位数，则是‘19’年，如果是3位数，则是‘20’年
                year = '19'+year2
            elif len(year2) == 3:
                year = '20'+year2[1:]
            date = year + u'年'+mon+u'月'+day + u'日'
            j['equpledate'] = date
            type1 = json.loads(j['type'] )
            pass_type = j['type']
            if type1 == 1:
                j['type'] = u'有效'
            elif type1 == 2:
                j['type'] = u'无效'
            djbh = j['equityno']
            self.equity_date = date
            pledge_detail = self.get_pledge_detail(encrptpripid, djbh, pass_type)
            for k in j:
                if k in gu_quan_chu_zhi_dict:
                    pledge_params = dict()
                    col = family + ':' + gu_quan_chu_zhi_dict[k]
                    val = j[k]
                    self.json_result[family][-1][col] = val
                    self.json_result[family][-1].update(pledge_detail)
        for i in range(len(self.json_result[family])):
            self.json_result[family][i]['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.cur_zch, self.today, i+1)
            self.json_result[family][i][family + ':registrationno'] = self.cur_zch
            self.json_result[family][i][family + ':enterprisename'] = self.cur_mc
            self.json_result[family][i][family + ':id'] = self.today + str(i + 1)
            self.json_result[family][i][family + ':equitypledge_no'] = str(i + 1)
            # print json.dumps(self.json_result[family][i], ensure_ascii=False)
        # print json.dumps(self.json_result[family], ensure_ascii=False)

    def get_pledge_detail(self, encrptpripid, djbh, pass_type):
            family = 'gqczzx'
            table_id = '60'
            result_values = dict()
            pledge_list = list()
            values = dict()
            url = 'http://218.57.139.24/pub/gsgqczdetail/'+encrptpripid+'/'+djbh+'/'+pass_type
            r = self.get_request(url)
            # print r.text
            soup = BeautifulSoup(r.text, 'lxml')
            table = soup.find(class_='detailsList')
            table_des = table.find('tr').find('th').text.strip()
            if table_des == u'变更':
                dyqrgk_th_list = table.find_all('th')[1:-1]
                gqcz_tr_list = table.find_all('tr')[2:-1]
                for tr_element in gqcz_tr_list:
                    td_element_list = tr_element.find_all('td')
                    col_nums = len(td_element_list)
                    for i in range(col_nums):
                        col_dec = dyqrgk_th_list[i].get_text().strip().replace('\n', '')
                        col = gqczzx_biangeng_dict[col_dec]
                        val = td_element_list[i].get_text().strip().replace('\n', '')
                        result_values[col] = val
            elif table_des == u'注销':
                values[family + ':gqcz_zxrq'] = table.find_all('tr')[1].find('td').text.strip()
                values[family + ':gqcz_zxyy'] = table.find_all('tr')[2].find('td').text.strip()
            equity_date = self.equity_date.replace(u'年', '-').replace(u'月', '-').replace(u'日', '')  #
            equity_no = djbh
            values['rowkey'] = '%s_%s_%s_%s' % (self.cur_mc,equity_no,equity_date, table_id)
            values[family + ':registrationno'] = self.cur_zch
            values[family + ':enterprisename'] = self.cur_mc
            pledge_list.append(values)
            result_values['Equity_Pledge:gqczzx'] = pledge_list
            return result_values

    def get_xing_zheng_chu_fa(self, tag_a):
        """
        :param tag_a:
        查询行政处罚信息
        """
        self.info(u'解析行政处罚信息...')
        family = 'Administrative_Penalty'
        table_id = '13'
        self.json_result[family] = []
        url = 'http://218.57.139.24/pub/gsxzcfxx'
        encrptpripid = tag_a.split('/', 7)[6]
        params = {'encrpripid': encrptpripid}
        r = self.post_request(url=url, data=params)
        if r.text == '[]':
            return None
        soup = BeautifulSoup(r.text, 'lxml')
        xingzhengcf_text = json.loads(soup.text.strip())
        for j in xingzhengcf_text:
            self.json_result[family].append({})
            for k in j:
                if k in xing_zheng_chu_fa_dict:
                    col = family + ':' + xing_zheng_chu_fa_dict[k]
                    val = j[k]
                    if k == 'penam' and val:
                        val = str(val) + u'万元'
                    self.json_result[family][-1][col] = val
            time_sec = j["pendecissdate"]["time"]/1000
            self.json_result[family][-1][family + ':' + 'penalty_decisiondate'] = time.strftime('%Y-%m-%d', time.localtime(time_sec))
        for i in range(len(self.json_result[family])):
            self.json_result[family][i]['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.cur_zch, self.today, i+1)
            self.json_result[family][i][family + ':registrationno'] = self.cur_zch
            self.json_result[family][i][family + ':enterprisename'] = self.cur_mc
            self.json_result[family][i][family + ':id'] = self.today + str(i + 1)
            # self.json_result[family][i][family + ':penalty_no'] = self.today + str(i + 1)
        # print json.dumps(self.json_result[family], ensure_ascii=False)

    def get_jing_ying_yi_chang(self, tag_a):
        """
        查询经营异常信息
        :param param_pripid:
        :param param_invid:
        :return:
        """
        self.info(u'解析经营异常信息...')
        family = 'Business_Abnormal'
        table_id = '14'
        self.json_result[family] = []
        self.headers['X-CSRF-TOKEN'] = self.token
        jingyingyc_url = 'http://218.57.139.24/pub/jyyc/'
        enttype = tag_a.split('/', 7)[5]
        url = jingyingyc_url + enttype
        encrptpripid = tag_a.split('/', 7)[6]
        params = {'encrpripid': encrptpripid}
        r = self.post_request(url=url, data=params)
        soup = BeautifulSoup(r.text, 'lxml')
        jingyingyc_text = json.loads(soup.text.strip())
        # print u'经营异常网站', jingyingyc_text
        for j in jingyingyc_text:
            self.json_result[family].append({})
            # print "jingyingyc_text[0]['abntime']",jingyingyc_text[0]['abntime']
            if 'abntime' in j and j['abntime']:
                year1 = j["abntime"]["year"]
                year2 = '%d' % year1
                mon1 = j["abntime"]["month"]+1
                mon2 = '%d' % mon1
                day1 = j["abntime"]["date"]
                day2 = '%d' % day1
                if len(year2) == 2:          # 如果是2位数，则是‘19’年，如果是3位数，则是‘20’年
                    year2 = '19'+year2
                elif len(year2) == 3:
                    year2 = '20'+year2[1:]
                date1 = year2 + u'年'+mon2+u'月'+day2 + u'日'
                j['abntime'] = date1
            if 'remdate' in j and j['remdate']:
                year3 = j["remdate"]["year"]
                year4 = '%d' % year3
                mon3 = j["remdate"]["month"]+1
                mon4 = '%d' % mon3
                day3  = j["remdate"]["date"]
                day4 = '%d' % day3
                if len(year4) == 2:          # 如果是2位数，则是‘19’年，如果是3位数，则是‘20’年
                    year4 = '19'+year4
                elif len(year4) ==3:
                    year4 = '20'+year2[1:]
                date2 = year4 + u'年'+mon4+u'月'+day4 + u'日'
                j['remdate'] = date2
            for k in j:
                if k in jing_ying_yi_chang_dict:
                    col = family + ':' + jing_ying_yi_chang_dict[k]
                    val = j[k]
                    self.json_result[family][-1][col] = val
        for i in range(len(self.json_result[family])):
            self.json_result[family][i]['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.cur_zch, self.today, i+1)
            self.json_result[family][i][family + ':registrationno'] = self.cur_zch
            self.json_result[family][i][family + ':enterprisename'] = self.cur_mc
            self.json_result[family][i][family + ':id'] = self.today + str(i + 1)
            self.json_result[family][i][family + ':abnormal_no'] = str(i + 1)
            # print json.dumps(self.json_result[family][i], ensure_ascii=False)
        # print json.dumps(self.json_result[family], ensure_ascii=False)

    def get_yan_zhong_wei_fa(self, tag_a):
        """
        查询严重违法信息
        :param tag_a:
        :return:
        """
        self.info(u'解析严重违法信息...')
        family = 'Serious_Violations'
        table_id = '15'
        self.json_result[family] = []
        self.headers['X-CSRF-TOKEN'] = self.token
        url = 'http://218.57.139.24/pub/yzwfqy'
        encrptpripid = tag_a.split('/', 7)[6]
        params = {'encrpripid': encrptpripid}
        r = self.post_request(url=url, data=params)
        soup = BeautifulSoup(r.text, 'lxml')
        yanzhongwf_text = json.loads(soup.text.strip())
        # print u'严重违法网站', yanzhongwf_text
        for j in yanzhongwf_text:
            self.json_result[family].append({})
            for k in j:
                if k in yan_zhong_wei_fa_dict:
                    col = family + ':' + yan_zhong_wei_fa_dict[k]
                    val = j[k]
                    self.json_result[family][-1][col] = val
                    # print col, val
        for i in range(len(self.json_result[family])):
            self.json_result[family][i]['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.cur_zch, self.today, i+1)
            self.json_result[family][i][family + ':registrationno'] = self.cur_zch
            self.json_result[family][i][family + ':enterprisename'] = self.cur_mc
            self.json_result[family][i][family + ':id'] = self.today + str(i + 1)
            self.json_result[family][i][family + ':serious_no'] = str(i + 1)
            #  print json.dumps(self.json_result[family][i], ensure_ascii=False)
        #  print json.dumps(self.json_result[family], ensure_ascii=False)

    def get_chou_cha_jian_cha(self, tag_a):
        """
        查询抽查检查信息
        :param tag_a:
        :return:
        """
        self.info(u'解析抽查检查信息...')
        family = 'Spot_Check'
        table_id = '16'
        self.json_result[family] = []
        self.headers['X-CSRF-TOKEN'] = self.token
        url = 'http://218.57.139.24/pub/ccjcxx'
        encrptpripid = tag_a.split('/', 7)[6]
        params = {'encrpripid': encrptpripid}
        r = self.post_request(url=url, data=params)
        soup = BeautifulSoup(r.text, 'lxml')
        chouchajc_text = json.loads(soup.text.strip())
        #  print u'抽查检查', chouchajc_text
        for j in chouchajc_text:
            self.json_result[family].append({})
            year1 = j["insdate"]["year"]
            year2 = '%d' % year1
            mon1 = j["insdate"]["month"]+1
            mon = '%d' % mon1
            day1 = j["insdate"]["date"]
            day = '%d' % day1
            if len(year2) == 2:          # 如果是2位数，则是‘19’年，如果是3位数，则是‘20’年
                year = '19'+year2
            elif len(year2) == 3:
                year = '20'+year2[1:]
            date = year + u'年'+mon+u'月'+day + u'日'
            j['insdate'] = date
            for k in j:
                if k in chou_cha_jian_cha_dict:
                    col = family + ':' + chou_cha_jian_cha_dict[k]
                    val = j[k]
                    self.json_result[family][-1][col] = val
        for i in range(len(self.json_result[family])):
            self.json_result[family][i]['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.cur_zch, self.today, i+1)
            self.json_result[family][i][family + ':registrationno'] = self.cur_zch
            self.json_result[family][i][family + ':enterprisename'] = self.cur_mc
            self.json_result[family][i][family + ':id'] = self.today + str(i + 1)
            self.json_result[family][i][family + ':check_no'] = str(i + 1)
            #  print json.dumps(self.json_result[family][i], ensure_ascii=False)
        # print json.dumps(self.json_result[family], ensure_ascii=False)

if __name__ == '__main__':
    args_dict = get_args()
    searcher = ShanDongSearcher()
    # searcher.delete_tag_a_from_db(u'博山鲁正灯具厂')
    # searcher.submit_search_request(u'安丘市宏丰建筑工程有限公司')
    searcher.submit_search_request(u'山东远大板业科技有限公司')
    searcher.info(json.dumps(searcher.json_result, ensure_ascii=False))
    # print json.dumps(searcher.json_result, ensure_ascii=False)
