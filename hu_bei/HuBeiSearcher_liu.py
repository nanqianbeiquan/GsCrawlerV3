# coding=utf-8

import PackageTool

from gs.Searcher import get_args
from gs.KafkaAPI import KafkaAPI
from gs.Searcher import Searcher
# from gs.Searcher import get_args
# from PIL import Image
# from bs4 import BeautifulSoup
# import urllib2
# import random
import json
# from json.decoder import JSONArray
# from gs.TimeUtils import get_cur_time_jiangsu
from gs.TimeUtils import get_cur_time,get_cur_ts_mil
from lxml import html
# from gs.ProxyConf import ProxyConf, key1 as app_key
from HuBeiConfig import *
import re
# import tesseract
from threading import Thread


class HuBeiSearcher(Searcher):

    def __init__(self):
        super(HuBeiSearcher, self).__init__(use_proxy=False)
        self.headers = {
            "Host": "xyjg.egs.gov.cn",
            # "Referer": "http://xyjg.egs.gov.cn/ECPS_HB/search.jspx",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.63 Safari/537.36"
        }
        # self.s = set()
        # self.get_word_set()
        self.set_config()
        self.ent_id = ''
        self.log_name = 'hu_bei'

    def set_config(self):
        self.province = u'湖北省'

    def get_tag_a_from_page(self, keyword, flags=True):
        self.ent_id = ''
        params = {"currentPageIndex": '1', "entName": keyword, "searchType": '1'}
        url = "http://xyjg.egs.gov.cn/ECPS_HB/queryListData.jspx"
        r = self.post_request(url, data=params)
        r.encoding = 'utf-8'
        tree = html.fromstring(r.text)
        result_list = tree.xpath(".//p[@class='gggscpnametitle']")
        for ent in result_list:
            ent_name = ent.text.replace('(', u'（').replace(')', u'）').strip().replace('\n\r', '')
            if ent_name != keyword:
                self.save_mc_to_db(ent_name)
        for ent in result_list:
            ent_name = ent.text.replace('(', u'（').replace(')', u'）').strip().replace('\n\r', '')
            # self.info( ent_name
            if flags:
                if ent_name == keyword:
                    self.info(u'查到指定公司')
                    # self.cur_mc = keyword
                    self.ent_id = ent.xpath("span[2]")[0].get("class")
                    return "http://xyjg.egs.gov.cn/ECPS_HB/company/detail.jspx?id=%s" % self.ent_id
            else:
                self.info(u'查到指定公司')
                self.ent_id = ent.xpath("span[2]")[0].get("class")
                return "http://xyjg.egs.gov.cn/ECPS_HB/company/detail.jspx?id=%s" % self.ent_id

    def get_search_args(self, tag_a, keyword):
        self.cur_mc = keyword
        self.ent_id = re.findall('.*?id=(.*)$', tag_a)[0]
        return 1

    def get_ji_ben(self):
        family = 'Registered_Info'
        table_id = '01'
        url = "http://xyjg.egs.gov.cn/ECPS_HB/business/JCXX.jspx?id=" + self.ent_id
        r = self.get_request(url)
        r.encoding = 'utf-8'
        dengji_tree = html.fromstring(r.text)
        th_list = dengji_tree.xpath(".//td")
        td_list = dengji_tree.xpath(".//td/span")
        result_values = {}
        for i in range(len(td_list)):
            th = th_list[i]
            td = td_list[i]
            desc = th.text.strip(u'·').replace(u'：', '').strip()
            val = td.text
            if val:
                val = val.strip().replace("\n", '')
            if desc:
                if desc == u'统一社会信用代码/注册号':
                    self.cur_zch = val
                    if len(self.cur_zch) == 18:
                        result_values[family + ':tyshxy_code'] = self.cur_zch
                    else:
                        result_values[family + ':zch'] = self.cur_zch
                if desc in ji_ben_dict:
                    result_values[family + ':' + ji_ben_dict[desc]] = val
        result_values['rowkey'] = '%s_%s_%s_' % (self.cur_mc, table_id, self.cur_zch)
        result_values[family + ':registrationno'] = self.cur_zch
        result_values[family + ':enterprisename'] = self.cur_mc
        result_values[family + ':province'] = u'湖北省'
        result_values[family + ':lastupdatetime'] = get_cur_time()
        self.json_result[family] = [result_values]

    def get_gu_dong(self):
        family = 'Shareholder_Info'
        table_id = '04'
        result_list = []
        result_values = dict()
        j = 1
        for num in range(1, 100):
            url = 'http://xyjg.egs.gov.cn/ECPS_HB/business/QueryInvList.jspx?pno=%s&order=0&mainId=%s' % (num, self.ent_id)
            r = self.get_request(url)
            r.encoding = 'utf-8'
            shareholder_table = html.fromstring(r.text)
            page_num = int(shareholder_table.xpath(".//ul/li[2]")[0].text[1:-1])
            if page_num == 0:
                break
            th_list = shareholder_table.xpath(".//table[1]//th")
            tr_list = shareholder_table.xpath(".//table[2]/tr")
            if len(tr_list) == 0:
                break
            if tr_list:
                for tr in tr_list:
                    td_list = tr.xpath("td")
                    for i in range(len(th_list)):
                        th = th_list[i]
                        td = td_list[i]
                        desc = th.text.strip()
                        if td.xpath("a"):
                            self.info(u'%s %s 发现股东详情' % (self.province, self.cur_mc))  # 湖北发现股东详情
                            val = td.xpath('a')[0].get('onclick')
                            val = "http://xyjg.egs.gov.cn/ECPS_HB/queryInvDetailAction.jspx?invId=" + re.findall("(\d+)", val)[0]
                            gu_dong_detail = self.get_gu_dong_detail(val)
                            for detail_key in gu_dong_detail:
                                if detail_key in gu_dong_dict:
                                    result_values[family + ":" + gu_dong_dict[detail_key]] = gu_dong_detail[detail_key]
                        else:
                            val = td.text
                        if desc in gu_dong_dict:
                            if val:
                                result_values[family + ":" + gu_dong_dict[desc]] = val
                    result_values['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.cur_zch, self.today, j)
                    result_values[family + ':registrationno'] = self.cur_zch
                    result_values[family + ':enterprisename'] = self.cur_mc
                    result_values[family + ':id'] = j
                    result_list.append(result_values)
                    result_values = {}
                    j += 1
            if page_num == num:
                break
        self.json_result[family] = result_list
        # self.info( json.dumps(self.json_result, ensure_ascii=False)

    def get_gu_dong_detail(self, url):
        r = self.get_request(url)
        r.encoding = 'utf-8'
        tree = html.fromstring(r.text)
        colum_name_list = tree.xpath(".//th")
        td_element_list = tree.xpath(".//td")
        # del colum_name_list[3:5]
        col_num = min(len(td_element_list), len(colum_name_list))
        values = {}
        for i in range(col_num):
            col = colum_name_list[i].text.strip().replace('\n', '')
            if td_element_list[i].xpath("span"):
                val = td_element_list[i].xpath("span")[0].text
            else:
                val = td_element_list[i].text
            if val:
                values[col] = val.strip().replace('\n', '')
        # self.info(json.dumps(values,ensure_ascii=False)
        return values

    def get_bian_geng(self):
        family = 'Changed_Announcement'
        table_id = '05'
        result_list = []
        result_values = dict()
        j = 1
        for num in range(1, 100):
            url = 'http://xyjg.egs.gov.cn/ECPS_HB/business/QueryAltList.jspx?pno=%s&order=0&mainId=%s' % (num, self.ent_id)
            r = self.get_request(url)
            r.encoding = 'utf-8'
            alt_table = html.fromstring(r.text)
            page_num = int(alt_table.xpath(".//ul/li[2]")[0].text[1:-1])
            if page_num == 0:
                break
            th_list = alt_table.xpath(".//table[1]//th")
            tr_list = alt_table.xpath(".//div[@id='altDiv']//tr")
            if len(tr_list) == 0:
                break
            if tr_list:
                for tr in tr_list:
                    td_list = tr.xpath("td")
                    for i in range(len(th_list)):
                        th = th_list[i]
                        td = td_list[i]
                        desc = th.text.strip()
                        val = td.text
                        if val:
                            val = val.strip()
                        if desc in bian_geng_dict:
                            result_values[family + ":" + bian_geng_dict[desc]] = val
                    result_values['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.cur_zch, self.today, j)
                    result_values[family + ':registrationno'] = self.cur_zch
                    result_values[family + ':enterprisename'] = self.cur_mc
                    result_values[family + ':id'] = j
                    result_list.append(result_values)
                    result_values = {}
                    j += 1
            if num == page_num:
                break
        self.json_result[family] = result_list
        # self.info( json.dumps(self.json_result, ensure_ascii=False)

    def get_zhu_yao_ren_yuan(self):
        family = 'KeyPerson_Info'
        table_id = '06'
        result_list = []
        result_values = dict()
        j = 1
        url = 'http://xyjg.egs.gov.cn/ECPS_HB/business/loadMoreMainStaff.jspx?uuid=%s&order=0' % self.ent_id
        r = self.get_request(url)
        r.encoding = 'utf-8'
        mem_table = html.fromstring(r.text)
        th_list = [u'姓名', u'职务']
        tr_list = mem_table.xpath(".//div[@class='keyPerInfo']")
        if tr_list:
            for tr in tr_list:
                td_list = tr.xpath(".//span")
                for i in range(len(td_list)):
                    th = th_list[i]
                    td = td_list[i]
                    desc = th
                    val = td.text
                    if desc in zhu_yao_ren_yuan_dict:
                        result_values[family + ":" + zhu_yao_ren_yuan_dict[desc]] = val
                result_values['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.cur_zch, self.today, j)
                result_values[family + ':registrationno'] = self.cur_zch
                result_values[family + ':enterprisename'] = self.cur_mc
                result_values[family + ':id'] = j
                result_list.append(result_values)
                result_values = {}
                j += 1
        self.json_result[family] = result_list
        # self.info( json.dumps(self.json_result, ensure_ascii=False)

    def get_fen_zhi_ji_gou(self):
        family = 'Branches'
        table_id = '08'
        result_list = []
        result_values = dict()
        j = 1
        url = 'http://xyjg.egs.gov.cn/ECPS_HB/business/loadMoreChildEnt.jspx?uuid=%s&order=0' % self.ent_id
        r = self.get_request(url)
        r.encoding = 'utf-8'
        mem_table = html.fromstring(r.text)
        th_list = [u'名称', u'注册号', u'登记机关']
        tr_list = mem_table.xpath(".//div[@class='fenzhixinxin']")
        if tr_list:
            for tr in tr_list:
                td_list = tr.xpath(".//p/span")
                for i in range(3):
                    th = th_list[i]
                    td = td_list[i]
                    desc = th
                    val = td.text
                    # self.info( desc, val
                    if val:
                        if u'：' in val:
                            val = td.text.split(u'：')[1]
                        val = val.strip()
                    if desc in fen_zhi_ji_gou_dict:
                        result_values[family + ":" + fen_zhi_ji_gou_dict[desc]] = val
                result_values['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.cur_zch, self.today, j)
                result_values[family + ':registrationno'] = self.cur_zch
                result_values[family + ':enterprisename'] = self.cur_mc
                result_values[family + ':id'] = j
                result_list.append(result_values)
                result_values = {}
                j += 1
        self.json_result[family] = result_list
        # self.info( json.dumps(self.json_result, ensure_ascii=False)

    def get_qing_suan(self):
        pass

    def get_dong_chan_di_ya(self):
        family = 'Chattel_Mortgage'
        table_id = '11'
        result_list = []
        result_values = dict()
        j = 1
        for num in range(1, 100):
            url = 'http://xyjg.egs.gov.cn/ECPS_HB/business/QueryMortList.jspx?pno=%d&mainId=%s' % (num, self.ent_id)
            r = self.get_request(url)
            r.encoding = 'utf-8'
            # self.info( r.text
            mortage_table = html.fromstring(r.text)
            page_num = int(mortage_table.xpath(".//ul/li[2]")[0].text[1:-1])
            if page_num == 0:
                break
            th_list = mortage_table.xpath(".//th")
            tr_list = mortage_table.xpath("div/table[2]//tr")
            if tr_list:
                for tr in tr_list:
                    td_list = tr.xpath("td")
                    for i in range(len(th_list)):
                        th = th_list[i]
                        td = td_list[i]
                        desc = th.text.strip()
                        val = td.text
                        if td.xpath("a"):
                            val = "http://xyjg.egs.gov.cn" + td.xpath("a")[0].get("onclick")[13:-2]
                        if val:
                            val = val.strip()
                        if desc in dong_chan_di_ya_dict and val:
                            result_values[family + ":" + dong_chan_di_ya_dict[desc]] = val
                    result_values['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.cur_zch, self.today, j)
                    result_values[family + ':registrationno'] = self.cur_zch
                    result_values[family + ':enterprisename'] = self.cur_mc
                    result_values[family + ':id'] = j
                    result_list.append(result_values)
                    result_values = {}
                    j += 1
            if num == page_num:
                break
        self.json_result[family] = result_list
        # self.info( json.dumps(self.json_result, ensure_ascii=False)

    def get_gu_quan_chu_zhi(self):
        family = 'Equity_Pledge'
        table_id = '12'
        result_list = []
        result_values = dict()
        j = 1
        for num in range(1, 100):
            url = 'http://xyjg.egs.gov.cn/ECPS_HB/business/QueryPledgeList.jspx?pno=%s&order=0&mainId=%s' % (num, self.ent_id)
            r = self.get_request(url)
            r.encoding = 'utf-8'
            pledge_table = html.fromstring(r.text)
            page_num = int(pledge_table.xpath(".//ul/li[2]")[0].text[1:-1])
            if page_num == 0:
                break
            th_list = pledge_table.xpath(".//th")
            tr_list = pledge_table.xpath("div/table[2]//tr")
            if tr_list:
                for tr in tr_list:
                    td_list = tr.xpath("td")
                    for i in range(len(th_list)):
                        th = th_list[i]
                        td = td_list[i]
                        desc = th.text.strip()
                        val = td.text
                        if desc == u'证照/证件号码':
                            if i == 3:
                                desc = u'证照/证件号码(出质人)'
                            elif i == 6:
                                desc = u'证照/证件号码(质权人)'
                        if td.xpath("a"):
                            self.info(u'发现%s%s%s详情' % (self.province, self.cur_mc, family))
                            # val = "http://xyjg.egs.gov.cn" + td.xpath("a")[0].get("onclick")[13:-2]
                        if val:
                            val = val.strip()
                        if desc in gu_quan_chu_zhi_dict:
                            result_values[family + ":" + gu_quan_chu_zhi_dict[desc]] = val
                    result_values['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.cur_zch, self.today, j)
                    result_values[family + ':registrationno'] = self.cur_zch
                    result_values[family + ':enterprisename'] = self.cur_mc
                    result_values[family + ':id'] = j
                    result_list.append(result_values)
                    result_values = {}
                    j += 1
            if num == page_num:
                break
        self.json_result[family] = result_list
        # self.info( json.dumps(self.json_result, ensure_ascii=False)

    def get_xing_zheng_chu_fa(self):
        family = 'Administrative_Penalty'
        table_id = '13'
        result_list = []
        result_values = dict()
        j = 1
        for num in range(1, 100):
            url = 'http://xyjg.egs.gov.cn/ECPS_HB/business/QueryPunList.jspx?pno=%d&mainId=%s' % (num, self.ent_id)
            r = self.get_request(url)
            r.encoding = 'utf-8'
            penalty_table = html.fromstring(r.text)
            page_num = int(penalty_table.xpath(".//ul/li[2]")[0].text[1:-1])
            if page_num == 0:
                break
            th_list = penalty_table.xpath(".//th")
            tr_list = penalty_table.xpath(".//tr")[1:]
            if tr_list:
                for tr in tr_list:
                    td_list = tr.xpath("td")
                    if len(td_list) == 1:
                        break
                    for i in range(len(td_list)):
                        th = th_list[i]
                        td = td_list[i]
                        desc = th.text.strip()
                        val = td.text
                        if td.xpath("a"):
                            val = "http://xyjg.egs.gov.cn" + td.xpath("a")[0].get("onclick")[13:-2]
                        if val:
                            val = val.strip()
                        if desc in xing_zheng_chu_fa_dict:
                            result_values[family + ":" + xing_zheng_chu_fa_dict[desc]] = val
                    result_values['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.cur_zch, self.today, j)
                    result_values[family + ':registrationno'] = self.cur_zch
                    result_values[family + ':enterprisename'] = self.cur_mc
                    result_values[family + ':id'] = j
                    result_list.append(result_values)
                    result_values = {}
                    j += 1
            if num == page_num:
                break
        self.json_result[family] = result_list
        # self.info( json.dumps(self.json_result, ensure_ascii=False)

    def get_jing_ying_yi_chang(self):
        family = 'Business_Abnormal'
        table_id = '14'
        result_list = []
        result_values = dict()
        j = 1
        for num in range(1, 100):
            url = 'http://xyjg.egs.gov.cn/ECPS_HB/business/QueryExcList.jspx?pno=%d&mainId=%s' % (num, self.ent_id)
            r = self.get_request(url)
            r.encoding = 'utf-8'
            abnormal_table = html.fromstring(r.text)
            page_num = int(abnormal_table.xpath(".//ul/li[2]")[0].text[1:-1])
            if page_num == 0:
                break
            th_list = abnormal_table.xpath(".//th")
            tr_list = abnormal_table.xpath(".//div[@id='excDiv']//tr")
            # print tr_list
            if tr_list:
                for tr in tr_list:
                    td_list = tr.xpath("td")
                    for i in range(len(th_list)):
                        th = th_list[i]
                        td = td_list[i]
                        desc = th.text
                        val = td.text
                        if td.xpath("a"):
                            val = "http://xyjg.egs.gov.cn" + td.xpath("a")[0].get("onclick")[13:-2]
                        if val:
                            val = val.strip()
                        if desc in jing_ying_yi_chang_dict:
                            result_values[family + ":" + jing_ying_yi_chang_dict[desc]] = val
                    result_values['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.cur_zch, self.today, j)
                    result_values[family + ':registrationno'] = self.cur_zch
                    result_values[family + ':enterprisename'] = self.cur_mc
                    result_values[family + ':id'] = j
                    result_list.append(result_values)
                    result_values = {}
                    j += 1
            if num == page_num:
                break
        self.json_result[family] = result_list
        # self.info( json.dumps(self.json_result, ensure_ascii=False)

    def get_yan_zhong_wei_fa(self):
        pass

    def get_chou_cha_jian_cha(self):
        # return
        family = 'Spot_Check'
        table_id = '16'
        result_list = []
        result_values = dict()
        j = 1
        for num in range(1, 100):
            url = 'http://xyjg.egs.gov.cn/ECPS_HB/business/QuerySpotCheckList.jspx?pno=%d&mainid=%s&order=0' % (num, self.ent_id)
            r = self.get_request(url)
            r.encoding = 'utf-8'
            spotcheck_table = html.fromstring(r.text)
            page_num = int(spotcheck_table.xpath(".//ul/li[2]")[0].text[1:-1])
            if page_num == 0:
                break
            th_list = spotcheck_table.xpath(".//th")
            tr_list = spotcheck_table.xpath(".//tr")[1:]
            if tr_list:
                for tr in tr_list:
                    td_list = tr.xpath("td")
                    for i in range(len(th_list)):
                        th = th_list[i]
                        td = td_list[i]
                        desc = th.text
                        val = td.text
                        if td.xpath("a"):
                            val = "http://xyjg.egs.gov.cn" + td.xpath("a")[0].get("onclick")[13:-2]
                        if desc in chou_cha_jian_cha_dict and val:
                            val = val.strip()
                            result_values[family + ":" + chou_cha_jian_cha_dict[desc]] = val
                    result_values['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.cur_zch, self.today, j)
                    result_values[family + ':registrationno'] = self.cur_zch
                    result_values[family + ':enterprisename'] = self.cur_mc
                    result_values[family + ':id'] = j
                    result_list.append(result_values)
                    result_values = {}
                    j += 1
            if num == page_num:
                break
        self.json_result[family] = result_list

if __name__ == "__main__":
    searcher = HuBeiSearcher()
    args_dict = get_args()
    if args_dict:
        searcher.submit_search_request(keyword=args_dict['companyName'], account_id=args_dict['accountId'], task_id=args_dict['taskId'])
    else:
        # searcher.delete_tag_a_from_db(u"东风汽车有限公司")
        searcher.submit_search_request(u"湖北东方航空传媒有限公司")
        searcher.info(json.dumps(searcher.json_result, ensure_ascii=False))
