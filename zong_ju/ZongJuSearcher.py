# coding=utf-8

from gs.Searcher import Searcher
from gs import TimeUtils
from geetest_broker.GeetestBroker import GeetestBrokerRealTime
import json
import random
from bs4 import BeautifulSoup
import re
import ZongJuConfig
from gs.MyException import *
from gs.TimeUtils import get_cur_time
from geetest_broker import MySQL
import codecs
import urllib
import requests
from gs import CompareStatus
from urlparse import urlparse
from gs.SpiderMan import SpiderMan
from gs.USCC import check
# from gs import ProxyConf


class ZongJuSearcher(SpiderMan, GeetestBrokerRealTime):

    reg_code = None
    province = u'工商总局'
    tag_a = None
    ent_type = None
    bian_geng_url = None
    gu_dong_url = None
    gu_quan_chu_zhi_url = None
    dong_chan_di_ya_url = None
    jing_ying_yi_chang_url = None
    zhu_yao_ren_yuan_url = None
    xing_zheng_chu_fa_url = None
    chou_cha_jian_cha_url = None
    nian_bao_url = None
    today = None
    input_company_name = None
    has_lsmc = False
    new_flag = False
    # app_key = ProxyConf.key2
    ignore_pattern = re.compile(u'[ ~`@$%\^&*_\-—+=\[\]{}|:;"\',.<>?/，。？、：；“”‘’【】．'
                                u'《》１２３４５６７８９０ｑｗｅｒｔｙｕｉｏｐａｓｄｆｇｈｊｋｌｚｘｃｖ'
                                u'ｂｎｍＱＷＥＲＴＹＵＩＯＰＡＳＤＦＧＨＪＫＬＺＸＣＶＢＮＭ]')
    ignore_pattern2 = re.compile(u'[1234567890qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM]')

    def __init__(self, dst_topic=None):
        super(ZongJuSearcher, self).__init__(keep_session=True, dst_topic=dst_topic, max_try_times=5)
        # self.headers = {
        #     'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:45.0) Gecko/20100101 Firefox/45.0'
        # }
        self.set_geetest_config()

    def save_lsmc(self, mc, xydm, lsmc):
        sql = "replace into enterprise_credit_info.lsmc(mc,xydm,lsmc,last_update_time,add_date) " \
              "values(%s,%s,%s,now(),date(now()))"
        # print sql, (mc, xydm, lsmc)
        MySQL.execute_update(sql, (mc, xydm, lsmc))

        if self.new_flag:
            lsmc_list = lsmc\
                .replace(u'历史名称：', '')\
                .replace(u'企业基本信息：名称:', '') \
                .replace(u'企业（机构）名称:', '') \
                .replace(u'注册号:', '') \
                .replace(u'从属名称:', '') \
                .replace(u'名称:', '') \
                .split(u'；')
            for mc in lsmc_list:
                mc = mc.strip().rstrip('.')
                sql1 = u"insert into %s values('%s',-1,null,'曾用名') on duplicate key update update_status=-1" % ('law.dtjk_company_shixin', mc)
                sql2 = u"insert into %s values('%s',-1,null,'曾用名') on duplicate key update update_status=-1" % ('law.dtjk_company_beizhixing', mc)
                sql3 = u"insert into %s values('%s',-1,null,null,'曾用名') on duplicate key update update_status=-1" % ('law.dtjk_company_src', mc)
                sql4 = u"insert into %s values('%s',-1,null,date(now())) on duplicate key update update_status=-1,add_date=date(now())" % ('news.news_lsmc', mc)

                # print sql1
                # print sql2
                # print sql3
                # print sql4

                MySQL.execute_update(sql1)
                MySQL.execute_update(sql2)
                MySQL.execute_update(sql3)
                MySQL.execute_update(sql4)

    def set_geetest_config(self):
        self.geetest_product = 'popup'
        self.geetest_referer = 'http://www.gsxt.gov.cn/index.html'

    def get_gt_challenge(self):
        url_1 = "http://www.gsxt.gov.cn/SearchItemCaptcha?v=%s" % TimeUtils.get_cur_ts_mil()
        self.info(u'获取gt和challenge...')
        r_1 = self.get_request(url_1)
        json_1 = json.loads(r_1.text)
        self.gt = json_1['gt']
        self.challenge = json_1['challenge']

    def get_token(self):
        self
        return str(random.randint(50000000, 60000000))

    @staticmethod
    def send_msg(msg):
        f_out = codecs.open('zongju_test.txt', 'a', 'utf-8', 'ignore')
        f_out.writelines(msg+'\n')
        f_out.close()

    def delete_tag_a_from_db(self, keyword):
        pass

    def get_tag_a_from_page(self, keyword):
        self.has_lsmc = False

        if check(keyword):
            is_xydm = True
        else:
            is_xydm = False
        if not is_xydm and (self.ignore_pattern2.search(keyword) or self.ignore_pattern.search(keyword)):
            return None
        validate = self.get_geetest_validate()
        for i in range(5):
            url = "http://www.gsxt.gov.cn/corp-query-search-1.html"
            params = {
                'geetest_challenge': self.challenge,
                'geetest_seccode': '%s|jordan' % validate,
                'geetest_validate': '%s' % validate,
                'searchword': keyword,
                'tab': 'ent_tab',
                'token': self.get_token()
            }
            r = self.post_request(url=url, params=params)
            soup = BeautifulSoup(r.text, 'lxml')
            item_list = soup.select('a.search_list_item.db')
            if len(item_list) == 0 and not re.search(u'查询到<span class="search_result_span1">\d</span>条信息', r.text):
                self.info(u'查询异常')
                continue
            else:
                break
            # if not r.text.strip():
            #     return None
            # if len(item_list) == 0 and not re.search(u'查询到<span class="search_result_span1">\d</span>条信息', r.text):
            #     raise Exception(u'查询异常')
        best_djzt = None
        best_tag_a = None
        match_pattern = -1  # -1:初始化，0：曾用名，1：现用名
        for item_ele in item_list:
            name = item_ele.select('h1')[0].text.replace('(', u'（').replace(')', u'）')
            name = re.sub(r'\s', '', name)
            code = item_ele.select('div')[1].select('span')[0].text.strip()
            history_name_list = []
            if len(item_ele.select('div.div-info-circle3')) > 0:
                self.has_lsmc = True
                history_name = item_ele.select('div.div-info-circle3')[0].text
                history_name_list = history_name.replace(u'历史名称：', '').strip().split(u'；')
                lsmc = item_ele.select('div.div-info-circle3')[0].text.replace(u'历史名称：', '').strip()
                self.save_lsmc(name, code if check(code) else None, lsmc)
            # else:
            #     if code == xydm and name != keyword:
            #         self.has_lsmc = True
            #         self.save_lsmc(name, code if check(code) else None, keyword)
            tag_a = item_ele.attrs['href']
            djzt = item_ele.select('div.wrap-corpStatus')[0].text.strip().replace('(', u'（').replace(')', u'）')
            code_ele = item_ele.select('div.div-map2')[0]
            code_text = code_ele.text
            code_type, self.reg_code = [s.strip() for s in re.split(u'[:：]', code_text)]

            if is_xydm or keyword == name or keyword in history_name_list:
                if is_xydm or keyword == name:
                    tmp_match_pattern = 1
                else:
                    tmp_match_pattern = 0
                    self.info("insert ignore into changed_mc_src values('%s',-1,null,'%s')" % (name, self.province))
                    MySQL.execute_update("insert ignore into enterprise_credit_info.changed_mc_src values('%s',-1,null,'%s')"
                                         % (name, self.province))  # 保留到因名称变更而引起的待更新表中
                if tmp_match_pattern >= match_pattern:
                    match_pattern = tmp_match_pattern
                    if CompareStatus.compare_status(djzt, best_djzt) > 0:
                        best_djzt = djzt
                        best_tag_a = tag_a
                        self.input_company_name = name

            # self.save_tag_a_to_db(tag_a, mc, xydm)
        return best_tag_a

    def get_tag_a_from_db(self, keyword, xydm):
        return None

    def submit_search_request(self, keyword, account_id='null', task_id='null'):
        """
        :param keyword:
        :param flags: {True： 名称查询，False：信用代码查询}
        :param account_id:
        :param task_id:
        :return:
        """

        if check(keyword):
            is_xydm = True
        else:
            is_xydm = False
            keyword = self.process_mc(keyword)
        update_status = 0
        self.json_result.clear()
        # keyword = self.process_mc(keyword)
        self.json_result['accountId'] = account_id
        self.json_result['taskId'] = task_id
        self.today = TimeUtils.get_today()
        self.tag_a = self.get_tag_a_from_page(keyword)
        self.json_result['inputCompanyName'] = self.input_company_name
        # print self.tag_a
        if self.tag_a:
            if is_xydm or self.input_company_name == keyword:
                update_status = 1
            else:
                update_status = 888
            if self.get_ying_ye_zhi_zhao():
                self.get_zhu_yao_ren_yuan()
                self.get_bian_geng()
                self.get_gu_dong()
                # self.get_gu_quan_chu_zhi()
                # self.get_dong_chan_di_ya()
                # self.get_jing_ying_yi_chang()
                # self.get_chou_cha_jian_cha()
                # self.get_xing_zheng_chu_fa()
                self.send_msg_to_kafka(json.dumps(self.json_result, ensure_ascii=False))
            else:
                update_status = -1
        return update_status

    def get_ying_ye_zhi_zhao(self):

        ying_ye_zhi_zhao_url = 'http://www.gsxt.gov.cn' + self.tag_a

        r = self.get_request(ying_ye_zhi_zhao_url, allow_redirects=False,
                     headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:45.0) Gecko/20100101 Firefox/45.0'})
        # print '->', r.text
        if (r.status_code == 303 and r.headers.get('Location', '').startswith('/index')) \
                or r.status_code == 404\
                or "window.location.href = '/error.html'" in r.text:
            return None
        else:
            soup = BeautifulSoup(r.text, 'html5lib')
            if len(soup.select('input#entType')) > 0:
                self.ent_type = soup.select('input#entType')[0].attrs['value']
            else:
                self.info(u'获取ent_type失败')
                return None
        soup = BeautifulSoup(r.text, 'html5lib')
        self.ent_type = soup.select('input#entType')[0].attrs['value']
        dl_list = soup.select('div#wrap-base dl')
        ying_ye_zhi_zhao_data = {}
        yyzz_data = dict()
        for dl in dl_list:
            desc = dl.select('dt')[0].text.strip().strip(u'：:')
            val = dl.select('dd')[0].text.strip()
            if desc in ZongJuConfig.ying_ye_zhi_zhao_dict:
                col = ZongJuConfig.ying_ye_zhi_zhao_dict[desc]
                ying_ye_zhi_zhao_data[col] = val
                yyzz_data[desc] = val
            else:
                raise UnknownColumnException(mc=self.input_company_name, col=desc)
        # print json.dumps(ying_ye_zhi_zhao, ensure_ascii=False)
        family = 'Registered_Info'
        table_id = '01'
        self.json_result[family] = []
        self.json_result[family].append({})
        for k in ying_ye_zhi_zhao_data:
            col = family + ':' + k
            val = ying_ye_zhi_zhao_data[k]
            self.json_result[family][-1][col] = val
        self.json_result[family][-1]['rowkey'] = '%s_%s_%s_' % (self.input_company_name, table_id, self.reg_code)
        self.json_result[family][-1][family + ':enterprisename'] = self.input_company_name
        self.json_result[family][-1][family + ':province'] = self.province
        self.json_result[family][-1][family + ':lastupdatetime'] = get_cur_time()

        # 获取其他模块url
        if self.ent_type != '16':
            self.bian_geng_url = self.get_url('alterInfoUrl', r.text)
            self.zhu_yao_ren_yuan_url = self.get_url('keyPersonUrl', r.text)
        else:
            self.bian_geng_url = self.get_url('gtAlertInfoUrl', r.text)
            self.zhu_yao_ren_yuan_url = self.get_url('gtKeyPersonUrl', r.text)
        self.gu_dong_url = self.get_url('shareholderUrl', r.text)
        self.jing_ying_yi_chang_url = self.get_url('entBusExcepUrl', r.text)
        self.gu_quan_chu_zhi_url = self.get_url('stakQualitInfoUrl', r.text)
        self.dong_chan_di_ya_url = self.get_url('mortRegInfoUrl', r.text)
        self.xing_zheng_chu_fa_url = self.get_url('punishmentDetailInfoUrl', r.text)
        self.chou_cha_jian_cha_url = self.get_url('spotCheckInfoUrl', r.text)
        self.nian_bao_url = self.get_url('anCheYearInfo', r.text)
        return yyzz_data

    @ staticmethod
    def get_url(flag, text):
        pattern = re.compile('var ' + flag + '( )?=( )?"[^"]+"')
        res = pattern.search(text)
        if res:
            return 'http://www.gsxt.gov.cn' + res.group().split('"')[1]
        else:
            return None

    def get_bian_geng(self):
        draw = 1
        bian_geng_data = []
        while True:
            params = {
                'draw': draw,
                'length': 5,
                'start': 5*(draw-1),
            }
            r = self.post_request(self.bian_geng_url, params=params)
            json_obj = json.loads(r.text)
            data = json_obj['data']
            for item in data:
                bian_geng_data.append({})
                for k in item:
                    col = ZongJuConfig.bian_geng_dict[k]
                    val = item[k]
                    if type(val) == unicode:
                        if '<span' in val:
                            val = re.sub('<span[^<]*</span>', '', val)
                        if '<div' in val:
                            val = re.sub('<div[^<]*</div>', '', val)
                        val = re.sub(r'\s', '', val)
                    if col == 'changedannouncement_date' and val:
                        val = TimeUtils.get_date(val)
                    bian_geng_data[-1][col] = val
            if int(json_obj['draw']) < int(json_obj['totalPage']):
                draw += 1
                # self.get_bian_geng(draw + 1, bian_geng_data)
            else:
                # print json.dumps(bian_geng_data, ensure_ascii=False)
                family = 'Changed_Announcement'
                table_id = '05'
                self.json_result[family] = []
                for i in range(len(bian_geng_data)):
                    row = bian_geng_data[i]
                    self.json_result[family].append({})
                    self.json_result[family][-1]['rowkey'] = '%s_%s_%s_%s%d' % (self.input_company_name, table_id, self.reg_code, self.today, i + 1)
                    self.json_result[family][-1][family + ':registrationno'] = self.reg_code
                    self.json_result[family][-1][family + ':enterprisename'] = self.input_company_name
                    for k in row:
                        col = family + ':' + k
                        val = row[k]
                        self.json_result[family][-1][col] = val
                break

    def get_gu_dong(self):
        draw = 1
        gu_dong_data = []
        while True:
            params = {
                'draw': draw,
                'length': 5,
                'start': 5*(draw-1),
            }
            r = self.post_request(self.gu_dong_url, params=params)
            # print r.text
            json_obj = json.loads(r.text)
            data = json_obj['data']
            for item in data:
                gu_dong_data.append({})
                for k in item:
                    if k in ZongJuConfig.gu_dong_dict:
                        col = ZongJuConfig.gu_dong_dict[k]
                        val = item[k]
                        if type(val) == unicode:
                            if '<span' in val:
                                val = re.sub('<span[^<]*</span>', '', val)
                            if '<div' in val:
                                val = re.sub('<div[^<]*</div>', '', val)
                            val = re.sub(r'\s', '', val)
                        gu_dong_data[-1][col] = val
                if 'detailCheck' in item and item['detailCheck'] == 'true':
                    inv_id = item['invId']
                    detail = self.get_gu_dong_detail(inv_id)
                    gu_dong_data[-1]['sjmx'] = detail[u'实缴明细']

                    if len(detail[u'实缴明细']) > 0:
                        gu_dong_data[-1]['actualpaid_method'] = detail[u'实缴明细'][0][u'实缴出资方式']
                        gu_dong_data[-1]['actualpaid_time'] = detail[u'实缴明细'][0][u'实缴出资日期']
                        gu_dong_data[-1]['actualpaid_amount'] = detail[u'实缴明细'][0][u'实缴出资额(万元)']
                        s = 0
                        for sj in detail[u'实缴明细']:
                            try:
                                s += sj[u'实缴出资额(万元)']
                            except:
                                pass
                        gu_dong_data[-1]['actualpaid_capital'] = str(s)

                    gu_dong_data[-1]['rjmx'] = detail[u'认缴明细']
                    if len(detail[u'认缴明细']) > 0:
                        gu_dong_data[-1]['subscripted_method'] = detail[u'认缴明细'][0][u'认缴出资方式']
                        gu_dong_data[-1]['subscripted_time'] = detail[u'认缴明细'][0][u'认缴出资日期']
                        gu_dong_data[-1]['subscripted_amount'] = detail[u'认缴明细'][0][u'认缴出资额(万元)']
                        # print gu_dong_data[-1]['subscripted_capital']
                        # if not gu_dong_data[-1]['subscripted_capital']:
                        s = 0
                        for rj in detail[u'认缴明细']:
                            try:
                                s += rj[u'认缴出资额(万元)']
                            except:
                                pass
                        gu_dong_data[-1]['subscripted_capital'] = str(s)
            if int(json_obj['draw']) < int(json_obj['totalPage']):
                draw += 1
            else:
                family = 'Shareholder_Info'
                table_id = '04'
                self.json_result[family] = []
                for i in range(len(gu_dong_data)):
                    row = gu_dong_data[i]
                    self.json_result[family].append({})
                    self.json_result[family][-1]['rowkey'] = '%s_%s_%s_%s%d' % (self.input_company_name, table_id, self.reg_code, self.today, i + 1)
                    self.json_result[family][-1][family + ':registrationno'] = self.reg_code
                    self.json_result[family][-1][family + ':enterprisename'] = self.input_company_name
                    for k in row:
                        col = family + ':' + k
                        val = row[k]
                        self.json_result[family][-1][col] = val
                break

    def get_gu_dong_detail(self, inv_id):
        url = "http://www.gsxt.gov.cn/corp-query-entprise-info-shareholderDetail-%s.html" % urllib.quote(inv_id.encode('utf-8')).replace('%7C', '|')
        try:
            r = self.get_request(url)
            j = json.loads(r.text)
        except (requests.exceptions.ContentDecodingError, ValueError):
            return {u'认缴明细': [], u'实缴明细': []}
        rjmx = []
        sjmx = []
        if 'data' in j:
            sj_data = j['data'][0]
            rj_data = j['data'][1]
            for sj in sj_data:
                sje = sj['acConAm']
                sjczfs = sj['conForm_CN']
                sjczrq = TimeUtils.get_date(sj['conDate'])
                sjmx.append({u'实缴出资方式': sjczfs, u'实缴出资额(万元)': sje, u'实缴出资日期': sjczrq})
            for rj in rj_data:
                rje = rj['subConAm']
                rjczfs = rj['conForm_CN']
                rjczrq = TimeUtils.get_date(rj['conDate'])
                rjmx.append({u'认缴出资方式': rjczfs, u'认缴出资额(万元)': rje, u'认缴出资日期': rjczrq})
        return {u'认缴明细': rjmx, u'实缴明细': sjmx}

    def get_gu_quan_chu_zhi(self):
        draw = 1
        gu_quan_chu_zhi_data = []
        while True:
            params = {
                'draw': draw,
                'length': 5,
                'start': 5 * (draw - 1),
            }
            r = self.post_request(self.gu_quan_chu_zhi_url, params=params)
            json_obj = json.loads(r.text)
            data = json_obj['data']
            for item in data:
                gu_quan_chu_zhi_data.append({})
                for k in item:
                    if k in ZongJuConfig.gu_quan_chu_zhi_dict:
                        col = ZongJuConfig.gu_quan_chu_zhi_dict[k]
                        val = item[k]
                        if type(val) == unicode:
                            if '<span' in val:
                                val = re.sub('<span[^<]*</span>', '', val)
                            if '<div' in val:
                                val = re.sub('<div[^<]*</div>', '', val)
                            val = re.sub(r'\s', '', val)
                        if col == 'equitypledge_status':
                            if str(val) == '1':
                                val = u'有效'
                            else:
                                val = u'无效'
                        elif col == 'equitypledge_amount' and val:
                            if item['pledAmUnit']:
                                val = str(val) + re.sub(r'\s', '', item['pledAmUnit'])
                            else:
                                val = str(val) + u'万元'
                        elif col == 'equitypledge_registrationdate' and val:
                            val = TimeUtils.get_date(val)
                        gu_quan_chu_zhi_data[-1][col] = val
            if int(json_obj['draw']) < int(json_obj['totalPage']):
                draw += 1
                # self.get_gu_quan_chu_zhi(draw + 1, gu_quan_chu_zhi_data)
            else:
                # print json.dumps(gu_quan_chu_zhi_data, ensure_ascii=False)
                family = 'Equity_Pledge'
                table_id = '12'
                self.json_result[family] = []
                for i in range(len(gu_quan_chu_zhi_data)):
                    row = gu_quan_chu_zhi_data[i]
                    self.json_result[family].append({})
                    self.json_result[family][-1]['rowkey'] = '%s_%s_%s_%s%d' % (self.input_company_name, table_id, self.reg_code, self.today, i + 1)
                    self.json_result[family][-1][family + ':registrationno'] = self.reg_code
                    self.json_result[family][-1][family + ':enterprisename'] = self.input_company_name
                    for k in row:
                        col = family + ':' + k
                        val = row[k]
                        self.json_result[family][-1][col] = val
                break

    def get_dong_chan_di_ya(self):
        draw = 1
        dong_chan_di_ya_data = []
        while True:
            params = {
                'draw': draw,
                'length': 5,
                'start': 5 * (draw - 1),
            }
            r = self.post_request(self.dong_chan_di_ya_url, params=params)
            json_obj = json.loads(r.text)
            data = json_obj['data']
            for item in data:
                dong_chan_di_ya_data.append({})
                for k in item:
                    if k in ZongJuConfig.dong_chan_di_ya_dict:
                        col = ZongJuConfig.dong_chan_di_ya_dict[k]
                        val = item[k]
                        if type(val) == unicode:
                            if '<span' in val:
                                val = re.sub('<span[^<]*</span>', '', val)
                            if '<div' in val:
                                val = re.sub('<div[^<]*</div>', '', val)
                            val = re.sub(r'\s', '', val)
                        if col == 'chattelmortgage_status':
                            if str(val) == '1':
                                val = u'有效'
                            else:
                                val = u'无效'
                        elif col == 'chattelmortgage_guaranteedamount':
                            val = str(val) + re.sub(r'\s', '', item['regCapCur_Cn'])
                        elif col == 'chattelmortgage_registrationdate' and val:
                            val = TimeUtils.get_date(val)
                        dong_chan_di_ya_data[-1][col] = val
            if int(json_obj['draw']) < int(json_obj['totalPage']):
                draw += 1
                # self.get_gu_quan_chu_zhi(draw + 1, dong_chan_di_ya_data)
            else:
                # print json.dumps(dong_chan_di_ya_data, ensure_ascii=False)
                family = 'Chattel_Mortgage'
                table_id = '11'
                self.json_result[family] = []
                for i in range(len(dong_chan_di_ya_data)):
                    row = dong_chan_di_ya_data[i]
                    self.json_result[family].append({})
                    self.json_result[family][-1]['rowkey'] = '%s_%s_%s_%s%d' % (self.input_company_name, table_id, self.reg_code, self.today, i + 1)
                    self.json_result[family][-1][family + ':registrationno'] = self.reg_code
                    self.json_result[family][-1][family + ':enterprisename'] = self.input_company_name
                    for k in row:
                        col = family + ':' + k
                        val = row[k]
                        self.json_result[family][-1][col] = val
                break

    def get_dong_chan_di_ya_detail(self, dy_id, output_data):
        # 抵押权人信息
        dyqrxx_url = 'http://www.gsxt.gov.cn/corp-query-entprise-info-mortregpersoninfo-%s.html' % dy_id
        dyqrxx_res = self.get_request(dyqrxx_url)
        dyqrxx_data = json.loads(dyqrxx_res.text)['data']
        dyqrxx_dict = {
            'bLicType_CN': 'dyqr_zzlx',  # 抵押权人证照类型
            'more': 'dyqr_mc',  # 抵押权人名称
            'bLicNo': 'dyqr_zzhm',  # 证照号码
            # '': '',  # 住所地
        }
        # 被担保主债权信息
        bdbzzqxx_url = 'http://www.gsxt.gov.cn/corp-query-entprise-info-mortCreditorRightInfo-%s.html' % dy_id
        bdbzzqxx_res = self.get_request(bdbzzqxx_url)
        bdbzzqxx_data = json.loads(bdbzzqxx_res.text)['data']
        bdbzzqxx_dict = {
            'priClaSecKind_CN': 'dbzq_zl',  # 种类
            'priClaSecAm': 'dbzq_sl',  # 数额
            'warCov': 'dbzq_fw',  # 担保的范围
            'remark': 'dbzq_bz',  # 备注
        }
        # 抵押物信息
        dywxx_url = 'http://www.gsxt.gov.cn/corp-query-entprise-info-mortGuaranteeInfo-%s.html' % dy_id
        dywxx_res = self.get_request(dywxx_url)
        dywxx_data = json.loads(dywxx_res.text)['data']
        dywxx_dict = {
            'guaDes': 'dyw_xq',  # 数量、质量、状况、所在地等情况
            'own': 'dyw_gs',  # 所有权或使用权归属
            'guaName': 'dyw_mc',  # 抵押物名称
        }
        for d in dyqrxx_data:
            for k in d:
                if k in dyqrxx_dict:
                    col = dyqrxx_dict[k]
                    val = d[k]
                    output_data[col] = val
        for d in bdbzzqxx_data:
            for k in d:
                if k in bdbzzqxx_dict:
                    col = bdbzzqxx_dict[k]
                    val = d[k]
                    # if col == 'pefPerForm' or col == 'pefPerTo' and val:
                    #     val = TimeUtils.get_date(val)
                    if col == 'priClaSecAm':
                        val = val + bdbzzqxx_data['regCapCur_CN']
                    output_data[col] = val
            output_data['dbzq_qx'] = TimeUtils.get_date(d['pefPerForm'])+u'至'+TimeUtils.get_date(d['pefPerTo'])
            # val = TimeUtils.get_date(val)
        for d in dywxx_data:
            for k in d:
                if k in dywxx_dict:
                    col = dywxx_dict[k]
                    val = d[k]
                    output_data[col] = val
        # print json.dumps(output_data, ensure_ascii=False)

    def get_zhu_yao_ren_yuan(self):
        if not self.zhu_yao_ren_yuan_url:
            return
        start = -1
        page = 1
        zhu_yao_ren_yuan_data = []
        while True:
            if start == -1:
                url = self.zhu_yao_ren_yuan_url
            else:
                url = '%s?start=%d' % (self.zhu_yao_ren_yuan_url, start)

            res = self.get_request(url)
            data = json.loads(res.text)['data']
            for person in data:
                name = person['name']
                position = ''
                if '<span' in name:
                    name = re.sub('<span[^<]*</span>', '', name)
                if '<div' in name:
                    name = re.sub('<div[^<]*</div>', '', name)
                # print person['position_CN']
                if 'position_CN' in person:
                    if person['position_CN'].startswith('<img src='):
                        position = person['position_CN'].split('"')[1].replace('\n', '')
                        position = ZongJuConfig.key_person_role_dict[position]
                    else:
                        position = person['position_CN'].strip()
                zhu_yao_ren_yuan_data.append({'keyperson_name': name, 'keyperson_position': position})
            # print json.dumps(zhu_yao_ren_yuan_data, ensure_ascii=False)

            total_page = int(json.loads(res.text)['totalPage'])
            # print page, total_page
            if page < total_page:
                start = json.loads(res.text)['start'] + json.loads(res.text)['perPage']
                page += 1
            else:
                family = 'KeyPerson_Info'
                table_id = '06'
                self.json_result[family] = []
                for i in range(len(zhu_yao_ren_yuan_data)):
                    row = zhu_yao_ren_yuan_data[i]
                    self.json_result[family].append({})
                    self.json_result[family][-1]['rowkey'] = '%s_%s_%s_%s%d' % (self.input_company_name, table_id, self.reg_code, self.today, i + 1)
                    self.json_result[family][-1][family + ':registrationno'] = self.reg_code
                    self.json_result[family][-1][family + ':enterprisename'] = self.input_company_name
                    for k in row:
                        col = family + ':' + k
                        val = row[k]
                        self.json_result[family][-1][col] = val
                break

    def get_jing_ying_yi_chang(self):
        draw = 1
        jing_ying_yi_chang_data = []
        while True:
            params = {
                'draw': draw,
                'length': 5,
                'start': 5 * (draw - 1),
            }
            r = self.post_request(self.jing_ying_yi_chang_url, params=params)
            json_obj = json.loads(r.text)
            data = json_obj['data']
            for item in data:
                jing_ying_yi_chang_data.append({})
                for k in item:
                    if k in ZongJuConfig.jing_ying_yi_chang_dict:
                        col = ZongJuConfig.jing_ying_yi_chang_dict[k]
                        val = item[k]
                        if type(val) == unicode:
                            if '<span' in val:
                                val = re.sub('<span[^<]*</span>', '', val)
                            if '<div' in val:
                                val = re.sub('<div[^<]*</div>', '', val)
                            val = re.sub(r'\s', '', val)
                        if col == 'abnormal_datesin' or col == 'abnormal_datesout' and val:
                            val = TimeUtils.get_date(val)
                        jing_ying_yi_chang_data[-1][col] = val
            if int(json_obj['draw']) < int(json_obj['totalPage']):
                draw += 1
                # self.get_jing_ying_yi_chang(draw + 1, jing_ying_yi_chang_data)
            else:
                # print json.dumps(jing_ying_yi_chang_data, ensure_ascii=False)
                family = 'Business_Abnormal'
                table_id = '14'
                self.json_result[family] = []
                for i in range(len(jing_ying_yi_chang_data)):
                    row = jing_ying_yi_chang_data[i]
                    self.json_result[family].append({})
                    self.json_result[family][-1]['rowkey'] = '%s_%s_%s_%s%d' % (self.input_company_name, table_id, self.reg_code, self.today, i + 1)
                    self.json_result[family][-1][family + ':registrationno'] = self.reg_code
                    self.json_result[family][-1][family + ':enterprisename'] = self.input_company_name
                    for k in row:
                        col = family + ':' + k
                        val = row[k]
                        self.json_result[family][-1][col] = val
                break

    def get_xing_zheng_chu_fa(self):
        draw = 1
        xing_zheng_chu_fa_data = []
        while True:
            params = {
                'draw': draw,
                'length': 5,
                'start': 5 * (draw - 1),
            }
            r = self.post_request(self.xing_zheng_chu_fa_url, params=params)
            json_obj = json.loads(r.text)
            data = json_obj['data']
            for item in data:
                if not item['illegActType'] and not item['penAuth_CN'] \
                        and not item['penContent'] and not item['penDecIssDate'] \
                        and not item['penDecNo']:
                    continue
                xing_zheng_chu_fa_data.append({})
                for k in item:
                    if k in ZongJuConfig.xing_zheng_chu_fa_dict:
                        col = ZongJuConfig.xing_zheng_chu_fa_dict[k]
                        val = item[k]
                        if type(val) == unicode:
                            if '<span' in val:
                                val = re.sub('<span[^<]*</span>', '', val)
                            if '<div' in val:
                                val = re.sub('<div[^<]*</div>', '', val)
                            val = re.sub(r'\s', '', val)
                        if col in ('penalty_decisiondate', 'penalty_announcedate') and val:
                            val = TimeUtils.get_date(val)
                        xing_zheng_chu_fa_data[-1][col] = val
                if item['vPunishmentDecision'] and item['vPunishmentDecision']['fileName'].endswith('.pdf'):
                    detail_url = 'http://www.gsxt.gov.cn/doc/%s/casefiles/%s' % (item['nodeNum'], item['vPunishmentDecision']['fileName'])
                    xing_zheng_chu_fa_data[-1]['penalty_details'] = detail_url
            if int(json_obj['draw']) < int(json_obj['totalPage']):
                # self.get_xing_zheng_chu_fa(draw + 1, xing_zheng_chu_fa_data)
                draw += 1
            else:
                # print json.dumps(xing_zheng_chu_fa_data, ensure_ascii=False)
                family = 'Administrative_Penalty'
                table_id = '13'
                self.json_result[family] = []
                for i in range(len(xing_zheng_chu_fa_data)):
                    row = xing_zheng_chu_fa_data[i]
                    self.json_result[family].append({})
                    self.json_result[family][-1]['rowkey'] = '%s_%s_%s_%s%d' % (self.input_company_name, table_id, self.reg_code, self.today, i + 1)
                    self.json_result[family][-1][family + ':registrationno'] = self.reg_code
                    self.json_result[family][-1][family + ':enterprisename'] = self.input_company_name
                    for k in row:
                        col = family + ':' + k
                        val = row[k]
                        self.json_result[family][-1][col] = val
                break

    def get_chou_cha_jian_cha(self):
        draw = 1
        chou_cha_jian_cha_data = []
        while True:
            params = {
                'draw': draw,
                'length': 5,
                'start': 5 * (draw - 1),
            }
            r = self.post_request(self.chou_cha_jian_cha_url, params=params)
            json_obj = json.loads(r.text)
            data = json_obj['data']
            for item in data:
                chou_cha_jian_cha_data.append({})
                for k in item:
                    if k in ZongJuConfig.chou_cha_jian_cha_dict:
                        col = ZongJuConfig.chou_cha_jian_cha_dict[k]
                        val = item[k]
                        if type(val) == unicode:
                            if '<span' in val:
                                val = re.sub('<span[^<]*</span>', '', val)
                            if '<div' in val:
                                val = re.sub('<div[^<]*</div>', '', val)
                            val = re.sub(r'\s', '', val)
                        if col == 'check_type':
                            if str(val) == '1':
                                val = u'抽查'
                            elif str(val) == '2':
                                val = u'检查'
                        elif col == 'check_date' and val:
                            val = TimeUtils.get_date(val)
                        chou_cha_jian_cha_data[-1][col] = val
            if int(json_obj['draw']) < int(json_obj['totalPage']):
                draw += 1
                # self.get_chou_cha_jian_cha(draw + 1, chou_cha_jian_cha_data)
            else:
                # print json.dumps(chou_cha_jian_cha_data, ensure_ascii=False)
                family = 'Spot_Check'
                table_id = '16'
                self.json_result[family] = []
                for i in range(len(chou_cha_jian_cha_data)):
                    row = chou_cha_jian_cha_data[i]
                    self.json_result[family].append({})
                    self.json_result[family][-1]['rowkey'] = '%s_%s_%s_%s%d' % (self.input_company_name, table_id, self.reg_code, self.today, i + 1)
                    self.json_result[family][-1][family + ':registrationno'] = self.reg_code
                    self.json_result[family][-1][family + ':enterprisename'] = self.input_company_name
                    for k in row:
                        col = family + ':' + k
                        val = row[k]
                        self.json_result[family][-1][col] = val
                break

    def get_request(self, url, **kwargs):
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
            kwargs['headers']['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:45.0) Gecko/20100101 Firefox/45.0'
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
            kwargs['headers']['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:45.0) Gecko/20100101 Firefox/45.0'
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

if __name__ == '__main__':
    # test()
    searcher = ZongJuSearcher('GsCrawlerOnline')
    # for i in range(10):
    #     print searcher.load_nian_bao_msg(mc=u'晋江市陈埭统一化工贸易有限公司', xydm="")
    # print searcher.get_tag_a_from_page(u'北京京寿堂医院管理有限公司', u'91110105580808881C')
    # print json.dumps(searcher.get_gu_dong_detail('PROVINCENODENUM31000052270439'), ensure_ascii=False)
    # searcher.get_dong_chan_di_ya_detail('PROVINCENODENUM130000a0a0e3984ee39312014f6e223a051bc3', {})
    searcher.submit_search_request(keyword=u'91230800606542285D')

