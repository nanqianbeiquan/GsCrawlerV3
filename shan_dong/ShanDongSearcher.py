#coding=utf-8
import PackageTool
from bs4 import BeautifulSoup
import json
import re
from ShanDongConfig import *
from gs import TimeUtils
import sys
from geetest_broker.GeetestBroker import GeetestBrokerOffline
import urllib
from gs.Searcher import Searcher
from gs.Searcher import get_args
import requests
from gs.TimeUtils import *
import hashlib
from gs.CompareStatus import *
import platform
if platform.system() == 'Windows':
    import PyV8
else:
    from pyv8 import PyV8
requests.packages.urllib3.disable_warnings()
m = hashlib.md5()
reload(sys)
sys.setdefaultencoding('utf-8')


class ShanDongSearcher(Searcher, GeetestBrokerOffline):
    json_result = {}
    load_func_dict = {}
    pattern = re.compile("\s")
    cur_mc = ''
    cur_zch = ''
    code = ''
    save_tag_a = False
    tag_a = None
    resdetail = None
    # token = None

    def __init__(self, dst_topic=None):
        super(ShanDongSearcher, self).__init__(dst_topic=dst_topic, use_proxy=True)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:45.0) Gecko/20100101 Firefox/45.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
        }

        self.host = 'http://218.57.139.24/pub/gsgsdetail/'
        self.set_config()
        self.corp_id = ''
        self.corp_org = ''
        self.enttype = ''
        self.encrptpripid = ''

    def set_config(self):
        self.province = u'山东省'

    def get_token_from_page(self):
        self.headers['Host'] = 'sd.gsxt.gov.cn'
        self.headers['Referer'] = 'http://www.gsxt.gov.cn/index.html'
        # self.headers['Referer'] = 'http://sd.gsxt.gov.cn/'
        url_1 = "http://sd.gsxt.gov.cn"
        # url_1 = "http://sd.gsxt.gov.cn"
        # params = {'ad_check': 1}
        # headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0',
        #            'Host': 'sd.gsxt.gov.cn'}
        r_1 = self.get_request(url=url_1)
        # print '-'*100
        # print r_1.headers
        # print r_1.text
        soup_1 = BeautifulSoup(r_1.text, 'lxml')
        if len(soup_1.select('input[name=_csrf]')) == 0:
            self.set_cookie(r_1.text)
            # print '+'*100
            _r = self.get_request('http://sd.gsxt.gov.cn/?ad_check=1')
            # print '*'*100
            soup_1 = BeautifulSoup(_r.text, 'html5lib')
        self.token = soup_1.select('input[name=_csrf]')[0].attrs['value']
        # print 'self.token', self.token
        return self.token

    def get_tag_a_from_page(self, keyword, flags=True):
        self.get_lock_id()
        best_djzt = None
        url_4 = "http://sd.gsxt.gov.cn/pub/query/"
        params_4 = {
            'isjyyc': 0,
            'isyzwf': 0,
            'keyword': keyword,
        }
        self.headers['X-CSRF-TOKEN'] = self.get_token_from_page()
        r_4 = self.post_request(url_4, params=params_4)
        # print '*r4*'*10, r_4.text
        result_text = json.loads(r_4.text)
        result_json = result_text['results']
        self.xydm_if = ''
        self.zch_if = ''
        cnt = 0
        tag_a = None
        keyword_tran = keyword.replace('(', u'（').replace(')', u'）')
        if result_json:
            for i, item in enumerate(result_json):
                cnt += 1
                name_tran = re.sub('<[^>]+>', '', item['entname'].encode('utf8').strip())
                name_tran = self.process_mc(name_tran)
                if item['regstate']:
                    regstate = item['regstate']
                    if regstate == '1':
                        status = u'存续'
                    elif regstate == '2':
                        status = u'吊销'
                    elif regstate == '3':
                        status = u'注销'
                    else:
                        status = u'迁出'
                # print 'status_1', status
                if keyword_tran == name_tran:
                    if compare_status(status, best_djzt) >= 0:
                        # print 'status', compare_status(status, best_djzt)
                        best_djzt = status
                        self.kw = keyword_tran
                        pripid1 = item['pripid']
                        tag_a = 'http://sd.gsxt.gov.cn/pub/jbxx/qy/'+pripid1+'/jbxx'
                        # print 'tag_a:', tag_a
                        detail = self.get_request_302(tag_a)
                        # print 'detail*'*15
                        # print detail.text
                        bs = BeautifulSoup(detail.text, 'lxml')
                        pripid = bs.find(id="pripid").get('value')
                        # print 'pripid*'*10, pripid
                        self.headers['Referer'] = tag_a
                        url = 'http://sd.gsxt.gov.cn/pub/jbxx/qy/'+pripid
                        # print 'A'*10,url
                        for i in range(5):
                            r = self.post_request(url=url, headers=self.headers)
                            if r.status_code != 200:
                                continue
                            else:
                                break
                        if not json.loads(r.text)['jbxx']:
                            url = 'http://sd.gsxt.gov.cn/pub/jbxx/gt/'+pripid
                            # print 'B'*10,url
                            r = self.post_request(url=url, headers=self.headers)
                        r.encoding = 'utf-8'
                        self.detail_html = r.text
            return tag_a
        else:
            self.info(u'查询无结果')
            return None

    def get_gt_challenge(self, t=1):
        if t == 15:
            raise Exception(u'获取不到challenge')
        self.info(u'第%d次获取challenge。。。' % t)
        ts_1 = TimeUtils.get_cur_ts_mil()
        url_1 = "http://sd.gsxt.gov.cn/pub/geetest/register/%s?_=%s" % (TimeUtils.get_cur_ts_mil(), ts_1)
        r_1 = self.get_request(url_1)
        try:
            self.challenge = str(json.loads(r_1.text)['challenge'])
            self.gt = str(json.loads(r_1.text)['gt'])
        except:
            self.get_gt_challenge(t+1)

    def get_search_args(self, tag_a, keyword):
        self.tag_a = tag_a
        # print 'get_search_args_tag_a:', self.tag_a
        if tag_a:
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
        # html = open('C:/Users/huaixuan.guan/Desktop/sd_ls.txt')
        # data = html.read().decode('gbk')
        # html.close()
        # self.detail_html = data
        # print 'r.text', data
        # soup = BeautifulSoup(html, 'html5lib')
        # li_list = soup.find(class_='detailheader').find(class_='col-md-9').find_all('div')
        # mc = li_list[0].contents[0]
        # code = li_list[1].contents[1]
        # print 'r.text', mc, code
        # div_element_list = soup.find(id='sub_tab_01').find_all(class_='content1')
        self.get_ji_ben()
        if 'czxx' in json.loads(self.detail_html):
            if u'合作社' in self.kw or u'联合社' in self.kw:
                pass
            else:
                self.get_gu_dong()
        if 'bgsx' in json.loads(self.detail_html):
            self.get_bian_geng()
        if 'ryxx' in json.loads(self.detail_html):
            self.get_zhu_yao_ren_yuan()
        if u'主要人员信息' in self.detail_html:
            # token = self.resdetail.select('meta')[3].attrs['content']
            # self.token = token
            self.get_zhu_yao_ren_yuan()
        elif u'主管部门（出资人）信息' in self.detail_html:
            # token = self.resdetail.select('meta')[2].attrs['content']
            # self.token = token
            self.get_zhu_guan_bu_men()
        # self.get_fen_zhi_ji_gou()
        # self.get_qing_suan()
        # self.get_dong_chan_di_ya()
        # self.get_gu_quan_chu_zhi()
        # self.get_xing_zheng_chu_fa(tag_a)
        # self.get_jing_ying_yi_chang()
        # self.get_yan_zhong_wei_fa(tag_a)
        # self.get_chou_cha_jian_cha()
        self.release_lock_id()

    def get_ji_ben(self):
        """
        查询基本信息
        :return:
        """
        # self.src_table = 'enterprise_credit_info.dtjk_company_src_test'
        self.info(u'解析基本信息...')
        family = 'Registered_Info'
        table_id = '01'
        self.json_result[family] = []
        self.json_result[family].append({})
        content = self.detail_html.encode('utf-8').replace("\n", '').replace("\r\n", '').replace("\r\n", '')
        # print "content", content
        result_text = json.loads(content)
        result_json = result_text['jbxx']
        # print "result_json:", result_json
        for j in result_json:
            if j in ji_ben_dict:
                col = family + ':' + ji_ben_dict[j]
                val = result_json[j]
                self.json_result[family][-1][col] = val
            if j == 'entname' or j == 'traname':
                self.cur_mc = result_json[j].replace('(', u'（').replace(')', u'）')
            if j == 'regstate':
                if result_json[j] in ['1', '2', '3']:
                    a = [u"存续", u"吊销", u"注销"]
                    self.json_result[family][-1]['Registered_Info:registrationstatus'] = a[['1', '2', '3'].index(result_json[j])]
                else:
                    self.json_result[family][-1]['Registered_Info:registrationstatus'] = result_json[j]
            if j == 'enttype' and '9' in result_json['enttype']:
                self.json_result[family][-1]['Registered_Info:enterprisetype'] = u'个体工商户'
            if 'compform' in result_json:
                if result_json['compform']:
                    self.json_result[family][-1]['Registered_Info:compositionform'] = u'个人经营'
                else:
                    self.json_result[family][-1]['Registered_Info:compositionform'] = u'家庭经营'
            if j == 'uniscid':
                if result_json['uniscid']:
                    self.cur_zch = result_json['uniscid']
                else:
                    self.cur_zch = result_json['regno']
                self.json_result[family][-1]['Registered_Info:tyshxy_code'] = result_json['uniscid']
            if j == 'regcap':
                if result_json['regcapcur']:
                    self.json_result[family][-1]['Registered_Info:registeredcapital'] = str(result_json[j]) + u'万' +\
                        result_json['regcapcur']
                else:
                    self.json_result[family][-1]['Registered_Info:registeredcapital'] = str(result_json[j]) + u'万'
        self.json_result[family][-1]['rowkey'] = '%s_%s_%s_' % (self.cur_mc, table_id, self.cur_zch)
        self.json_result[family][-1][family + ':registrationno'] = self.cur_zch
        self.json_result[family][-1][family + ':enterprisename'] = self.cur_mc
        self.json_result[family][-1][family + ':province'] = self.province
        self.json_result[family][-1][family + ':lastupdatetime'] = get_cur_time()
        # print json.dumps(self.json_result[family], ensure_ascii=False)

    def get_gu_dong(self):
        """
        查询股东信息
        :return:
        """
        self.info(u'解析股东信息...')
        family = 'Shareholder_Info'
        table_id = '04'
        self.json_result[family] = []
        content = self.detail_html.encode('utf-8').replace("\n", '').replace("\n", '')
        # print "content", content
        result_text = json.loads(content)
        result_json = result_text['czxx']
        # print 'result_json:', result_json
        for j in result_json:
            self.json_result[family].append({})
            for k in j:
                if k in gu_dong_dict:
                    col = family + ':' + gu_dong_dict[k]
                    val = j[k]
                    self.json_result[family][-1][col] = val
            if j['recid']:
                link = j['recid']
                detail_list = self.get_gu_dong_detail(link)
                # print 'detail_list', detail_list
                self.json_result[family][-1].update(detail_list)
            for i in range(len(self.json_result[family])):
                self.json_result[family][i]['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.cur_zch, self.today, i+1)
                self.json_result[family][i][family + ':registrationno'] = self.cur_zch
                self.json_result[family][i][family + ':enterprisename'] = self.cur_mc
                self.json_result[family][i][family + ':id'] = self.today+str(i+1)
                # print json.dumps(self.json_result[family][i], ensure_ascii=False)
            # print json.dumps(self.json_result[family], ensure_ascii=False)

    def get_gu_dong_detail(self, link):
        """
        查询股东详情
        :param link:
        :return:
        """
        value = {}
        rjmx_list = []
        sjmx_list = []
        rjmx_dict = dict()
        sjmx_dict = dict()
        url = 'http://sd.gsxt.gov.cn/pub/czxx/'+link
        # print "gu_dong_self.headers:",self.headers
        t = 1
        for i in range(15):
            r = self.post_request(url=url, headers=self.headers, verify=False)
            if r.status_code != 200:
                t += 1
                self.info(u'第%d次获取股东详情。。。' % t)
                if t == 12:
                    raise Exception(u'获取不到股东详情')
                elif t > 12:
                    self.info(u'需要检查网址。。。' )
            else:
                break
        result_text = json.loads(r.text)
        renjiao_json = result_text['rjs']
        # print type(renjiao_json), renjiao_json
        for j in renjiao_json:
            # self.json_result[family].append({})
            rjmx_dict[u'认缴出资方式']= j['conform']
            rjmx_dict[u'认缴出资额（万元）']= j['subconam']
            rjmx_dict[u'认缴出资日期']= j['condate']
            rjmx_list.append(rjmx_dict)
            value['Shareholder_Info:subscripted_method'] = j['conform']
            # print "j['conform']",type(j['conform']),  j['conform']
            if 'conform' in j:
                # if int(j['conform']) == 1 or j['conform'] == '1;2;':
                a = ['1', '2', '3', '4',  '6', '7', '9']
                b = [u"货币", u"实物", u"知识产权", u"债权", u"土地使用权", u"股权", u"其他"]
                if j['conform'] in a:
                    rjmx_dict[u'认缴出资方式'] = b[a.index(j['conform'])]
                    value['Shareholder_Info:subscripted_method'] = b[a.index(j['conform'])]
                else:
                    rjmx_dict[u'认缴出资方式']= u'货币'
                    value['Shareholder_Info:subscripted_method'] = u'货币'
            # value['Shareholder_Info:subscripted_amount'] = str(j['subconam'])+ u'万元'
            value['Shareholder_Info:subscripted_amount'] = j['subconam']
            value['Shareholder_Info:subscripted_time'] = j['condate']
            rjmx_dict = {}
        value['Shareholder_Info:rjmx'] = rjmx_list
        shijiao_json = result_text['sjs']
        for j in shijiao_json:
            # self.json_result[family].append({})
            sjmx_dict[u'认缴出资方式']= j['conform']
            sjmx_dict[u'认缴出资额（万元）']= j['acconam']
            sjmx_dict[u'认缴出资日期']= j['condate']
            sjmx_list.append(sjmx_dict)
            value['Shareholder_Info:actualpaid_method'] = j['conform']
            if 'conform' in j:
                a = ['1', '2', '3', '4',  '6', '7', '9']
                b = [u"货币", u"实物", u"知识产权", u"债权", u"土地使用权", u"股权", u"其他"]
                if j['conform'] in a:
                    sjmx_dict[u'认缴出资方式']= b[a.index(j['conform'])]
                    value['Shareholder_Info:actualpaid_method']= b[a.index(j['conform'])]
                else:
                    sjmx_dict[u'认缴出资方式']= u'货币'
                    value['Shareholder_Info:actualpaid_method'] = u'货币'
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
        self.info(u'解析变更信息...')
        family = 'Changed_Announcement'
        table_id = '05'
        self.json_result[family] = []
        content = self.detail_html.encode('utf-8').replace("\n", '').replace("\n", '')
        result_text = json.loads(content)
        result_json = result_text['bgsx']
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
            self.json_result[family][i][family + ':id'] = i+1
            # print json.dumps(self.json_result[family][i], ensure_ascii=False)

    def get_zhu_yao_ren_yuan(self):
        """
        查询主要人员信息
        :return:
        """
        self.info(u'解析主要人员信息...')
        family = 'KeyPerson_Info'
        table_id = '06'
        self.json_result[family] = []
        content = self.detail_html.encode('utf-8').replace("\n", '').replace("\n", '')
        result_text = json.loads(content)
        result_json = result_text['ryxx']
        # print 'result_json', result_json
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
            self.json_result[family][i][family + ':id'] = i+1
            # print json.dumps(self.json_result[family][i], ensure_ascii=False)

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
        r = self.post_request(url=url, data=params)
        soup = BeautifulSoup(r.text, 'lxml')
        zhuguanbumen_text = soup.text.strip()
        zhuguanbumen_text = json.loads(zhuguanbumen_text)
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

    def get_fen_zhi_ji_gou(self):
        """
        查询分支机构信息
        :return:
        """
        self.info(u'解析分支机构信息...')
        family = 'Branches'
        table_id = '08'
        self.json_result[family] = []
        content = self.detail_html.encode('utf-8').replace("\n", '').replace("\n", '')
        result_text = json.loads(content)
        result_json = result_text['fzjg']
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
            self.json_result[family][i][family + ':id'] = i+1
            # print json.dumps(self.json_result[family][i], ensure_ascii=False)

    def get_qing_suan(self):
        pass

    def get_dong_chan_di_ya(self):
        """
        查询动产抵押信息
        :return:
        """
        self.info(u'解析动产抵押信息...')
        family = 'Chattel_Mortgage'
        table_id = '11'
        self.json_result[family] = []
        content = self.detail_html.encode('utf-8').replace("\n", '').replace("\n", '')
        result_text = json.loads(content)
        result_json = result_text['dcdyDjxx']
        for j in result_json:
            self.json_result[family].append({})
            for k in j:
                if k in dong_chan_di_ya_dict:
                    col = family + ':' + dong_chan_di_ya_dict[k]
                    val = j[k]
                    self.json_result[family][-1][col] = val
                if j['priclasecam']:
                    self.json_result[family][-1]['Chattel_Mortgage:chattelmortgage_guaranteedamount'] = \
                        str(j['priclasecam']) + u'万'
                if j['type'] == str(1):
                    self.json_result[family][-1]['Chattel_Mortgage:chattelmortgage_status'] = u'有效'
                elif j['type'] == str(2):
                    self.json_result[family][-1]['Chattel_Mortgage:chattelmortgage_status'] = u'无效'
        for i in range(len(self.json_result[family])):
            self.json_result[family][i]['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.cur_zch, self.today, i+1)
            self.json_result[family][i][family + ':registrationno'] = self.cur_zch
            self.json_result[family][i][family + ':enterprisename'] = self.cur_mc
            self.json_result[family][i][family + ':id'] = i+1
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

    def get_gu_quan_chu_zhi(self):
        """
        查询股权出置信息
        :return:
        """
        self.info(u'解析股权出质信息...')
        family = 'Equity_Pledge'
        table_id = '12'
        self.json_result[family] = []
        content = self.detail_html.encode('utf-8').replace("\n", '').replace("\n", '')
        result_text = json.loads(content)
        result_json = result_text['gqczDjxx']
        for j in result_json:
            self.json_result[family].append({})
            for k in j:
                if k in gu_quan_chu_zhi_dict:
                    col = family + ':' + gu_quan_chu_zhi_dict[k]
                    val = j[k]
                    self.json_result[family][-1][col] = val
                if j['impam']:
                    self.json_result[family][-1]['Equity_Pledge:impam'] = \
                        str(j['priclasecam']) + u'万'
                if j['type'] == str(1):
                    self.json_result[family][-1]['Equity_Pledge:type'] = u'有效'
                elif j['type'] == str(2):
                    self.json_result[family][-1]['Equity_Pledge:type'] = u'无效'
        for i in range(len(self.json_result[family])):
            self.json_result[family][i]['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.cur_zch, self.today, i+1)
            self.json_result[family][i][family + ':registrationno'] = self.cur_zch
            self.json_result[family][i][family + ':enterprisename'] = self.cur_mc
            self.json_result[family][i][family + ':id'] = i+1
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

    def get_jing_ying_yi_chang(self):
        """
        :return:
        """
        self.info(u'解析经营异常信息...')
        family = 'Business_Abnormal'
        table_id = '14'
        self.json_result[family] = []
        content = self.detail_html.encode('utf-8').replace("\n", '').replace("\n", '')
        result_text = json.loads(content)
        result_json = result_text['jyyc']
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
            self.json_result[family][i][family + ':id'] = i+1
            # print json.dumps(self.json_result[family][i], ensure_ascii=False)

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

    def get_chou_cha_jian_cha(self):
        """
        查询抽查检查信息
        :return:
        """
        self.info(u'解析抽查检查信息...')
        family = 'Spot_Check'
        table_id = '16'
        self.json_result[family] = []
        content = self.detail_html.encode('utf-8').replace("\n", '').replace("\n", '')
        result_text = json.loads(content)
        result_json = result_text['ccjcxx']
        for j in result_json:
            self.json_result[family].append({})
            for k in j:
                if k in chou_cha_jian_cha_dict:
                    col = family + ':' + chou_cha_jian_cha_dict[k]
                    val = j[k]
                    self.json_result[family][-1][col] = val
                if j['instype'] == str(1):
                    self.json_result[family][-1]['Spot_Check:check_type'] = u'抽查'
                elif j['instype'] == str(2):
                    self.json_result[family][-1]['Spot_Check:check_type'] = u'检查'
        for i in range(len(self.json_result[family])):
            self.json_result[family][i]['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.cur_zch, self.today, i+1)
            self.json_result[family][i][family + ':registrationno'] = self.cur_zch
            self.json_result[family][i][family + ':enterprisename'] = self.cur_mc
            self.json_result[family][i][family + ':id'] = i+1
            # print json.dumps(self.json_result[family][i], ensure_ascii=False)

    def set_cookie(self, html_text):
        ctxt = PyV8.JSContext()
        ctxt.enter()
        soup = BeautifulSoup(html_text, 'html5lib')
        js = soup.select('script')[0].text
        js = js.replace('eval', 'return')
        js = str("(function(){%s})" % js)
        f = ctxt.eval(js)
        res = f()
        a = res.split(';')[0].split('=')[1].strip('"')
        self.session.cookies.set(name='AD_VALUE', value=a, domain='sd.gsxt.gov.cn', path='/')
        # print self.session.cookies

# if __name__ == '__main__':
#     searcher = ShanDongSearcher()
#     f = open('E:\\shandong.txt','r').readlines()
# #     # print f, len(f), f[0].strip().decode('gbk').encode('utf8')
#     for name in f:
#         word = name.strip().decode('gbk')#.encode('utf8')
#         # print 'word',word,type(word)          #.strip().decode('gbk').encode('utf8')
#         searcher.submit_search_request(word)
#         print json.dumps(searcher.json_result, ensure_ascii=False)

if __name__ == '__main__':
    args_dict = get_args()
    searcher = ShanDongSearcher()
    # searcher.delete_tag_a_from_db(u'青岛国金贵金属交易中心股份有限公司')
#     searcher.submit_search_request(u'山东远大板业科技有限公司')
#     searcher.submit_search_request(u'章丘市盛季锻造厂')
#     searcher.submit_search_request(u'南市中汉中新月鱼庄')
    searcher.submit_search_request(u'昌乐庆联后农业机械有限公司')
    # searcher.info(json.dumps(searcher.json_result, ensure_ascii=False))
    # print json.dumps(searcher.json_result, ensure_ascii=False)
