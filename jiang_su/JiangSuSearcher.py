# coding=utf-8

import PackageTool
import sys
from gs.KafkaAPI import KafkaAPI
from gs import TimeUtils
from geetest_broker.GeetestBroker import GeetestBrokerRealTime
import os
import uuid
import subprocess
from gs.Searcher import get_args
import json
from gs.TimeUtils import get_cur_time_jiangsu
from gs.TimeUtils import get_cur_time
from gs.CompareStatus import status_dict
from lxml import html
import requests
import datetime
from urlparse import urlparse
from gs.SpiderMan import SpiderMan
from gs.USCC import check

reload(sys)
sys.setdefaultencoding('utf8')

'''developer  liuwenhai'''


class JiangSuSearcher(SpiderMan, GeetestBrokerRealTime):
    def __init__(self, dst_topic=None):
        super(JiangSuSearcher, self).__init__(keep_session=True, dst_topic=dst_topic, max_try_times=5)
        self.error_judge = False  # 判断网站是否出错，False正常，True错误
        self.tag_a = ''
        self.id = ''
        self.org = ''
        self.seqId = ''
        self.reg_no = ''
        self.capiTypeName = ''
        self.set_config()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:47.0) Gecko/20100101 Firefox/47.0",
            "Host": "www.jsgsj.gov.cn:58888",
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
            "Connection": "keep-alive",
            "Referer": "http://www.jsgsj.gov.cn:58888/province/"
        }
        self.geetest_referer = "http://www.jsgsj.gov.cn:58888/province/"
        self.log_name = 'jiang_su_' + str(uuid.uuid1())
        self.geetest_product = 'popup'

    def set_config(self):
        self.plugin_path = os.path.join(sys.path[0], r'..\jiang_su\ocr\jiangsuocr.exe')
        self.province = u'江苏省'

    def get_request(self, url, **kwargs):
        domain = urlparse(url).hostname
        for t in range(self.max_try_times):
            if domain != 'www.jsgsj.gov.cn':
                domain = None
            proxy_config = self.get_proxy(domain)
            kwargs['proxies'] = {'http': 'http://%(user)d:%(pwd)s@%(proxy)s' % proxy_config,
                                 'https': 'https://%(user)d:%(pwd)s@%(proxy)s' % proxy_config}
            kwargs['timeout'] = min(15, proxy_config['timeout'])
            kwargs['allow_redirects'] = False
            kwargs.setdefault('headers', {})
            kwargs['headers']['Connection'] = 'close'
            kwargs['headers'][
                'User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:45.0) Gecko/20100101 Firefox/45.0'
            try:
                if self.session:
                    r = self.session.get(url=url, **kwargs)
                else:
                    r = requests.get(url=url, **kwargs)
                if u'由于您操作过于频繁' in r.text \
                        or "<script>window.location.href='/index/blackList'</script>" in r.text \
                        or 'http://www.gsxt.gov.cn/index/blackList' in r.text:
                    self.add_to_black_list(domain=domain, proxy_ip=proxy_config['proxy'].split(':')[0])
                else:
                    return r
            except requests.exceptions.RequestException, e:
                if t == self.max_try_times - 1:
                    raise e

    def post_request(self, url, **kwargs):
        domain = urlparse(url).hostname
        for t in range(self.max_try_times):
            if domain != 'www.gsxt.gov.cn':
                domain = None
            proxy_config = self.get_proxy(domain)
            kwargs['proxies'] = {'http': 'http://%(user)d:%(pwd)s@%(proxy)s' % proxy_config,
                                 'https': 'https://%(user)d:%(pwd)s@%(proxy)s' % proxy_config}
            kwargs['timeout'] = min(15, proxy_config['timeout'])
            kwargs['allow_redirects'] = False
            kwargs.setdefault('headers', {})
            kwargs['headers']['Connection'] = 'close'
            kwargs['headers'][
                'User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:45.0) Gecko/20100101 Firefox/45.0'
            # if 'headers' in kwargs:
            #     kwargs['headers']['Proxy-Authentication'] = proxy_config['secret_key']
            # else:
            #     kwargs['headers'] = {'Proxy-Authentication': proxy_config['secret_key']}
            try:
                if self.session:
                    r = self.session.post(url=url, **kwargs)
                else:
                    r = requests.post(url=url, **kwargs)
                if u'由于您操作过于频繁' in r.text \
                        or "<script>window.location.href='/index/blackList'</script>" in r.text \
                        or 'http://www.gsxt.gov.cn/index/blackList' in r.text:
                    self.add_to_black_list(domain=domain, proxy_ip=proxy_config['proxy'].split(':')[0])
                else:
                    return r
            except requests.exceptions.RequestException, e:
                if t == self.max_try_times - 1:
                    raise e

    def get_gt_challenge(self):
        url_1 = "http://www.jsgsj.gov.cn:58888/province/geetestViladateServlet.json?register=true&t=%s" % TimeUtils.get_cur_ts_mil()
        # print url_1
        self.info(u'**获取gt和challenge...')
        r_1 = self.get_request(url_1)
        json_1 = json.loads(r_1.text)
        self.gt = json_1['gt']
        self.challenge = json_1['challenge']

    def get_tag_a_from_page(self, keyword):
        if check(keyword):
            is_xydm = True
        else:
            is_xydm = False
        coded_name = ''
        result_list = []
        corp_prioritys = []
        headers = {
            "Host": 'www.jsgsj.gov.cn:58888',
            "Referer": "http://www.jsgsj.gov.cn:58888/province/login.jsp",
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:46.0) Gecko/20100101 Firefox/46.0",
            "Origin": "http: // www.jsgsj.gov.cn:58888"
            # 'Proxy-Authorization': self.proxy_config.get_auth_header()
        }

        validate = self.get_geetest_validate()

        url = "http://www.jsgsj.gov.cn:58888/province/geetestViladateServlet.json?validate=true"
        params = {
            'geetest_challenge': self.challenge,
            'geetest_seccode': '%s|jordan' % validate,
            'geetest_validate': '%s' % validate,
            'name': keyword,
            'type': 'search'
        }
        r = self.post_request(url=url, data=params, headers=headers)
        # print r.text
        name = json.loads(r.text)['name']
        for j in range(10):
            try:
                params = {'name': name, 'pageNo': 1, "pageSize": 10, "searchType": "qyxx"}
                url = 'http://www.jsgsj.gov.cn:58888/province/infoQueryServlet.json?queryCinfo=true'  # 此处验证ip
                r = self.post_request(url, data=params, headers=headers)
                result_dict = json.loads(r.text)
                result_list = result_dict['items']
                break
            except Exception, e:
                if j == 9:
                    raise e
        for result in result_list:
            name = result['CORP_NAME'].replace('(', u'（').replace(')', u'）')
            if is_xydm or name == keyword:
                corp_status = result['CORP_STATUS'].strip()
                corp_priority = status_dict[corp_status]
                result.update({'corp_priority': corp_priority})
                corp_prioritys.append(corp_priority)
        if corp_prioritys:
            corp_highest_priority = min(corp_prioritys)
        else:
            corp_highest_priority = 1
        for result in result_list:
            name = result['CORP_NAME'].replace('(', u'（').replace(')', u'）')
            if is_xydm or name == keyword:
                priority_condition = result['corp_priority'] == corp_highest_priority
                if priority_condition:
                    self.id = result["ID"]
                    self.org = result["ORG"]
                    self.seqId = result["SEQ_ID"]
                    self.tag_a = self.id + ";" + self.org + ";" + self.seqId
                    return self.tag_a
            else:
                self.id = result["ID"]
                self.org = result["ORG"]
                self.seqId = result["SEQ_ID"]
                self.tag_a = self.id + ";" + self.org + ";" + self.seqId
                return self.tag_a

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
            keyword = self.process_mc(keyword)
        self.session = requests.session()  # 初始化session
        # self.add_proxy(self.app_key)  # 为session添加代理
        res = 0
        self.cur_mc = ''  # 当前查询公司名称
        self.cur_zch = ''  # 当前查询公司注册号
        # keyword = keyword.replace('(', u'（').replace(')', u'）')  # 公司名称括号统一转成全角
        self.today = str(datetime.date.today()).replace('-', '')
        self.json_result.clear()
        self.json_result['inputCompanyName'] = keyword
        self.json_result['accountId'] = account_id
        self.json_result['taskId'] = task_id
        self.save_tag_a = True
        self.info(u'keyword: %s' % keyword)
        tag_a = ''
        if not tag_a:
            tag_a = self.get_tag_a_from_page(keyword)
        # if not tag_a:  # 等所有省份都修改结束，使用此段代码代替以上代码
        #     tag_a = self.get_tag_a_from_page(keyword, flags)
        if tag_a:
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
        self.info(u'消息写入kafka')
        # self.kafka.send(json.dumps(self.json_result, ensure_ascii=False))
        if 'Registered_Info' in self.json_result:
            self.json_result['inputCompanyName'] = self.json_result['Registered_Info'][0]['Registered_Info:enterprisename']
        self.send_msg_to_kafka(json.dumps(self.json_result, ensure_ascii=False))
        # self.info(json.dumps(self.json_result, ensure_ascii=False))
        return res

    def recognize_yzm(self, yzm_path):
        """
        识别验证码
        :param yzm_path: 验证码保存路径
        :return: 验证码识别结果
        """
        cmd = self.plugin_path + " " + yzm_path
        self.info(cmd)
        process = subprocess.Popen(cmd.encode('GBK', 'ignore'), stdout=subprocess.PIPE)
        process_out = process.stdout.read()
        # self.info('process_out', process_out
        answer = process_out.split('\r\n')[0].strip()
        # self.info('answer: ' + answer)
        return answer.decode('gbk', 'ignore')

    def get_search_args(self, tag_a, keyword):
        self.info(u'解析查询参数')
        # print tag_a
        self.cur_mc = keyword
        self.id = tag_a.split(";")[0]
        self.org = tag_a.split(";")[1]
        self.seqId = tag_a.split(";")[2]
        return 1

    def download_yzm(self):
        time_url = get_cur_time_jiangsu()
        image_url = 'http://www.jsgsj.gov.cn:58888/province/rand_img.jsp?type=7&temp=' + time_url[:-6].replace(" ",
                                                                                                               "%20")
        r = self.get_request(image_url, headers=self.headers)
        yzm_path = self.get_yzm_path()
        with open(yzm_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
                    f.flush()
            f.close()
        return yzm_path

    def parse_detail(self):
        """
        解析公司详情信息
        :param kwargs:
        :return:
        """
        self.get_ji_ben()
        self.get_gu_dong()
        self.get_bian_geng()
        self.get_zhu_yao_ren_yuan()
        # self.get_fen_zhi_ji_gou()
        # self.get_dong_chan_di_ya()
        # self.get_gu_quan_chu_zhi()
        # self.get_jing_ying_yi_chang()
        # self.get_si_fa_xie_zhu()

        # self.get_qing_suan()
        # self.get_xing_zheng_chu_fa()
        # self.get_yan_zhong_wei_fa()
        # self.get_chou_cha_jian_cha()
         # 苏州融创科技担保投资有限公司

    def get_ji_ben(self):
        """
        查询基本信息
        :return: 基本信息结果
        """
        family = 'Registered_Info'
        table_id = '01'
        result_values = dict()
        url = 'http://www.jsgsj.gov.cn:58888/ecipplatform/publicInfoQueryServlet.json?pageView=true'  # http://www.jsgsj.gov.cn:58888/ecipplatform/inner_ci/ci_queryCorpInfor_gsRelease.jsp
        params = {'id': self.id, 'org': self.org, 'seqId': self.seqId}
        r = self.get_request(url=url, params=params)
        self.info(u'基本信息')
        ji_ben_xinxi = json.loads(r.text)
        if not ji_ben_xinxi:
            self.error_judge = True
            self.info(r.text)
            raise ValueError('!!!!!!!!!!!!website is wrong!!!!!!!!!!!!!')
        self.cur_zch = ji_ben_xinxi.get('REG_NO', '')
        if self.cur_zch:
            if len(self.cur_zch) == 18:
                result_values[family + ':tyshxy_code'] = self.cur_zch
            else:
                result_values[family + ':zch'] = self.cur_zch
        result_values[family + ':registrationno'] = self.cur_zch
        result_values[family + ':enterprisename'] = ji_ben_xinxi.get('CORP_NAME', '')
        result_values[family + ':enterprisetype'] = ji_ben_xinxi.get('ZJ_ECON_KIND', '')
        result_values[family + ':residenceaddress'] = ji_ben_xinxi.get('ADDR', '')
        result_values[family + ':registeredcapital'] = ji_ben_xinxi.get('REG_CAPI_WS', '')
        result_values[family + ':legalrepresentative'] = ji_ben_xinxi.get('OPER_MAN_NAME', '')
        result_values[family + ':validityfrom'] = ji_ben_xinxi.get('FARE_TERM_START', '')
        result_values[family + ':validityto'] = ji_ben_xinxi.get('FARE_TERM_END', '')
        result_values[family + ':businessscope'] = ji_ben_xinxi.get('FARE_SCOPE', '')
        result_values[family + ':registrationinstitution'] = ji_ben_xinxi.get('BELONG_ORG', '')
        result_values[family + ':registrationstatus'] = ji_ben_xinxi.get('CORP_STATUS', '')
        result_values[family + ':establishmentdate'] = ji_ben_xinxi.get('START_DATE', '')
        result_values[family + ':approvaldate'] = ji_ben_xinxi.get('CHECK_DATE', '')

        result_values['rowkey'] = '%s_%s_%s_' % (self.cur_mc, table_id, self.cur_zch)
        result_values[family + ':province'] = u'江苏省'
        result_values[family + ':lastupdatetime'] = get_cur_time()
        self.json_result["Registered_Info"] = [result_values]

    def get_gu_dong(self):
        """
        查询股东信息
        :param param_pripid:
        :param param_type:
        :return:
        """
        family = 'Shareholder_Info'
        table_id = '04'
        result_list = []
        j = 1
        url = 'http://www.jsgsj.gov.cn:58888/ecipplatform/publicInfoQueryServlet.json?queryGdcz=true'
        params = {'id': self.id, 'org': self.org, 'seqId': self.seqId, 'curPage': 1, 'pageSize': 1000}
        r = self.post_request(url, data=params)
        self.info(u'股东信息')
        result_values = dict()
        investmentinfo = json.loads(r.text)["data"]
        for invest_dict in investmentinfo:
            result_values[family + ':shareholder_type'] = invest_dict.get('STOCK_TYPE', '')
            result_values[family + ':shareholder_name'] = invest_dict.get('STOCK_NAME', '')
            result_values[family + ':shareholder_certificationtype'] = invest_dict.get('IDENT_TYPE_NAME', '')
            result_values[family + ':shareholder_certificationno'] = invest_dict.get('IDENT_NO', '')
            invest_detail = self.get_investor_detail(invest_dict)
            result_values.update(invest_detail)
            result_values['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.cur_zch, self.today, j)
            result_values[family + ':registrationno'] = self.cur_zch
            result_values[family + ':enterprisename'] = self.cur_mc
            result_values[family + ':id'] = j
            result_list.append(result_values)
            result_values = {}
            j += 1
        self.json_result["Shareholder_Info"] = result_list

    def get_investor_detail(self, inv_dict):
        # print 'inv_dict', inv_dict
        if "CAPI_TYPE_NAME" not in inv_dict:
            inv_dict.update({u'CAPI_TYPE_NAME': u''})
        family = 'Shareholder_Info'
        params = {
            'seqId': inv_dict["SEQ_ID"],
            'org': inv_dict["ORG"],
            'id': inv_dict["ID"],
            'admitMain': '10',
            'capiTypeName': inv_dict["CAPI_TYPE_NAME"]
        }
        url = "http://www.jsgsj.gov.cn:58888/ecipplatform/publicInfoQueryServlet.json?queryGdczGdxx=true"
        r = self.get_request(url, params=params)
        detail = json.loads(r.text)
        detail_values = dict()
        detail_values[family + ':subscripted_capital'] = detail.get("SHOULD_CAPI", '')  # 认缴额
        detail_values[family + ':actualpaid_capital'] = detail.get("REAL_CAPI", '')  # 实缴额
        rjmx_list = []
        sjmx_list = []
        params = {
            "curPage": 1,
            "id": inv_dict["ID"],
            'org': inv_dict["ORG"],
            "type": 'rj',
            'admitMain': '10',
            'capiTypeName': inv_dict["CAPI_TYPE_NAME"]
        }
        url = "http://www.jsgsj.gov.cn:58888/ecipplatform/publicInfoQueryServlet.json?queryGdczGdxx=true"
        r = self.post_request(url, data=params)
        # print 'rrrrrrrrr', json.loads(r.text)
        rj = r.text.replace('SHOULD_CAPI_DATE', u'认缴出资日期') \
            .replace('SHOULD_CAPI', u'认缴出资额（万元）') \
            .replace('INVEST_TYPE_NAME', u'认缴出资方式') \
            .replace('REAL_CAPI', u'实缴出资额（万元）')
        detail_1 = json.loads(rj)
        if detail_1["data"]:
            detail_values[family + ':subscripted_time'] = detail_1["data"][0].get(u'认缴出资日期', '')
            detail_values[family + ':subscripted_method'] = detail_1["data"][0].get(u'认缴出资方式', '')
            detail_values[family + ':subscripted_amount'] = detail_1["data"][0].get(u'认缴出资额（万元）', '')
            rjmx_list = detail_1["data"]
            # print 'rjmx_list', rjmx_list
            for j in rjmx_list:
                j.update({u'认缴出资方式': detail_1["data"][0].get(u'认缴出资方式', '')})
                if u'实缴出资额（万元）' in j.keys():
                    j.pop(u'实缴出资额（万元）')
            detail_values[family + ':rjmx'] = rjmx_list
        params = {
            "curPage": 1,
            "id": inv_dict["ID"],
            'org': inv_dict["ORG"],
            "type": 'sj',
            'admitMain': '10',
            'capiTypeName': inv_dict["CAPI_TYPE_NAME"]
        }
        url = "http://www.jsgsj.gov.cn:58888/ecipplatform/publicInfoQueryServlet.json?queryGdczGdxx=true"
        r = self.post_request(url, data=params)
        sj = r.text.replace('REAL_CAPI_DATE', u'实缴出资日期') \
            .replace('REAL_CAPI', u'实缴出资额（万元）') \
            .replace('INVEST_TYPE_NAME', u'实缴出资方式') \
            .replace('SHOULD_CAPI', u'认缴出资额（万元）')
        detail_2 = json.loads(sj)
        if detail_2['data']:
            detail_values[family + ':actualpaid_time'] = detail_2["data"][0].get(u"实缴出资日期", '')
            detail_values[family + ':actualpaid_method'] = detail_2["data"][0].get(u"实缴出资方式", '')
            detail_values[family + ':actualpaid_amount'] = detail_2["data"][0].get(u"实缴出资额（万元）", '')
            sjmx_list = detail_2['data']
            # print 'sjmx_list', sjmx_list
            for j in sjmx_list:
                j.update({u"实缴出资方式": detail_2["data"][0].get(u"实缴出资方式", '')})
                if u'认缴出资额（万元）' in j.keys():
                    j.pop(u'认缴出资额（万元）')
            detail_values[family + ':sjmx'] = sjmx_list
        return detail_values

    def get_bian_geng(self):
        """
        查询变更信息
        :param param_pripid:
        :param param_type:
        :return:
        """
        family = 'Changed_Announcement'
        table_id = '05'
        result_list = []
        j = 1
        # self.json_result[family] = []
        url = 'http://www.jsgsj.gov.cn:58888/ecipplatform/publicInfoQueryServlet.json?queryBgxx=true'
        params = {'id': self.id, 'org': self.org, 'seqId': self.seqId, 'curPage': 1, 'pageSize': 1000}
        r = self.post_request(url, data=params)
        self.info(u'变更信息')
        result_values = dict()
        change_info = json.loads(r.text)["data"]
        for change_dict in change_info:
            result_values[family + ':changedannouncement_events'] = change_dict.get('CHANGE_ITEM_NAME', '')
            result_values[family + ':changedannouncement_before'] = change_dict.get('OLD_CONTENT', ' ')
            result_values[family + ':changedannouncement_after'] = change_dict.get('NEW_CONTENT', ' ')
            result_values[family + ':changedannouncement_date'] = change_dict.get('CHANGE_DATE', '')
            result_values['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.cur_zch, self.today, j)
            result_values[family + ':registrationno'] = self.cur_zch
            result_values[family + ':enterprisename'] = self.cur_mc
            result_values[family + ':id'] = j
            result_list.append(result_values)
            result_values = {}
            j += 1
        self.json_result["Changed_Announcement"] = result_list

    def get_zhu_yao_ren_yuan(self):
        """
        查询主要人员信息
        :param param_pripid:
        :param param_type:
        :return:
        """
        family = 'KeyPerson_Info'
        table_id = '06'
        result_list = []
        j = 1
        # self.json_result[family] = []
        url = 'http://www.jsgsj.gov.cn:58888/ecipplatform/publicInfoQueryServlet.json?queryZyry=true'
        params = {'id': self.id, 'org': self.org, 'seqId': self.seqId}
        r = self.get_request(url, params=params)
        self.info(u'主要人员信息')
        result_values = dict()
        keyperson_info = json.loads(r.text)
        for keyperson_dict in keyperson_info:
            result_values[family + ':keyperson_name'] = keyperson_dict['PERSON_NAME']
            result_values[family + ':keyperson_position'] = keyperson_dict['POSITION_NAME']
            result_values['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.cur_zch, self.today, j)
            result_values[family + ':registrationno'] = self.cur_zch
            result_values[family + ':enterprisename'] = self.cur_mc
            result_values[family + ':id'] = j
            result_list.append(result_values)
            result_values = {}
            j += 1
        self.json_result["KeyPerson_Info"] = result_list

    def get_fen_zhi_ji_gou(self):
        """
        查询分支机构信息
        :param param_pripid:
        :param param_type:
        :return:
        """
        family = 'Branches'
        table_id = '08'
        result_list = []
        j = 1
        # self.json_result[family] = []
        url = 'http://www.jsgsj.gov.cn:58888/ecipplatform/publicInfoQueryServlet.json?queryFzjg=true'
        params = {'id': self.id, 'org': self.org, 'seqId': self.seqId}
        r = self.get_request(url, params=params)
        self.info(u'分支机构')
        result_values = dict()
        branch_info = json.loads(r.text)
        for branch_dict in branch_info:
            result_values[family + ':branch_registrationname'] = branch_dict.get('DIST_NAME', '')
            result_values[family + ':branch_registrationinstitution'] = branch_dict.get('DIST_BELONG_ORG', '')
            result_values[family + ':branch_registrationno'] = branch_dict.get('DIST_REG_NO', '')
            result_values['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.cur_zch, self.today, j)
            result_values[family + ':registrationno'] = self.cur_zch
            result_values[family + ':enterprisename'] = self.cur_mc
            result_values[family + ':id'] = j
            result_list.append(result_values)
            result_values = {}
            j += 1
        self.json_result["Branches"] = result_list

    def get_qing_suan(self):
        pass

    def get_dong_chan_di_ya(self):
        """
        查询动产抵押信息
        :param param_pripid:
        :param param_type:
        :return:
        """
        family = 'Chattel_Mortgage'
        table_id = '11'
        result_list = []
        j = 1
        # self.json_result[family] = []
        url = 'http://www.jsgsj.gov.cn:58888/ecipplatform/publicInfoQueryServlet.json?queryDcdy=true'
        params = {'id': self.id, 'org': self.org, 'seqId': self.seqId, 'curPage': 1, 'pageSize': 1000}
        r = self.post_request(url, data=params)
        self.info(u'动产抵押信息')
        result_values = dict()
        mortgage_info = json.loads(r.text)["data"]
        for mortgage_dict in mortgage_info:
            result_values[family + ':chattelmortgage_registrationno'] = mortgage_dict.get('GUARANTY_REG_NO', '')
            result_values[family + ':chattelmortgage_registrationdate'] = mortgage_dict.get('START_DATE', '')
            result_values[family + ':chattelmortgage_registrationinstitution'] = mortgage_dict.get('CREATE_ORG', '')
            result_values[family + ':chattelmortgage_guaranteedamount'] = mortgage_dict.get('ASSURE_CAPI', '')
            result_values[family + ':chattelmortgage_status'] = mortgage_dict.get('STATUS', '')
            result_values[family + ':priclaseckind'] = mortgage_dict.get('ASSURE_KIND', '')  # 被担保主债权种类
            # result_values[family + ':priclaseckind'] = mortgage_dict.get('ASSURE_KIND', '')  # 被担保主债权种类
            mortgage_params = dict()
            mortgage_params['id'] = mortgage_dict['ID']
            mortgage_params['org'] = mortgage_dict['ORG']
            mortgage_params['seqId'] = mortgage_dict['SEQ_ID']
            diya_detail = self.get_diya_detail(mortgage_params, mortgage_dict.get('GUARANTY_REG_NO', ''),
                                               mortgage_dict.get('START_DATE', ''))
            result_values[family + ':detail'] = diya_detail

            result_values['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.cur_zch, self.today, j)
            result_values[family + ':registrationno'] = self.cur_zch
            result_values[family + ':enterprisename'] = self.cur_mc
            result_values[family + ':id'] = j
            result_list.append(result_values)
            result_values = {}
            j += 1
        self.json_result["Chattel_Mortgage"] = result_list
        # self.info(json.dumps(result_json_2, ensure_ascii=False)

    def get_diya_detail(self, mortgage_params, mot_no, mot_date):
        values = dict()
        if not mot_date: mot_date = ''
        mot_date = mot_date.replace(u'年', '-').replace(u'月', '-').replace(u'日', '')

        """被担保债券概况"""
        family = '被担保债券概况'
        # bdbzqgk = {}
        # bdbzqgk_table_id = '56'
        r_1 = self.post_request(
            'http://www.jsgsj.gov.cn:58888/ecipplatform/publicInfoQueryServlet.json?queryDcdyDetail=true',
            data=mortgage_params)
        result = r_1.json()
        # bdbzqgk_dict = dict()
        values[family] = {}
        values[family]['担保的范围'] = result[0]['ASSURE_SCOPE']
        values[family]['种类'] = result[0]['ASSURE_KIND']
        values[family]['债务人履行债务的期限'] = result[0]['ASSURE_START_DATE']
        values[family]['备注'] = result[0]['REMARK']
        values[family]['数额'] = result[0]['ASSURE_CAPI']
        # bdbzqgk_dict['rowkey'] = '%s_%s_%s_%s' % (self.cur_mc, mot_no, mot_date, bdbzqgk_table_id)
        # bdbzqgk_dict[family + ':registrationno'] = self.cur_zch
        # bdbzqgk_dict[family + ':enterprisename'] = self.cur_mc
        # bdbzqgk.append(bdbzqgk_dict)
        # values['Chattel_Mortgage:bdbzqgk'] = bdbzqgk  # 被担保债券概况

        """动产抵押登记信息"""
        # dcdydj = list()
        # dcdydj_table_id = '63'
        family = '动产抵押登记信息'
        values[family] = {}
        # dcdydj_dict = dict()
        values[family]['登记编号'] = result[0]['GUARANTY_REG_NO']
        if not result[0]['START_DATE']: result[0]['START_DATE'] = ''
        values[family]['登记日期'] = result[0]['START_DATE'].replace(u'年', '-').replace(u'月', '-').replace(u'日',
                                                                                                       '')
        values[family]['登记机关'] = result[0]['CREATE_ORG']
        # values['rowkey'] = '%s_%s_%s_%s' % (self.cur_mc, mot_no, mot_date, dcdydj_table_id)
        # values[family + ':registrationno'] = self.cur_zch
        # values[family + ':enterprisename'] = self.cur_mc
        # dcdydj.append(dcdydj_dict)
        # values['Chattel_Mortgage:dcdydj'] = dcdydj  # 动产抵押登记信息

        """注销信息"""
        family = '注销信息'
        values[family] = {}
        values[family]['注销日期'] = result[0]['WRITEOFF_DATE']
        values[family]['注销原因'] = result[0]['WRITEOFF_REASON']

        """抵押权人概况"""
        r_2 = self.post_request(
            'http://www.jsgsj.gov.cn:58888/ecipplatform/publicInfoQueryServlet.json?queryDcdyDyqrgk=true',
            data=mortgage_params)
        result = r_2.json()['data']
        family = '抵押权人概况'
        values[family] = []
        # dyqrgk = list()
        # dyqrgk_table_id = '55'  # 抵押权人概况表格
        # k = 1
        for dyqrgk_dict in result:
            dyqrgk_values = dict()
            count = 1
            dyqrgk_values['序号'] = count
            dyqrgk_values['抵押权人名称'] = dyqrgk_dict.get('AU_NAME', '')
            dyqrgk_values['抵押权人证照/证件类型'] = dyqrgk_dict.get('AU_CER_TYPE', '')
            dyqrgk_values['证照/证件号码'] = dyqrgk_dict.get('AU_CER_NO', '')
            values[family].append(dyqrgk_values)
            count += 1
            # dyqrgk_values['rowkey'] = '%s_%s_%s_%s_%d' % (self.cur_mc, mot_no, mot_date, dyqrgk_table_id, k)
            # dyqrgk_values[family + ':registrationno'] = self.cur_zch
            # dyqrgk_values[family + ':enterprisename'] = self.cur_mc
            # dyqrgk_values[family + ':id'] = k
            # dyqrgk.append(dyqrgk_values)
            # k += 1
        # values['Chattel_Mortgage:dyqrgk'] = dyqrgk  # 抵押权人概况

        """抵押物概况"""
        family = '抵押物概况'
        values[family] = []
        # dywgk = list()
        # dywgk_table_id = '57'
        r_2 = self.post_request(
            'http://www.jsgsj.gov.cn:58888/ecipplatform/publicInfoQueryServlet.json?queryDcdyDywgk=true',
            data=mortgage_params)
        result = r_2.json()['data']
        # k = 1
        for dyqrgk_dict in result:
            dyqrgk_values = dict()
            count = 1
            dyqrgk_values['序号'] = count
            dyqrgk_values['名称'] = dyqrgk_dict.get('NAME', '')
            dyqrgk_values['所有权归属'] = dyqrgk_dict.get('BELONG_KIND', '')
            dyqrgk_values['数量、质量、状况、所在地等情况'] = dyqrgk_dict.get('PA_DETAIL', '')
            dyqrgk_values['备注'] = dyqrgk_dict.get('REMARK', '')
            values[family].append(dyqrgk_values)
            count += 1
        # dyqrgk_values['rowkey'] = '%s_%s_%s_%s_%d' % (self.cur_mc, mot_no, mot_date, dywgk_table_id, k)
        #     dyqrgk_values[family + ':registrationno'] = self.cur_zch
        #     dyqrgk_values[family + ':enterprisename'] = self.cur_mc
        #     dyqrgk_values[family + ':id'] = k
        #     dywgk.append(dyqrgk_values)
        #     k += 1
        # values[family + ':dywgk'] = dywgk  # 抵押物概况
        return values

    def get_gu_quan_chu_zhi(self):  # finished
        """
        查询股权出置信息
        :param param_pripid:
        :param param_type:
        :return:
        """
        family = 'Equity_Pledge'
        table_id = '12'
        result_list = []
        j = 1
        url = 'http://www.jsgsj.gov.cn:58888/ecipplatform/publicInfoQueryServlet.json?queryGqcz=true'
        params = {'id': self.id, 'org': self.org, 'seqId': self.seqId, 'curPage': 1, 'pageSize': 1000}
        r = self.post_request(url, data=params)
        self.info(u'股权出质')
        result_values = dict()
        pledge_info = json.loads(r.text)["data"]
        for pledge_dict in pledge_info:
            pledge_text = pledge_dict.get('D1', '')
            tree = html.fromstring(pledge_text)
            td_list = tree.xpath(".//td")
            result_values[family + ':equitypledge_registrationno'] = td_list[1].text
            result_values[family + ':equitypledge_pledgor'] = td_list[2].text
            result_values[family + ':equitypledge_pledgorid'] = td_list[3].text
            result_values[family + ':equitypledge_amount'] = td_list[4].text
            result_values[family + ':equitypledge_pawnee'] = td_list[5].text
            result_values[family + ':equitypledge_pawneeid'] = td_list[6].text
            result_values[family + ':equitypledge_registrationdate'] = td_list[7].text.replace(u'年', '-').replace(u'月',
                                                                                                                  '-').replace(
                u'日', '')
            result_values[family + ':equitypledge_status'] = td_list[8].text
            result_values[family + ':equitypledge_announcedate'] = td_list[9].text.replace(u'年', '-').replace(u'月',
                                                                                                              '-').replace(
                u'日', '')
            if pledge_dict.get('CHANGESITUATION', '') == u'详情':
                pledge_params = dict()
                pledge_params['id'] = pledge_dict['ID']
                pledge_params['org'] = pledge_dict['ORG']
                pledge_params['seqId'] = pledge_dict['SEQ_ID']
                pledge_detail = self.get_pledge_detail(pledge_params, td_list[1].text, td_list[7].text)
                result_values[family + ':detail'] = pledge_detail
            # result_values[family + ':equitypledge_pawnee'] = pledge_dict.get('C5', '')
            else:
                result_values[family + ':detail'] = {}
            result_values['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.cur_zch, self.today, j)
            result_values[family + ':registrationno'] = self.cur_zch
            result_values[family + ':enterprisename'] = self.cur_mc
            result_values[family + ':id'] = j
            result_list.append(result_values)
            result_values = {}
            j += 1
        self.json_result["Equity_Pledge"] = result_list
        # print result_list

    def get_pledge_detail(self, pledge_params, equity_no, equity_date):
        equity_date = equity_date.replace(u'年', '-').replace(u'月', '-').replace(u'日', '')

        family = '股权出质注销信息'
        # table_id = '60'
        # result_values = dict()
        # pledge_list = list()
        values = dict()

        r = self.post_request(
            'http://www.jsgsj.gov.cn:58888/ecipplatform/publicInfoQueryServlet.json?queryGqczDetail=true',
            data=pledge_params)
        # print r.text
        result = json.loads(r.text)
        values[family]={}
        values[family]['注销日期'] = result.get('CREATE_DATE', '').replace(u'年', '-').replace(u'月', '-').replace(
            u'日', '')  #
        values[family]['注销原因'] = result.get('WRITEOFF_REASON', '')  #
        # values['rowkey'] = '%s_%s_%s_%s' % (self.cur_mc, equity_no, equity_date, table_id)
        # values[family + ':registrationno'] = self.cur_zch
        # values[family + ':enterprisename'] = self.cur_mc
        # pledge_list.append(values)
        # result_values['Equity_Pledge:gqczzx'] = pledge_list
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
        result_list = []
        j = 1
        # self.json_result[family] = []
        url = 'http://www.jsgsj.gov.cn:58888/ecipplatform/publicInfoQueryServlet.json?queryXzcf=true'
        params = {'id': self.id, 'org': self.org, 'seqId': self.seqId, 'curPage': 1, 'pageSize': 1000}
        r = self.post_request(url, data=params)
        self.info(u'行政处罚')
        result_values = dict()
        penalty_info = json.loads(r.text)["data"]
        for penalty_dict in penalty_info:
            result_values[family + ':penalty_code'] = penalty_dict.get('PEN_DEC_NO', '')
            result_values[family + ':penalty_illegaltype'] = penalty_dict.get('ILLEG_ACT_TYPE', '')
            result_values[family + ':penalty_decisioncontent'] = penalty_dict.get('PEN_TYPE', '')
            result_values[family + ':penalty_decisioninsititution'] = penalty_dict.get('PUNISH_ORG_NAME', '')
            result_values[family + ':penalty_decisiondate'] = penalty_dict.get('PUNISH_DATE', '')
            result_values[family + ':penalty_publicationdate'] = penalty_dict.get('CREATE_DATE', '')

            result_values['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.cur_zch, self.today, j)
            result_values[family + ':registrationno'] = self.cur_zch
            result_values[family + ':enterprisename'] = self.cur_mc
            result_values[family + ':id'] = j
            result_list.append(result_values)
            result_values = {}
            j += 1
        self.json_result["Administrative_Penalty"] = result_list
        # self.info(json.dumps(result_json_2, ensure_ascii=False)

    def get_jing_ying_yi_chang(self):
        """
        查询经营异常信息
        :param param_pripid:
        :param param_type:
        :return:
        """
        family = 'Business_Abnormal'
        table_id = '14'
        result_list = []
        j = 1
        # self.json_result[family] = []
        url = 'http://www.jsgsj.gov.cn:58888/ecipplatform/publicInfoQueryServlet.json?queryJyyc=true'
        params = {'id': self.id, 'org': self.org, 'seqId': self.seqId, 'curPage': 1, 'pageSize': 1000}
        r = self.post_request(url, data=params)
        self.info(u'经营异常')
        result_values = dict()
        abnormal_info = json.loads(r.text)["data"]
        for abnormal_dict in abnormal_info:
            result_values[family + ':abnormal_events'] = abnormal_dict.get('FACT_REASON', '')
            result_values[family + ':abnormal_datesin'] = abnormal_dict.get('MARK_DATE', '')
            result_values[family + ':abnormal_moveoutreason'] = abnormal_dict.get('REMOVE_REASON', '')
            result_values[family + ':abnormal_datesout'] = abnormal_dict.get('CREATE_DATE', '')
            result_values[family + ':abnormal_decisioninstitution'] = abnormal_dict.get('CREATE_ORG', '')

            result_values['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.cur_zch, self.today, j)
            result_values[family + ':registrationno'] = self.cur_zch
            result_values[family + ':enterprisename'] = self.cur_mc
            result_values[family + ':id'] = j
            result_list.append(result_values)
            result_values = {}
            j += 1
        self.json_result["Business_Abnormal"] = result_list
        # self.info(json.dumps(result_json_2, ensure_ascii=False)

    def get_yan_zhong_wei_fa(self):
        """
        查询严重违法信息
        :param param_pripid:
        :param param_type:
        :return:
        """
        pass

    def get_chou_cha_jian_cha(self):
        """
        查询抽查检查信息
        :param param_pripid:
        :param param_type:
        :return:
        """
        family = 'Spot_Check'
        table_id = '16'
        result_list = []
        j = 1
        # self.json_result[family] = []
        url = 'http://www.jsgsj.gov.cn:58888/ecipplatform/publicInfoQueryServlet.json?queryCcjc=true'
        params = {'id': self.id, 'org': self.org, 'seqId': self.seqId, 'curPage': 1, 'pageSize': 1000}
        r = self.post_request(url, data=params)
        self.info(u'抽查检查信息')
        result_values = dict()
        spot_info = json.loads(r.text)["data"]
        for spot_dict in spot_info:
            result_values[family + ':check_institution'] = spot_dict.get('CHECK_ORG', '')
            result_values[family + ':check_type'] = spot_dict.get('CHECK_TYPE', '')
            result_values[family + ':check_date'] = spot_dict.get('CHECK_DATE', '')
            result_values[family + ':check_result'] = spot_dict.get('CHECK_RESULT', '')

            result_values['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.cur_zch, self.today, j)
            result_values[family + ':registrationno'] = self.cur_zch
            result_values[family + ':enterprisename'] = self.cur_mc
            result_values[family + ':id'] = j
            result_list.append(result_values)
            result_values = {}
            j += 1
        self.json_result["Spot_Check"] = result_list
        # self.info(self.json_result
        # self.info(json.dumps(result_json_2, ensure_ascii=False)
        # self.info(json.dumps(result_json, ensure_ascii=False)

    def get_si_fa_xie_zhu(self):
        self.info(u'司法协助')
        family = 'sharesfrost'
        table_id = '25'
        result_list = []
        j = 1
        # self.json_result[family] = []
        url = 'http://www.jsgsj.gov.cn:58888/ecipplatform/publicInfoQueryServlet.json?querySfxz=true'
        params = {'id': self.id, 'org': self.org, 'seqId': self.seqId, 'curPage': 1, 'pageSize': 1000}
        r = self.post_request(url, data=params)
        result_values = dict()
        result_data = r.json()["data"]
        for result_dict in result_data:
            result_values[family + ':fro_bzxr'] = result_dict.get('ASSIST_NAME', '')
            result_values[family + ':fro_zxfy'] = result_dict.get('EXECUTE_COURT', '')
            result_values[family + ':fro_zxtzswh'] = result_dict.get('NOTICE_NO', '')
            result_values[family + ':fro_lx'] = result_dict.get('FREEZE_STATUS', '').split('|')[0]
            result_values[family + ':fro_zt'] = result_dict.get('FREEZE_STATUS', '').split('|')[-1]
            result_values[family + ':froam'] = result_dict.get('FREEZE_AMOUNT', '')
            # result_values[family + ':shareholder_name'] = result_dict.get('STOCK_NAME', '')
            # result_values[family + ':shareholder_certificationtype'] = result_dict.get('IDENT_TYPE_NAME', '')
            # result_values[family + ':shareholder_certificationno'] = result_dict.get('IDENT_NO', '')
            if result_values[family + ':fro_lx'] == u'股东变更':
                params = {'id': result_dict['ID'], 'org': result_dict['ORG'], 'seqId': result_dict['SEQ_ID']}
                sharefrost_detail = self.get_sharefrost_detail_gd(params)
            else:
                params = {'id': result_dict['ID'], 'org': result_dict['ORG']}
                sharefrost_detail = self.get_sharefrost_detail(params)
            # result_values.update(sharefrost_detail)
            result_values[family + ':detail'] = sharefrost_detail
            result_values['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.cur_zch, self.today, j)
            result_values[family + ':registrationno'] = self.cur_zch
            result_values[family + ':enterprisename'] = self.cur_mc
            result_values[family + ':id'] = j
            result_list.append(result_values)
            result_values = {}
            j += 1
        self.json_result["sharesfrost"] = result_list

    def get_sharefrost_detail(self, params):
        family = '冻结情况'
        url = "http://www.jsgsj.gov.cn:58888/ecipplatform/publicInfoQueryServlet.json?querySfxzGqdjDetail=true"
        r = self.get_request(url, params=params)
        detail = r.json()['djInfo'][0]
        detail_values = dict()
        detail_values[family] = {}
        detail_values[family]['执行法院'] = detail.get("EXECUTE_COURT", '')
        detail_values[family]['执行事项'] = detail.get("ASSIST_ITEM", '')
        detail_values[family]['执行通知书文号'] = detail.get("ADJUDICATE_NO", '')
        detail_values[family]['被执行人持有股权、其它投资权益的数额'] = detail.get("FREEZE_AMOUNT", '')
        detail_values[family]['被执行人证件种类'] = detail.get("ASSIST_IDENT_TYPE", '')
        detail_values[family]['被执行人证件号码'] = detail.get("ASSIST_IDENT_NO", '')
        detail_values[family]['冻结期限自'] = detail.get("FREEZE_START_DATE", '')
        detail_values[family]['冻结期限至'] = detail.get("FREEZE_END_DATE", '')
        detail_values[family]['冻结期限'] = detail.get("FREEZE_YEAR_MONTH", '')
        detail_values[family]['公示日期'] = detail.get("PUBLIC_DATE", '')
        # detail_values[family + ':fro_djqx'] = detail.get("FREEZE_YEAR_MONTH", '')
        # detail_values[family + ':fro_djqx'] = detail.get("FREEZE_YEAR_MONTH", '')
        return detail_values

    def get_sharefrost_detail_gd(self, params):
        family = 'sharesfrost'
        url = "http://www.jsgsj.gov.cn:58888/ecipplatform/publicInfoQueryServlet.json?querySfxzGdbgDetail=true"
        r = self.get_request(url, params=params)
        detail = r.json()[0]
        detail_values = dict()
        detail_values[family + ':fro_zxsx'] = detail.get("ASSIST_ITEM", '')
        detail_values[family + ':fro_zxcdswh'] = detail.get("ADJUDICATE_NO", '')
        detail_values[family + ':fro_cyse'] = detail.get("FREEZE_AMOUNT", '')
        detail_values[family + ':fro_bzxrzzzl'] = detail.get("ASSIST_IDENT_TYPE", '')
        detail_values[family + ':fro_bzxrzzhm'] = detail.get("ASSIST_IDENT_NO", '')
        detail_values[family + ':frofrom'] = detail.get("FREEZE_START_DATE", '')
        detail_values[family + ':fro_djqx_to'] = detail.get("FREEZE_END_DATE", '')
        detail_values[family + ':fro_djqx'] = detail.get("FREEZE_YEAR_MONTH", '')
        detail_values[family + ':fro_gsrq'] = detail.get("PUBLIC_DATE", '')
        detail_values[family + ':fro_xzzxrq'] = detail.get("ASSIST_DATE", '')
        detail_values[family + ':fro_srr'] = detail.get("ACCEPT_NAME", '')
        detail_values[family + ':fro_srrzjzl'] = detail.get("ACCEPT_IDENT_TYPE", '')
        detail_values[family + ':fro_srrzjhm'] = detail.get("ACCEPT_IDENT_NO", '')
        detail_values[family + ':fro_gqszgs'] = detail.get("CORP_NAME", '')
        return detail_values

    def get_nian_bao_link(self):
        """
        获取年报url
        :param param_pripid:
        :param param_type:
        :return:
        """
        pass
        # params = {"REG_NO": "913201002496827567",
        #   "propertiesName": "query_report_list",
        #   "showRecordLine": "0",
        #   "specificQuery": "gs_pb",
        #   }
        # url = "http://www.jsgsj.gov.cn:58888/ecipplatform/nbServlet.json?nbEnter=true"
        # r = self.post_request(url, params=params)
        # nianbao_list = json.loads(r.text)
        # for nianbao in nianbao_list:

        # def get_request(self, url, params={}, t=0):
        #     try:
        #         return self.session.get(url=url, headers=self.headers, params=params)
        #     except RequestException, e:
        #         if t == 5:
        #             raise e
        #         else:
        #             return self.get_request(url, params, t+1)
        #
        # def post_request(self, url, params, t=0):
        #     try:
        #         return self.session.post(url=url, headers=self.headers, data=params)
        #     except RequestException, e:
        #         if t == 5:
        #             raise e
        #         else:
        #             return self.post_request(url, params, t+1)


if __name__ == '__main__':
    searcher = JiangSuSearcher()
    # searcher = JiangSuSearcher('GSCrawlerResultTest')
    # searcher = JiangSuSearcher('GsCrawlerOnline')
    args_dict = get_args()
    if args_dict:
        searcher.submit_search_request(keyword=args_dict['companyName'], account_id=args_dict['accountId'],
                                       task_id=args_dict['taskId'])
    else:

        searcher.submit_search_request('91320000134773930E')
        # searcher.submit_search_request(u"江苏省建设集团有限公司")
        searcher.info(json.dumps(searcher.json_result, ensure_ascii=False))
