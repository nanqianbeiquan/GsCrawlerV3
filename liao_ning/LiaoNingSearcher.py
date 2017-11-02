# coding=utf-8

import PackageTool
from gs.Searcher import Searcher
from gs.CompareStatus import *
from bs4 import BeautifulSoup
import json
from geetest_broker.GeetestBroker import GeetestBrokerRealTime
from LiaoNingConfig import *
import re
from gs.Searcher import get_args
from gs.TimeUtils import get_cur_time


class LiaoNingSearcher(Searcher, GeetestBrokerRealTime):
    json_result = {}
    pattern = re.compile("\s")
    cur_zch = ''
    kafka = None
    save_tag_a = True
    pripid = None
    enttype = None

    def __init__(self, dst_topic=None):
        super(LiaoNingSearcher, self).__init__(use_proxy=False, dst_topic=dst_topic)
        self.headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:47.0) Gecko/20100101 Firefox/47.0",
                        "Host": "gsxt.lngs.gov.cn",
                        "Accept": "*/*",
                        "Accept-Encoding": "gzip, deflate",
                        "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
                        "Connection": "keep-alive",
                        "Content-type": "application/json"}
        self.set_config()

    def set_config(self):
        self.province = u'辽宁省'

    def get_tag_a_from_page(self, keyword, flags=True):
        best_djzt = None
        self.status = ''
        for t in range(10):
            url_2 = 'http://ln.gsxt.gov.cn/saicpub/entPublicitySC/entPublicityDC/lngsSearchFpc!searchSolr.action'
            url = 'http://ln.gsxt.gov.cn/entPublicitySC/entPublicityDC/lngsSearchFpc!searchSolr.action'
            params = {'authCode': 'finish', 'currentPage': '1', 'pageSize': '10', 'solrCondition': keyword, }
            r = self.post_request(url=url, params=params)
            if u'登录超时' not in r.text and r.status_code == 200:
                self.status = 1
                pass
            else:
                r = self.post_request(url=url_2, params=params)
                self.status = 2
            # print '*'*100, r.text,
            # soup = BeautifulSoup(r.text, 'lxml')
            # search_result_text = soup.select('html head script')[-1].text.strip()
            # print 'self.status',self.status
            search_result_text = json.loads(r.text)['jsonArray']
            # print 'search_result_text',search_result_text, type(search_result_text)
            if search_result_text != u'':
                if search_result_text == []:
                    return None
                else:
                    break
        if search_result_text == u'':
            raise Exception(u"验证码输入错误！")
        for search_result in search_result_text:
            search_result_json = search_result
            entname = search_result_json['realEntName']
            pripid = search_result_json['pripid']
            status = search_result_json['optstateName']
            enttype = search_result_json['enttype']
            cur_zch = search_result_json['regno']
            tag_a = pripid + '&' + enttype + '&' + cur_zch
            entname = entname.replace('(', u'（').replace(')', u'）')  # 公司名称括号统一转成全角
            # print 'entname', entname, keyword, status
            if entname == keyword:
                if compare_status(status, best_djzt) >= 0:
                    best_djzt = status
                    best_tag_a = tag_a
        try:
            if best_tag_a:
                return best_tag_a
        except:
            return None

    def get_search_args(self, tag_a, keyword):
        self.pripid = None
        self.enttype = None
        search_result_json = tag_a
        # print type(search_result_json)
        # print search_result_json
        self.pripid = search_result_json.split('&', 1)[0]
        self.enttype = search_result_json.split('&', 1)[1].split('&', 1)[0]
        self.cur_zch = search_result_json.split('&', 2)[-1]
        # print 'self.pripid', self.pripid, self.enttype
        return 1

    # def download_yzm(self):
    #     image_url = 'http://gsxt.lngs.gov.cn/saicpub/commonsSC/loginDC/securityCode.action'
    #     r = self.get_request(image_url)
    #     yzm_path = self.get_yzm_path()
    #     with open(yzm_path, 'wb') as f:
    #         for chunk in r.iter_content(chunk_size=1024):
    #             if chunk:  # filter out keep-alive new chunks
    #                 f.write(chunk)
    #                 f.flush()
    #         f.close()
    #     return yzm_path

    def parse_detail(self):
        self.info(u'解析基本信息...')
        self.get_ji_ben()
        self.info(u'解析股东信息...')
        self.get_gu_dong()
        self.info(u'解析变更信息...')
        self.get_bian_geng()
        self.info(u'解析主要人员信息...')
        self.get_zhu_yao_ren_yuan()

    def get_ji_ben(self):
        """
        查询基本信息
        :return: 基本信息结果
        """
        family = 'Registered_Info'
        table_id = '01'
        self.json_result[family] = []
        url_2 = 'http://ln.gsxt.gov.cn/saicpub/entPublicitySC/entPublicityDC/getJbxxAction.action'
        url = 'http://ln.gsxt.gov.cn/entPublicitySC/entPublicityDC/getJbxxAction.action'
        params = {'pripid': self.pripid, 'type': self.enttype}
        if self.status == 1:
            r = self.get_request(url=url, params=params)
        # if u'登录超时' not in r.text and r.status_code==200: #and u'企业名称' in r.text
        #     pass
        # else:
        elif self.status == 2:
            r = self.get_request(url=url_2, params=params)
        # print r.text
        soup = BeautifulSoup(r.text, 'lxml')
        td_list = soup.select('body dl > dd')
        th_list = soup.select('body dl > dt')
        result_json = [{}]
        for i in range(len(td_list)):
            th = th_list[i].text.split('\n')[0]
            td = td_list[i].text.split('\n')[0]
            # print '##', type(th), th
            desc = th.replace(u'·', '').replace(u'：', '').strip().replace('', '')
            val = self.pattern.sub('', td)
            if len(desc) > 0:
                if desc == u'统一社会信用代码/注册号':
                    if len(val) == 18:
                        result_json[0][u'统一社会信用代码'] = val
                    else:
                        result_json[0][u'注册号'] = val
                result_json[0][desc] = val
                if desc == u'注册资本':
                    cap1 = td_list[i].contents[0].string.strip()
                    cap2 = td_list[i].contents[1].string.strip()
                    cap = cap1 + cap2
                    # print 'cap', type(cap1), cap
                    result_json[0][u'注册资本'] = cap
        for j in result_json:
            self.json_result[family].append({})
            for k in j:
                col = family + ':' + ji_ben_dict[k]
                val = j[k]
                self.json_result[family][-1][col] = val
                # print col,val
        # print 'aaa',self.json_result[family][-1]['Registered_Info:enterprisename']
        cur_mc = self.json_result[family][-1]['Registered_Info:enterprisename']
        self.cur_mc = self.process_mc(cur_mc)
        # print 'aaa', self.cur_mc
        if self.cur_mc != self.input_company_name:
            raise Exception(u'获取详情失败')
        self.json_result[family][-1]['rowkey'] = '%s_%s_%s_' % (self.cur_mc, table_id, self.cur_zch)
        # self.json_result[family][-1][family + ':registrationno'] = self.cur_zch
        self.json_result[family][-1][family + ':enterprisename'] = self.cur_mc
        self.json_result[family][-1][family + ':province'] = self.province
        self.json_result[family][-1][family + ':lastupdatetime'] = get_cur_time()

    def get_gu_dong(self):
        """
        查询股东信息
        :return:
        """
        family = 'Shareholder_Info'
        table_id = '04'
        self.json_result[family] = []
        url_2 = 'http://ln.gsxt.gov.cn/saicpub/entPublicitySC/entPublicityDC/getTzrxxAction.action'
        url = 'http://ln.gsxt.gov.cn/entPublicitySC/entPublicityDC/getTzrxxAction.action'
        params = {'pripid': self.pripid, 'type': self.enttype}
        # params = {'pripid': '210000000012012061413892', 'type': '1190'}
        if self.status == 1:
            r = self.get_request(url=url, params=params)
        # print 'gu_dong.text',r.text
        # if u'登录超时' not in r.text and r.status_code==200: #and u'投资人信息' in r.text
        #     pass
        # else:
        elif self.status == 2:
            r = self.get_request(url=url_2, params=params)
        content = r.text
        # result_json = self.get_result_json(url, params)
        result_json = self.get_result_json(content)
        # print 'result_json', result_json
        for j in result_json:
            self.json_result[family].append({})
            for k in j:
                if k in gu_dong_dict:
                    col = family + ':' + gu_dong_dict[k]
                    val = j[k]
                    self.json_result[family][-1][col] = val
            if j['invid']:
                link = j['invid']
                detail_list = self.get_gu_dong_detail(link)
                # print 'detail_list', detail_list
                self.json_result[family][-1].update(detail_list)
        for i in range(len(self.json_result[family])):
            self.json_result[family][i]['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.cur_zch, self.today, i+1)
            self.json_result[family][i][family + ':registrationno'] = self.cur_zch
            self.json_result[family][i][family + ':enterprisename'] = self.cur_mc
            self.json_result[family][i][family + ':id'] = self.today+str(i+1)

    def get_gu_dong_detail(self, param_invid):
        """
        查询股东详情
        :param param_pripid:
        :param param_invid:
        :return:
        """
        value = {}
        rjmx_list = []
        sjmx_list = []
        rjmx_dict = dict()
        sjmx_dict = dict()
        params = {'invid': param_invid, 'pripid': self.pripid}
        url_2 = 'http://ln.gsxt.gov.cn/saicpub/entPublicitySC/entPublicityDC/getGsgsTzrxxPojoList.action'
        url = 'http://ln.gsxt.gov.cn/entPublicitySC/entPublicityDC/getGsgsTzrxxPojoList.action'
        if self.status == 1:
            r = self.session.post(url=url, headers=self.headers, params=params)
        # print 'gu_dong_detail_text',r.text
        # if u'登录超时' not in r.text and r.status_code== 200:
        #     pass
        # else:
        elif self.status == 2:
            r = self.session.post(url=url_2, headers=self.headers, params=params)
            # print 'gu_dong_detail_2',r.text
        result_text = json.loads(r.text)
        # print 'result_text', result_text
        gudong_json = result_text[0]['tRegTzrxx']
        value['Shareholder_Info:subscripted_capital'] = gudong_json['lisubconam']
        value['Shareholder_Info:actualpaid_capital'] = gudong_json['liacconam']
        renjiao_json = result_text[0]['tRegTzrrjxxList']
        # print type(renjiao_json), renjiao_json
        for j in renjiao_json:
            # self.json_result[family].append({})
            rjmx_dict[u'认缴出资方式']= j['conformName']
            rjmx_dict[u'认缴出资额（万元）']= j['subconam']
            rjmx_dict[u'认缴出资日期']= j['condate']
            rjmx_list.append(rjmx_dict)
            value['Shareholder_Info:subscripted_method'] = j['conformName']
            # print "j['conform']",type(j['conform']),  j['conform']
            # value['Shareholder_Info:subscripted_amount'] = str(j['subconam'])+ u'万元'
            value['Shareholder_Info:subscripted_amount'] = j['subconam']
            value['Shareholder_Info:subscripted_time'] = j['condate']
            rjmx_dict = {}
        value['Shareholder_Info:rjmx'] = rjmx_list
        shijiao_json = result_text[0]['tRegTzrsjxxList']
        for j in shijiao_json:
            # self.json_result[family].append({})
            sjmx_dict[u'认缴出资方式']= j['conformName']
            sjmx_dict[u'认缴出资额（万元）']= j['acconam']
            sjmx_dict[u'认缴出资日期']= j['condate']
            sjmx_list.append(sjmx_dict)
            value['Shareholder_Info:actualpaid_method'] = j['conformName']
            value['Shareholder_Info:actualpaid_amount'] = j['acconam']
            value['Shareholder_Info:actualpaid_time'] = j['condate']
            sjmx_dict = {}
        value['Shareholder_Info:sjmx'] = sjmx_list
        # print 'value', value
        return value

    def get_bian_geng(self):
        """
        查询变更信息
        :return:
        """
        family = 'Changed_Announcement'
        table_id = '05'
        self.json_result[family] = []
        url_2 = 'http://ln.gsxt.gov.cn/saicpub/entPublicitySC/entPublicityDC/getBgxxAction.action'
        url = 'http://ln.gsxt.gov.cn/entPublicitySC/entPublicityDC/getBgxxAction.action'
        params = {'pripid': self.pripid, 'type': self.enttype}
        # params = {'pripid': '210000000012012061413892', 'type': '1190'}
        if self.status == 1:
            r = self.get_request(url=url, params=params)
        # if u'登录超时' not in r.text and r.status_code== 200:  # and u'变更信息' in r.text
        #     pass
        # else:
        elif self.status == 2:
            r = self.get_request(url=url_2, params=params)
        content = r.text
        # result_json = self.get_result_json(url, params)
        result_json = self.get_result_json(content)
        for j in result_json:
            self.json_result[family].append({})
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

    def get_zhu_yao_ren_yuan(self):
        """
        查询主要人员信息
        :return:
        """
        family = 'KeyPerson_Info'
        table_id = '06'
        self.json_result[family] = []
        url_2 = 'http://ln.gsxt.gov.cn/saicpub/entPublicitySC/entPublicityDC/getZyryxxAction.action'
        url = 'http://ln.gsxt.gov.cn/entPublicitySC/entPublicityDC/getZyryxxAction.action'
        params = {'pripid': self.pripid, 'type': self.enttype}
        # params = {'pripid': '210000000012012061413892', 'type': '1190'}
        if self.status == 1:
            r = self.get_request(url=url, params=params)
        # if u'登录超时' not in r.text and r.status_code==200: # and u'主要人员' in r.text
        #     pass
        # else:
        elif self.status == 2:
            r = self.get_request(url=url_2, params=params)
        content = r.text
        result_json = self.get_result_json(content)
        for j in result_json:
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
        # print json.dumps(result_json_2, ensure_ascii=False)

    def get_fen_zhi_ji_gou(self):
        """
        查询分支机构信息
        :return:
        """
        family = 'Branches'
        table_id = '08'
        self.json_result[family] = []
        url = 'http://gsxt.lngs.gov.cn/saicpub/entPublicitySC/entPublicityDC/getFgsxxAction.action'
        params = {'pripid': self.pripid, 'type': self.enttype}
        result_json = self.get_result_json(url, params)
        for j in result_json:
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
        # print json.dumps(result_json_2, ensure_ascii=False)

    def get_qing_suan(self):
        """
        查询清算信息
        :return:
        """
        family = 'liquidation_Information'
        table_id = '09'
        self.json_result[family] = []
        url = 'http://gsxt.lngs.gov.cn/saicpub/entPublicitySC/entPublicityDC/getQsxxAction.action?'
        params = {'pripid': self.pripid, 'type': self.enttype}
        r = self.session.get(url=url, headers=self.headers, params=params)
        soup = BeautifulSoup(r.text, 'lxml')
        script_list = soup.select('html > head > script')
        if len(script_list) > 0:
            result_text = script_list[-1].text.strip()
            # print result_text
            result_text = result_text[len('$(document).ready(function()'):-2]
            start_idx = result_text.index('[')
            # stop_idx = result_text.index(']') + len(']')
            stop_idx = len(result_text) - result_text[::-1].index(']')
            result_text = result_text[start_idx:stop_idx]
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
        :return:
        """
        family = 'Chattel_Mortgage'
        table_id = '11'
        self.json_result[family] = []
        url = 'http://gsxt.lngs.gov.cn/saicpub/entPublicitySC/entPublicityDC/getDcdydjAction.action'
        params = {'pripid': self.pripid, 'type': self.enttype}
        result_json = self.get_result_json(url, params)
        for j in result_json:
            self.json_result[family].append({})
            for k in j:
                if k in dong_chan_di_ya_dict:
                    col = family + ':' + dong_chan_di_ya_dict[k]
                    val = j[k]
                    self.json_result[family][-1][col] = val
        for i in range(len(self.json_result[family])):
            self.json_result[family][i]['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.cur_zch, self.today, i+1)
            self.json_result[family][i][family + ':registrationno'] = self.cur_zch
            self.json_result[family][i][family + ':enterprisename'] = self.cur_mc
            self.json_result[family][i][family + ':id'] = self.today + str(i + 1)
        # print json.dumps(result_json_2, ensure_ascii=False)

    def get_gu_quan_chu_zhi(self):
        """
        查询股权出置信息
        :return:
        """
        family = 'Equity_Pledge'
        table_id = '12'
        self.json_result[family] = []
        url = 'http://gsxt.lngs.gov.cn/saicpub/entPublicitySC/entPublicityDC/getGsgsGqczxxAction.action'
        params = {'pripid': self.pripid, 'type': self.enttype}
        result_json = self.get_result_json(url, params)
        for j in result_json:
            self.json_result[family].append({})
            for k in j:
                if k in gu_quan_chu_zhi_dict:
                    col = family + ':' + gu_quan_chu_zhi_dict[k]
                    val = j[k]
                    self.json_result[family][-1][col] = val
            self.json_result[family][-1][family + ':equitypledge_amount'] = j['impam'] + j['pledamunitName']
        for i in range(len(self.json_result[family])):
            self.json_result[family][i]['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.cur_zch, self.today, i+1)
            self.json_result[family][i][family + ':registrationno'] = self.cur_zch
            self.json_result[family][i][family + ':enterprisename'] = self.cur_mc
            self.json_result[family][i][family + ':id'] = self.today + str(i + 1)
        # print json.dumps(result_json_2, ensure_ascii=False)

    def get_xing_zheng_chu_fa(self):
        """
        查询行政处罚信息
        :return:
        """
        family = 'Administrative_Penalty'
        table_id = '13'
        self.json_result[family] = []
        url = 'http://gsxt.lngs.gov.cn/saicpub/entPublicitySC/entPublicityDC/getXzcfxxAction.action'
        params = {'pripid': self.pripid, 'type': self.enttype}
        result_json = self.get_result_json(url, params)
        for j in result_json:
            self.json_result[family].append({})
            for k in j:
                if k in xing_zheng_chu_fa_dict:
                    col = family + ':' + xing_zheng_chu_fa_dict[k]
                    val = j[k]
                    self.json_result[family][-1][col] = val
        for i in range(len(self.json_result[family])):
            self.json_result[family][i]['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.cur_zch, self.today, i+1)
            self.json_result[family][i][family + ':registrationno'] = self.cur_zch
            self.json_result[family][i][family + ':enterprisename'] = self.cur_mc
            self.json_result[family][i][family + ':id'] = self.today + str(i + 1)
        # print json.dumps(result_json_2, ensure_ascii=False)

    def get_jing_ying_yi_chang(self):
        """
        查询经营异常信息
        :return:
        """
        family = 'Business_Abnormal'
        table_id = '14'
        self.json_result[family] = []
        url = 'http://gsxt.lngs.gov.cn/saicpub/entPublicitySC/entPublicityDC/getJyycxxAction.action'
        params = {'pripid': self.pripid, 'type': self.enttype}
        result_json = self.get_result_json(url, params)
        for j in result_json:
            self.json_result[family].append({})
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
        self.json_result[family] = []
        url = 'http://gsxt.lngs.gov.cn/saicpub/entPublicitySC/entPublicityDC/getYzwfxxAction.action'
        params = {'pripid': self.pripid, 'type': self.enttype}
        result_json = self.get_result_json(url, params)
        for j in result_json:
            self.json_result[family].append({})
            for k in j:
                if k in yan_zhong_wei_fa_dict:
                    col = family + ':' + yan_zhong_wei_fa_dict[k]
                    val = j[k]
                    self.json_result[family][-1][col] = val
        for i in range(len(self.json_result[family])):
            self.json_result[family][i]['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.cur_zch, self.today, i+1)
            self.json_result[family][i][family + ':registrationno'] = self.cur_zch
            self.json_result[family][i][family + ':enterprisename'] = self.cur_mc
            self.json_result[family][i][family + ':id'] = self.today + str(i + 1)
        # print json.dumps(result_json_2, ensure_ascii=False)

    def get_chou_cha_jian_cha(self):
        """
        查询抽查检查信息
        :return:
        """
        family = 'Spot_Check'
        table_id = '16'
        self.json_result[family] = []
        url = 'http://gsxt.lngs.gov.cn/saicpub/entPublicitySC/entPublicityDC/getCcjcxxAction.action'
        params = {'pripid': self.pripid, 'type': self.enttype}
        result_json = self.get_result_json(url, params)
        for j in result_json:
            self.json_result[family].append({})
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
        # print json.dumps(result_json_2, ensure_ascii=False)

    # def get_result_json(self, url, params):
    def get_result_json(self, content):
        """
        将get请求返回结果解析成json数组
        :param url:
        :param params:
        :return:
        """
        # r = self.get_request(url=url, params=params)
        soup = BeautifulSoup(content, 'lxml')
        script_list = soup.select('html > head > script')
        if len(script_list) > 0:
            result_text = script_list[-1].text.strip()
            # print '111', result_text
            # result_text = result_text[len('$(document).ready(function()'):-2]
            start_idx = result_text.index('[')
            # stop_idx = len(result_text) - result_text[::-1].index(']')
            stop_idx = result_text.rindex(']')
            result_text = result_text[start_idx:(stop_idx+1)]
            # print '222', result_text
            result_json = json.loads(result_text)
        else:
            result_json = []
        return result_json

        # print json.dumps(result_json, ensure_ascii=False)

    def get_nian_bao_link(self):
        """
        获取年报url
        :return:
        """
        url = 'http://gsxt.lngs.gov.cn/saicpub/entPublicitySC/entPublicityDC/getQygsQynbxxAction.action'
        params = {'pripid': self.pripid, 'type': self.enttype}
        return self.get_result_json(url, params)

    # def get_nian_bao(self, param_pripid, param_type):
    #     pass


if __name__ == '__main__':
    searcher = LiaoNingSearcher()
    # searcher = LiaoNingSearcher('GSCrawlerResultTest')
    args_dict = get_args()
    searcher.submit_search_request(u"大连鸿源伟运科技有限公司")
    # if args_dict:
    #     searcher.submit_search_request(keyword=args_dict['companyName'], account_id=args_dict['accountId'], task_id=args_dict['taskId'])
    # else:
    #     searcher.submit_search_request(u"京沈铁路客运专线辽宁有限责任公司")
        # searcher.info(json.dumps(searcher.json_result, ensure_ascii=False))
