# coding=utf-8
import PackageTool
import sys
from gs.Searcher import Searcher
from gs import TimeUtils
import json
from geetest_broker.GeetestBroker import GeetestBrokerOffline
from bs4 import BeautifulSoup
from gs.TimeUtils import get_cur_time
import GuangDongConfig
import re
import requests
from gs.USCC import check
from gs import CompareStatus
from gs.SpiderMan import SpiderMan


requests.packages.urllib3.disable_warnings()


class GuangDongSearcher(SpiderMan, GeetestBrokerOffline):

    xydm = None
    zch = None
    province = u'广东省'
    soup = None
    reg_code = None
    tag_a = None
    timeout = 120

    ent_no = None
    ent_type = None
    reg_org = None
    host = None
    input_company_name = None
    today = None

    __VIEWSTATEGENERATOR = None
    txtrid = None

    def __init__(self, dst_topic=None):
        super(GuangDongSearcher, self).__init__(keep_ip=False, keep_session=True, dst_topic=dst_topic)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:45.0) Gecko/20100101 Firefox/45.0',
        }

    def get_gt_challenge(self):
        url_1 = 'http://gd.gsxt.gov.cn/aiccips//verify/start.html?t=%s' % TimeUtils.get_cur_ts_mil()
        r_1 = self.get_request(url_1)
        self.challenge = str(json.loads(r_1.text)['challenge'])

    def get_tag_a_from_page(self, keyword):
        # keyword = keyword.replace('(', u'（').replace(')', u'）').replace(' ', '')
        if check(keyword):
            is_xydm = True
        else:
            is_xydm = False
        validate = self.get_geetest_validate()
        print 'validate', validate
        url_1 = "http://gd.gsxt.gov.cn/aiccips/verify/sec.html"
        params_1 = {
            'textfield': keyword,
            'geetest_challenge': self.challenge,
            'geetest_validate': validate,
            'geetest_seccode': '%s|jordan' % validate
        }
        r_1 = self.post_request(url=url_1, params=params_1)
        textfield = json.loads(r_1.text)['textfield']
        # print r_1.text
        url_2 = "http://gd.gsxt.gov.cn/aiccips/CheckEntContext/showCheck.html"
        params_2 = {
            'textfield': textfield,
            'type': 'nomal',
        }
        # print params_2
        r_2 = self.post_request(url_2, params=params_2)
        soup = BeautifulSoup(r_2.text, 'lxml')
        result_list = soup.select('div[onclick=details(this)]')
        item_num = 0

        latest_clrq = ''
        best_djzt = None
        best_link = None
        for item in result_list:
            item_num += 1
            item_mc = item.select('span.rsfont')[0].text.strip().replace('(', u'（').replace(')', u'）').replace(' ', '')
            djzt = item.select('span > span')[1].text.strip().replace('(', u'（').replace(')', u'）')
            item_link = item.select('a')[0].attrs['href'].strip()
            if 'szcredit' in item_link:
                area = u'深圳'
            elif 'gzaic' in item_link:
                area = u'广州'
            else:
                area = u'其他'
                item_link = item_link.replace('..', 'http://gd.gsxt.gov.cn')
            if is_xydm or item_mc == keyword:
                self.cur_mc = item_mc
                # print djzt, best_djzt, CompareStatus.compare_status(djzt, best_djzt)
                if CompareStatus.compare_status(djzt, best_djzt) >= 0:
                    best_djzt = djzt
                # if clrq > latest_clrq:
                #     latest_clrq = clrq
                    best_link = item_link
                # return item_link
        if item_num == 0 and u'暂无数据' not in r_2.text:
            self.info(u'异常页面')
            # print r_2.text
            raise Exception(u'异常页面')
        return best_link

    def get_ying_ye_zhi_zhao_sz(self):
        self.reg_code = u''
        ying_ye_zhi_zhao_data = {}
        li_list = self.soup.select('div#yyzz li')
        for li_ele in li_list:

            desc = li_ele.select('span')[0].text.strip()
            val = li_ele.select('span')[1].text.strip()
            if desc in (u'注册号/统一社会信用代码', u'统一社会信用代码/注册号', u'注册号', u'统一社会信用代码') and len(val) == 18:
                ying_ye_zhi_zhao_data[u'统一社会信用代码'] = val
                self.reg_code = val
            elif desc in (u'注册号/统一社会信用代码', u'统一社会信用代码/注册号', u'注册号', u'统一社会信用代码') and len(val) != 18:
                ying_ye_zhi_zhao_data[u'注册号'] = val
                self.reg_code = val
            ying_ye_zhi_zhao_data[desc] = val
            # print desc, val
        # print self.soup

        if u'名称' in ying_ye_zhi_zhao_data:
            self.cur_mc = self.process_mc(ying_ye_zhi_zhao_data[u'名称'])
        else:
            self.cur_mc = self.process_mc(ying_ye_zhi_zhao_data[u'企业名称'])
        if self.cur_mc != self.input_company_name:
            raise Exception(u'获取详情失败')
        self.cur_mc = self.cur_mc.replace('(', u'（').replace(')', u'）')
        ying_ye_zhi_zhao_data[u'省份'] = self.province

        family = 'Registered_Info'
        table_id = '01'
        self.json_result[family] = []
        self.json_result[family].append({})
        for k in ying_ye_zhi_zhao_data:
            col = family + ':' + GuangDongConfig.ying_ye_zhi_zhao_dict[k]
            val = ying_ye_zhi_zhao_data[k]
            self.json_result[family][-1][col] = val
        self.json_result[family][-1]['rowkey'] = '%s_%s_%s_' % (self.cur_mc, table_id, self.reg_code)
        # self.json_result[family][-1][family + ':registrationno'] = self.cur_zch
        self.json_result[family][-1][family + ':enterprisename'] = self.cur_mc
        # self.json_result[family][-1][family + ':province'] = self.province
        self.json_result[family][-1][family + ':lastupdatetime'] = get_cur_time()

    def get_ying_ye_zhi_zhao(self):
        self.reg_code = u''
        ying_ye_zhi_zhao_data = {}
        table_ele = self.soup.select('div.infoStyle table')[0]
        td_list = table_ele.select('td')
        for td_ele in td_list:
            span_list = td_ele.select('span')
            if len(span_list) == 3:
                desc = re.sub(u'[\s：]', '', td_ele.select('span')[1].text)
                val = re.sub('\\s', '', td_ele.select('span')[2].text)
                # print desc, val
                if desc in (u'注册号/统一社会信用代码', u'统一社会信用代码/注册号', u'注册号', u'统一社会信用代码') and len(val) == 18:
                    ying_ye_zhi_zhao_data[u'统一社会信用代码'] = val
                    self.reg_code = val
                elif desc in (u'注册号/统一社会信用代码', u'统一社会信用代码/注册号', u'注册号', u'统一社会信用代码') and len(val) != 18:
                    ying_ye_zhi_zhao_data[u'注册号'] = val
                    self.reg_code = val
                ying_ye_zhi_zhao_data[desc] = val

        ying_ye_zhi_zhao_data[u'省份'] = self.province

        if u'名称' in ying_ye_zhi_zhao_data:
            self.cur_mc = self.process_mc(ying_ye_zhi_zhao_data[u'名称'])
        else:
            self.cur_mc = self.process_mc(ying_ye_zhi_zhao_data[u'企业名称'])
        # if self.cur_mc != self.input_company_name:
        #     raise Exception(u'获取详情失败')

        self.cur_mc = self.cur_mc.replace('(', u'（').replace(')', u'）')
        family = 'Registered_Info'
        table_id = '01'
        self.json_result[family] = []
        self.json_result[family].append({})
        for k in ying_ye_zhi_zhao_data:
            col = family + ':' + GuangDongConfig.ying_ye_zhi_zhao_dict[k]
            val = ying_ye_zhi_zhao_data[k]
            self.json_result[family][-1][col] = val
        self.json_result[family][-1]['rowkey'] = '%s_%s_%s_' % (self.cur_mc, table_id, self.reg_code)
        # self.json_result[family][-1][family + ':registrationno'] = self.cur_zch
        self.json_result[family][-1][family + ':enterprisename'] = self.cur_mc
        # self.json_result[family][-1][family + ':province'] = self.province
        self.json_result[family][-1][family + ':lastupdatetime'] = get_cur_time()

        self.ent_no = self.soup.select('input#entNo')[0].attrs['value']
        self.ent_type = self.soup.select('input#entType')[0].attrs['value']
        self.reg_org = self.soup.select('input#regOrg')[0].attrs['value']

    def get_bian_geng(self):
        bian_geng_data = []
        url = "http://%s/aiccips//EntChaInfo/EntChatInfoList?pageNo=1&entNo=%s&regOrg=%s" % (self.host, self.ent_no, self.reg_org)
        r = self.get_request(url)
        result_data = json.loads(r.text)
        # print r.text
        if result_data['list']['totalRecords'] > 0 and result_data['list']['list']:
            for row in result_data['list']['list']:
                bian_geng_data.append({})
                bian_geng_data[-1][u'变更事项'] = row['altFiledName']
                bian_geng_data[-1][u'变更前内容'] = row['altBe']
                bian_geng_data[-1][u'变更后内容'] = row['altAf']
                bian_geng_data[-1][u'变更日期'] = TimeUtils.get_date(row['altDate'])

        family = 'Changed_Announcement'
        table_id = '05'
        # print json.dumps(bian_geng_data, ensure_ascii=False)
        self.json_result[family] = []
        for i in range(len(bian_geng_data)):
            row = bian_geng_data[i]
            self.json_result[family].append({})
            self.json_result[family][-1]['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.reg_code, self.today, i + 1)
            self.json_result[family][-1][family + ':registrationno'] = self.reg_code
            self.json_result[family][-1][family + ':enterprisename'] = self.cur_mc
            for k in row:
                col = family + ':' + GuangDongConfig.bian_geng_dict[k]
                val = row[k]
                self.json_result[family][-1][col] = val

    def get_gu_dong(self):
        gu_dong_data = []
        url = 'http://%s/aiccips//invInfo/invInfoList?pageNo=1&entNo=%s&regOrg=%s' % (self.host, self.ent_no, self.reg_org)
        r = self.get_request(url)
        result_data = json.loads(r.text)

        if result_data['list']['totalRecords'] > 0 and result_data['list']['list']:
            for row in result_data['list']['list']:
                gu_dong_data.append({})
                gu_dong_data[-1][u'股东名称'] = row['inv']
                gu_dong_data[-1][u'股东类型'] = row['invType']
                gu_dong_data[-1][u'证照/证件类型'] = row['certName']
                gu_dong_data[-1][u'证照/证件号码'] = row['certNo']
                # gu_dong_data[-1][u'认缴出资额'] = row['subConAm']
                # gu_dong_data[-1][u'实缴出资额'] = row['acConAm']
                # if self.host == 'gd.gsxt.gov.cn':
                inv_no = row['invNo']
                gd_detail = self.get_gu_dong_detail(inv_no)
                gu_dong_data[-1].update(gd_detail)

        family = 'Shareholder_Info'
        table_id = '04'
        # print json.dumps(gu_dong_data, ensure_ascii=False)
        self.json_result[family] = []
        for i in range(len(gu_dong_data)):
            row = gu_dong_data[i]
            self.json_result[family].append({})
            self.json_result[family][-1]['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.reg_code, self.today, i + 1)
            self.json_result[family][-1][family + ':registrationno'] = self.reg_code
            self.json_result[family][-1][family + ':enterprisename'] = self.cur_mc
            for k in row:
                col = family + ':' + GuangDongConfig.gu_dong_dict[k]
                val = row[k]
                self.json_result[family][-1][col] = val

    def get_gu_dong_detail(self, inv_no):
        url = "http://%s/aiccips/GSpublicity/invInfoDetails.html?invNo=%s&entNo=%s&regOrg=%s" % (self.host, inv_no, self.ent_no, self.reg_org)
        r = self.get_request(url=url)
        soup = BeautifulSoup(r.text, 'lxml')

        table_list = soup.select('table')

        tr_list = table_list[1].select('tr')
        rje = tr_list[1].select('td')[1].text.strip()
        sje = tr_list[2].select('td')[1].text.strip()

        rjczfs_mx = None
        rjcze_mx = None
        rjczrq_mx = None

        sjczfs_mx = None
        sjcze_mx = None
        sjczrq_mx = None

        rjmx_list = table_list[3].select('tr')

        rjmx = []
        sjmx = []

        for rjmx_ele in rjmx_list[1:]:
            td_list = rjmx_ele.select('td')
            rjczfs = td_list[0].text.strip()
            rjcze = td_list[1].text.strip()
            rjczrq = td_list[2].text.strip()
            if len(rjmx) == 0:
                rjczfs_mx = rjczfs
                rjcze_mx = rjcze
                rjczrq_mx = rjczrq
            rjmx.append({u'认缴出资方式': rjczfs, u'认缴出资额(万元)': rjcze, u'认缴出资日期': rjczrq})

        sjmx_list = table_list[5].select('tr')
        for sjmx_ele in sjmx_list[1:]:
            td_list = sjmx_ele.select('td')
            sjczfs = td_list[0].text.strip()
            sjcze = td_list[1].text.strip()
            sjczrq = td_list[2].text.strip()
            if len(sjmx) == 0:
                sjczfs_mx = sjczfs
                sjcze_mx = sjcze
                sjczrq_mx = sjczrq
            sjmx.append({u'实缴出资方式': sjczfs, u'实缴出资额(万元)': sjcze, u'实缴出资日期': sjczrq})
        return {
            u'认缴出资额': rje,
            u'实缴出资额': sje,
            u'认缴明细': rjmx,
            u'实缴明细': sjmx,
            u'认缴出资方式': rjczfs_mx,
            u'认缴出资额(万元)': rjcze_mx,
            u'认缴出资日期': rjczrq_mx,
            u'实缴出资方式': sjczfs_mx,
            u'实缴出资额(万元)': sjcze_mx,
            u'实缴出资日期': sjczrq_mx
        }

    def get_zhu_yao_ren_yuan(self):
        zhu_yao_ren_yuan_data = []
        name_list = self.soup.select('span.nameText')
        position_list = self.soup.select('span.positionText')
        for i in range(len(name_list)):
            xm = name_list[i].text
            if len(position_list) > 0:
                zw = position_list[i].text
            else:
                zw = ''
            zhu_yao_ren_yuan_data.append({'keyperson_name': xm, 'keyperson_position': zw})
        family = 'KeyPerson_Info'
        table_id = '06'
        self.json_result[family] = []
        for i in range(len(zhu_yao_ren_yuan_data)):
            row = zhu_yao_ren_yuan_data[i]
            self.json_result[family].append({})
            self.json_result[family][-1]['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.reg_code, self.today, i + 1)
            self.json_result[family][-1][family + ':registrationno'] = self.reg_code
            self.json_result[family][-1][family + ':enterprisename'] = self.cur_mc
            for k in row:
                col = family + ':' + k
                val = row[k]
                self.json_result[family][-1][col] = val

    def get_fen_zhi_ji_gou(self):
        '''
        公示平台数据缺失
        :return:
        '''
        pass

    def get_qing_suan(self):
        if not self.soup.find(text=u'清算组成员'):
            return
        qsxx = self.soup.find(text=u'清算组成员').parent.parent.parent
        qszfzr = qsxx.select('tr.tablebodytext td')[1].text.strip()
        if qszfzr == u'暂无数据':
            qszfzr = None
        qszcy = qsxx.select('tr.tablebodytext td')[3].text.strip()
        if qszfzr or qszcy:
            qing_suan_data = [{u'清算组负责人': qszfzr, u'清算组成员': qszcy}]
            family = 'liquidation_Information'
            table_id = '09'
            self.json_result[family] = []
            for i in range(len(qing_suan_data)):
                row = qing_suan_data[i]
                self.json_result[family].append({})
                self.json_result[family][-1]['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.reg_code, self.today, i + 1)
                self.json_result[family][-1][family + ':registrationno'] = self.reg_code
                self.json_result[family][-1][family + ':enterprisename'] = self.cur_mc
                for k in row:
                    col = family + ':' + GuangDongConfig.qing_suan_dict[k]
                    val = row[k]
                    self.json_result[family][-1][col] = val

    def get_xing_zheng_chu_fa(self):
        url = "http://%s/aiccips/OtherPublicity/environmentalProtection.html?requestType=tw" % self.host
        params = {
            'entNo': self.ent_no,
            'entType': self.ent_type,
            'regOrg': self.reg_org
        }
        r = self.post_request(url=url, data=params)
        soup = BeautifulSoup(r.text, 'lxml')
        th_list = soup.select('table#twPaginTable tr.trTitleText td')
        tr_list = soup.select('table#twPaginTable tr.tablebodytext')
        desc_list = [th_ele.text.strip() for th_ele in th_list]
        xing_zheng_chu_fa_data = []
        for tr_ele in tr_list:
            if tr_ele.text.strip() in (u'暂无相关信息', u'暂无数据'):
                continue
            xing_zheng_chu_fa_data.append({})
            td_list = tr_ele.select('td')
            for i in range(len(desc_list)):
                desc = desc_list[i]
                if desc in (u'序号', u'详情'):
                    continue
                # col = GuangDongConfig.bian_geng_dict[desc]
                val = td_list[i].text.strip()
                xing_zheng_chu_fa_data[-1][desc] = val
                # print desc, val

        family = 'Administrative_Penalty'
        table_id = '13'
        self.json_result[family] = []
        for i in range(len(xing_zheng_chu_fa_data)):
            row = xing_zheng_chu_fa_data[i]
            self.json_result[family].append({})
            self.json_result[family][-1]['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.reg_code, self.today, i + 1)
            self.json_result[family][-1][family + ':registrationno'] = self.reg_code
            self.json_result[family][-1][family + ':enterprisename'] = self.cur_mc
            for k in row:
                col = family + ':' + GuangDongConfig.xing_zheng_chu_fa_dict[k]
                val = row[k]
                self.json_result[family][-1][col] = val
                # print col, val

    def get_dong_chan_di_ya(self):
        dong_chan_di_ya_data = []
        url = "http://%s/aiccips//PleInfo/PleInfoList?pageNo=1&entNo=%s&regOrg=%s" % (self.host, self.ent_no, self.reg_org)
        r = self.get_request(url)
        result_data = json.loads(r.text)

        if result_data['list']['totalRecords'] > 0:
            for row in result_data['list']['list'] and result_data['list']['list']:
                dong_chan_di_ya_data.append({})
                dong_chan_di_ya_data[-1][u'登记编号'] = row['pleNo']
                dong_chan_di_ya_data[-1][u'登记日期'] = TimeUtils.get_date(row['regiDate'])
                dong_chan_di_ya_data[-1][u'登记机关'] = row['regOrgStr']
                dong_chan_di_ya_data[-1][u'被担保债权数额'] = str(row['priClaSecAm']) + u'万元'
                if row['type'] != '4' and row['type'] != 'undefined':
                    dong_chan_di_ya_data[-1][u'状态'] = u'有效'
                else:
                    dong_chan_di_ya_data[-1][u'状态'] = u'无效'
                dong_chan_di_ya_data[-1][u'公示日期'] = TimeUtils.get_date(row['pefPerForm'])

        family = 'Chattel_Mortgage'
        table_id = '11'
        self.json_result[family] = []
        for i in range(len(dong_chan_di_ya_data)):
            row = dong_chan_di_ya_data[i]
            self.json_result[family].append({})
            self.json_result[family][-1]['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.reg_code, self.today, i + 1)
            self.json_result[family][-1][family + ':registrationno'] = self.reg_code
            self.json_result[family][-1][family + ':enterprisename'] = self.cur_mc
            for k in row:
                col = family + ':' + GuangDongConfig.dong_chan_di_ya_dict[k]
                val = row[k]
                self.json_result[family][-1][col] = val

    def get_gu_quan_chu_zhi(self):
        gu_quan_chu_zhi_data = []
        url = "http://%s/aiccips//StoPleInfo/StoPleInfoList?pageNo=1&entNo=%s&regOrg=%s" % (self.host, self.ent_no, self.reg_org)
        r = self.get_request(url)
        result_data = json.loads(r.text)

        if result_data['list']['totalRecords'] > 0:
            for row in result_data['list']['list'] and result_data['list']['list']:
                gu_quan_chu_zhi_data.append({})
                # '''登记编号 	出质人 	证照/证件号码 	出质股权数额 	质权人 	证照/证件号码 	股权出质设立登记日期 	状态 	公示日期'''
                gu_quan_chu_zhi_data[-1][u'登记编号'] = row['stoRegNo']
                gu_quan_chu_zhi_data[-1][u'出质人'] = row['inv']
                if row['invType'] == '6':
                    if row['invID']:
                        gu_quan_chu_zhi_data[-1][u'出质人证照/证件号码'] = u'居民身份证' + '(' + row['invID'] + ')'
                    else:
                        gu_quan_chu_zhi_data[-1][u'出质人证照/证件号码'] = u'居民身份证'
                else:
                    gu_quan_chu_zhi_data[-1][u'出质人证照/证件号码'] = row['invID']

                gu_quan_chu_zhi_data[-1][u'出质股权数额'] = str(row['impAm']) + u'万元'

                gu_quan_chu_zhi_data[-1][u'质权人'] = row['impOrg']

                if row['impOrgType'] == '4':
                    if row['impOrgID']:
                        gu_quan_chu_zhi_data[-1][u'质权人证照/证件号码'] = u"居民身份证" + '(' + row['impOrgID'] + ')'
                    else:
                        gu_quan_chu_zhi_data[-1][u'质权人证照/证件号码'] = u"居民身份证"
                else:
                    gu_quan_chu_zhi_data[-1][u'质权人证照/证件号码'] = row['impOrgID']

                gu_quan_chu_zhi_data[-1][u'股权出质设立登记日期'] = TimeUtils.get_date(row['registDate'])
                if row['type'] == '1':
                    gu_quan_chu_zhi_data[-1][u'状态'] = u'有效'
                else:
                    gu_quan_chu_zhi_data[-1][u'状态'] = u'无效'
                gu_quan_chu_zhi_data[-1][u'公示日期'] = TimeUtils.get_date(row['registDate'])

        family = 'Equity_Pledge'
        table_id = '12'
        self.json_result[family] = []
        for i in range(len(gu_quan_chu_zhi_data)):
            row = gu_quan_chu_zhi_data[i]
            self.json_result[family].append({})
            self.json_result[family][-1]['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.reg_code, self.today, i + 1)
            self.json_result[family][-1][family + ':registrationno'] = self.reg_code
            self.json_result[family][-1][family + ':enterprisename'] = self.cur_mc
            for k in row:
                col = family + ':' + GuangDongConfig.gu_quan_chu_zhi_dict[k]
                val = row[k]
                self.json_result[family][-1][col] = val

    def get_jing_ying_yi_chang(self):
        url = "http://%s/aiccips/GSpublicity/GSpublicityList.html?service=cipUnuDirInfo" % self.host
        params = {
            'entNo': self.ent_no,
            'entType': self.ent_type,
            'regOrg': self.reg_org
        }
        r = self.post_request(url=url, data=params)
        soup = BeautifulSoup(r.text, 'lxml')
        th_list = soup.select('table#paginList tr.trTitleText td')
        tr_list = soup.select('table#paginList tr.tablebodytext')
        desc_list = [th_ele.text.strip() for th_ele in th_list]
        jing_ying_yi_chang_data = []
        for tr_ele in tr_list:
            if tr_ele.text.strip() in (u'暂无相关信息', u'暂无数据'):
                continue
            jing_ying_yi_chang_data.append({})
            td_list = tr_ele.select('td')
            for i in range(len(desc_list)):
                desc = desc_list[i]
                if desc in (u'序号', u'详情'):
                    continue
                # col = GuangDongConfig.bian_geng_dict[desc]
                val = td_list[i].text.strip()
                jing_ying_yi_chang_data[-1][desc] = val
                # print desc, val

        family = 'Business_Abnormal'
        table_id = '14'
        self.json_result[family] = []
        for i in range(len(jing_ying_yi_chang_data)):
            row = jing_ying_yi_chang_data[i]
            self.json_result[family].append({})
            self.json_result[family][-1]['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.reg_code, self.today, i + 1)
            self.json_result[family][-1][family + ':registrationno'] = self.reg_code
            self.json_result[family][-1][family + ':enterprisename'] = self.cur_mc
            for k in row:
                col = family + ':' + GuangDongConfig.jing_ying_yi_chang_dict[k]
                val = row[k]
                self.json_result[family][-1][col] = val
                # print col, val

    def get_chou_cha_jian_cha(self):
        chou_cha_jian_cha_data = []
        url = 'http://%s/aiccips//cipSpotCheInfo/cipSpotCheInfoList?pageNo=1&entNo=%s&regOrg=%s' % (self.host, self.ent_no, self.reg_org)
        r = self.get_request(url)
        result_data = json.loads(r.text)

        if result_data['list']['totalRecords'] > 0:
            for row in result_data['list']['list'] and result_data['list']['list']:
                chou_cha_jian_cha_data.append({})
                chou_cha_jian_cha_data[-1][u'检查实施机关'] = row['aicName'].strip()
                chou_cha_jian_cha_data[-1][u'类型'] = row['typeStr']
                chou_cha_jian_cha_data[-1][u'日期'] = TimeUtils.get_date(row['insDate'])
                chou_cha_jian_cha_data[-1][u'结果'] = row['inspectDetail']

        family = 'Spot_Check'
        table_id = '16'
        # print json.dumps(chou_cha_jian_cha_data, ensure_ascii=False)
        self.json_result[family] = []
        for i in range(len(chou_cha_jian_cha_data)):
            row = chou_cha_jian_cha_data[i]
            self.json_result[family].append({})
            self.json_result[family][-1]['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.reg_code, self.today, i + 1)
            self.json_result[family][-1][family + ':registrationno'] = self.reg_code
            self.json_result[family][-1][family + ':enterprisename'] = self.cur_mc
            for k in row:
                col = family + ':' + GuangDongConfig.chou_cha_jian_cha_dict[k]
                val = row[k]
                self.json_result[family][-1][col] = val

    def get_bian_geng_sz(self):

        __VIEWSTATE = self.soup.select('input#__VIEWSTATE')[0].attrs['value']
        __EVENTVALIDATION = self.soup.select('input#__EVENTVALIDATION')[0].attrs['value']

        tr_list = self.soup.select('div#bgxx table tr')
        th_list = tr_list[0].select('th')
        desc_list = [th_ele.text.strip() for th_ele in th_list]
        bian_geng_data = []
        for tr_ele in tr_list[1:]:
            if tr_ele.text.strip() == u'暂无相关信息':
                continue
            bian_geng_data.append({})
            td_list = tr_ele.select('td')
            for i in range(len(desc_list)):
                desc = desc_list[i]
                # col = GuangDongConfig.bian_geng_dict[desc]
                val = td_list[i].text.strip()
                bian_geng_data[-1][desc] = val
                # print desc, val
        # print json.dumps(bgxx_data)

        if len(self.soup.select('span#wucAlterItem_TurnPageBar1_lblBarTip')) > 0:
            row_num_info = self.soup.select('span#wucAlterItem_TurnPageBar1_lblBarTip')[0].text
            total_page_num = int(re.split(u'[共页]', row_num_info)[-2].strip())
        else:
            total_page_num = 0
        page_idx = 2
        # self.session.proxies = None
        if page_idx <= total_page_num:
            if self.session.proxies:
                self.session.proxies = None
                self.get_request(self.tag_a)
        while page_idx <= total_page_num:
            params = {
                'ScriptManager1': 'UpdatePanel5|wucAlterItem$TurnPageBar1$lbtnNextPage',
                'TakeEntID': '',
                '__ASYNCPOST': 'true',
                '__EVENTARGUMENT': '',
                '__EVENTTARGET': 'wucAlterItem$TurnPageBar1$lbtnNextPage',
                '__EVENTVALIDATION': __EVENTVALIDATION,
                '__VIEWSTATE': __VIEWSTATE,
                '__VIEWSTATEGENERATOR': self.__VIEWSTATEGENERATOR,
                'fromMail': '',
                'layerhid': '0',
                'txtrid': self.txtrid,
            }
            self.info(u'变更第%d页' % page_idx)

            r = self.post_request(self.tag_a, data=params, verify=False)
            # r = self.session.post(self.tag_a, data=params, verify=False)
            # print r.text
            idx_1 = r.text.find('<script type="text/javascript">')
            idx_2 = r.text.rfind('</div>') + len('</div>')
            data_text = r.text[idx_1:idx_2]
            param_text = r.text[idx_2:]

            _params = param_text.split('|')
            tmp_param = dict()
            for i in range(1, len(_params)):
                # print '<', i, y[i].replace('\n', ''), '>'
                if (i + 1) % 4 == 0:
                    col = _params[i].replace('\n', '')
                    val = _params[i + 1]
                    # print col, '->', val.replace('\n', ''), '>'
                    tmp_param[col] = val
            __VIEWSTATE = tmp_param['__VIEWSTATE']
            __EVENTVALIDATION = tmp_param['__EVENTVALIDATION']
            soup = BeautifulSoup(data_text, 'lxml')

            tr_list = soup.select('table tr')
            for tr_ele in tr_list[1:]:
                bian_geng_data.append({})
                td_list = tr_ele.select('td')
                for i in range(len(desc_list)):
                    desc = desc_list[i]
                    # col = GuangDongConfig.bian_geng_dict[desc]
                    val = td_list[i].text.strip()
                    bian_geng_data[-1][desc] = val
            page_idx += 1
        # self.session.proxies = self.proxy_config.get_proxy()
        family = 'Changed_Announcement'
        table_id = '05'
        self.json_result[family] = []
        for i in range(len(bian_geng_data)):
            row = bian_geng_data[i]
            self.json_result[family].append({})
            self.json_result[family][-1]['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.reg_code, self.today, i + 1)
            self.json_result[family][-1][family + ':registrationno'] = self.reg_code
            self.json_result[family][-1][family + ':enterprisename'] = self.cur_mc
            for k in row:
                col = family + ':' + GuangDongConfig.bian_geng_dict[k]
                val = row[k]
                self.json_result[family][-1][col] = val

    def get_gu_dong_sz(self):

        __VIEWSTATE = self.soup.select('input#__VIEWSTATE')[0].attrs['value']
        __EVENTVALIDATION = self.soup.select('input#__EVENTVALIDATION')[0].attrs['value']
        tr_list = self.soup.select('div#UpdatePanel2 table tr')
        th_list = tr_list[0].select('th')
        desc_list = [th_ele.text.strip() for th_ele in th_list]
        gu_dong_data = []
        for tr_ele in tr_list[1:]:
            if tr_ele.text.strip() == u'暂无相关信息':
                continue
            gu_dong_data.append({})
            td_list = tr_ele.select('td')
            for i in range(len(desc_list)):
                desc = re.sub('\\s', '', desc_list[i])
                val = td_list[i].text.strip()
                # print desc, val, [val]
                # col = GuangDongConfig.bian_geng_dict[desc]
                if desc == u'详情':
                    # continue
                    # print '**', desc
                    gd_id = td_list[i].attrs['info']
                    gd_detail = self.get_gu_dong_detail_sz(gd_id)
                    gu_dong_data[-1].update(gd_detail)
                else:
                    # val = td_list[i].text.strip()
                    gu_dong_data[-1][desc] = val
                # print desc, val
        # print json.dumps(bgxx_data)

        if len(self.soup.select('span#wucTZRInfo_TurnPageBar1_lblBarTip')) > 0:
            row_num_info = self.soup.select('span#wucTZRInfo_TurnPageBar1_lblBarTip')[0].text
            total_page_num = int(re.split(u'[共页]', row_num_info)[-2].strip())
            # print row_num_info
        else:
            total_page_num = 0

        page_idx = 2
        if page_idx <= total_page_num:
            if self.session.proxies:
                self.session.proxies = None
                self.get_request(self.tag_a)
        # print page_idx, total_page_num
        while page_idx <= total_page_num:
            # print page_idx, total_page_num
            self.info(u'股东第%d页' % page_idx)
            params = {
                'ScriptManager1': 'UpdatePanel2|wucTZRInfo$TurnPageBar1$lbtnNextPage',
                'TakeEntID': '',
                '__ASYNCPOST': 'true',
                '__EVENTARGUMENT': '',
                '__EVENTTARGET': 'wucTZRInfo$TurnPageBar1$lbtnNextPage',
                '__EVENTVALIDATION': __EVENTVALIDATION,
                '__VIEWSTATE': __VIEWSTATE,
                '__VIEWSTATEGENERATOR': self.__VIEWSTATEGENERATOR,
                'fromMail': '',
                'layerhid': '0',
                'txtrid': self.txtrid,
            }

            r = self.post_request(self.tag_a, data=params, verify=False)

            idx_1 = r.text.find('<div class="item_box">')
            idx_2 = r.text.rfind('</div>') + len('</div>')
            data_text = r.text[idx_1:idx_2]
            param_text = r.text[idx_2:]
            _params = param_text.split('|')
            tmp_param = dict()
            for i in range(1, len(_params)):
                # print '<', i, y[i].replace('\n', ''), '>'
                if (i + 1) % 4 == 0:
                    col = _params[i].replace('\n', '')
                    val = _params[i + 1]
                    # print col, '->', val.replace('\n', ''), '>'
                    tmp_param[col] = val
            __VIEWSTATE = tmp_param['__VIEWSTATE']
            __EVENTVALIDATION = tmp_param['__EVENTVALIDATION']
            soup = BeautifulSoup(data_text, 'lxml')

            tr_list = soup.select('table tr')
            for tr_ele in tr_list[1:]:
                gu_dong_data.append({})
                td_list = tr_ele.select('td')
                for i in range(len(desc_list)):
                    desc = desc_list[i]
                    # col = GuangDongConfig.bian_geng_dict[desc]
                    val = td_list[i].text.strip()
                    if desc == u'详情':
                        # continue
                        # print '**', desc
                        gd_id = td_list[i].attrs['info']
                        gd_detail = self.get_gu_dong_detail_sz(gd_id)
                        gu_dong_data[-1].update(gd_detail)
                        # continue
                    else:
                        # print desc, val
                        gu_dong_data[-1][desc] = val
            page_idx += 1
        # print '=>', json.dumps(gu_dong_data, ensure_ascii=False)
        family = 'Shareholder_Info'
        table_id = '04'
        self.json_result[family] = []
        for i in range(len(gu_dong_data)):
            row = gu_dong_data[i]
            self.json_result[family].append({})
            self.json_result[family][-1]['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.reg_code, self.today, i + 1)
            self.json_result[family][-1][family + ':registrationno'] = self.reg_code
            self.json_result[family][-1][family + ':enterprisename'] = self.cur_mc
            for k in row:
                col = family + ':' + GuangDongConfig.gu_dong_dict[k]
                if type(row[k]) != list:
                    val = re.sub('\\s', '', row[k])
                else:
                    val = row[k]
                self.json_result[family][-1][col] = val

    def get_gu_dong_detail_sz(self, recordid):
        url = "https://www.szcredit.org.cn/GJQYCredit/GSZJGSPTS/Detail/wucTZRInfoDetail.aspx?id=gdjczInfo&recordid=%s" % recordid
        r = self.get_request_sz(url=url, verify=False)
        soup = BeautifulSoup(r.text, 'lxml')

        rje = soup.select('span#RJE')[0].text.strip()
        sje = soup.select('span#SJE')[0].text.strip()

        rjczfs_mx = None
        rjcze_mx = None
        rjczrq_mx = None

        sjczfs_mx = None
        sjcze_mx = None
        sjczrq_mx = None

        rjmx_list = soup.select('div#rjmx table tr')

        rjmx = []
        sjmx = []

        for rjmx_ele in rjmx_list[1:]:
            td_list = rjmx_ele.select('td')
            rjczfs = td_list[0].text.strip()
            rjcze = td_list[1].text.strip()
            rjczrq = td_list[2].text.strip()
            if len(rjmx) == 0:
                rjczfs_mx = rjczfs
                rjcze_mx = rjcze
                rjczrq_mx = rjczrq
            rjmx.append({u'认缴出资方式': rjczfs, u'认缴出资额(万元)': rjcze, u'认缴出资日期': rjczrq})

        sjmx_list = soup.select('div#sjmx table tr')
        for sjmx_ele in sjmx_list[1:]:
            td_list = sjmx_ele.select('td')
            sjczfs = td_list[0].text.strip()
            sjcze = td_list[1].text.strip()
            sjczrq = td_list[2].text.strip()
            if len(sjmx) == 0:
                sjczfs_mx = sjczfs
                sjcze_mx = sjcze
                sjczrq_mx = sjczrq
            sjmx.append({u'实缴出资方式': sjczfs, u'实缴出资额(万元)': sjcze, u'实缴出资日期': sjczrq})
        return {
            u'认缴出资额': rje,
            u'实缴出资额': sje,
            u'认缴明细': rjmx,
            u'实缴明细': sjmx,
            u'认缴出资方式': rjczfs_mx,
            u'认缴出资额(万元)': rjcze_mx,
            u'认缴出资日期': rjczrq_mx,
            u'实缴出资方式': sjczfs_mx,
            u'实缴出资额(万元)': sjcze_mx,
            u'实缴出资日期': sjczrq_mx
        }

    def get_zhu_yao_ren_yuan_sz(self):
        zhu_yao_ren_yuan_data = []
        li_list = self.soup.select('div#MainPeople ul li')
        for li_ele in li_list:
            p_list = li_ele.select('p')
            if len(p_list) == 2:
                xm = p_list[0].text.strip()
                zw = p_list[1].text.strip()
                zhu_yao_ren_yuan_data.append({'keyperson_name': xm, 'keyperson_position': zw})
        # print json.dumps(zhu_yao_ren_yuan_data, ensure_ascii=False)
        family = 'KeyPerson_Info'
        table_id = '06'
        self.json_result[family] = []
        for i in range(len(zhu_yao_ren_yuan_data)):
            row = zhu_yao_ren_yuan_data[i]
            self.json_result[family].append({})
            self.json_result[family][-1]['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.reg_code, self.today, i + 1)
            self.json_result[family][-1][family + ':registrationno'] = self.reg_code
            self.json_result[family][-1][family + ':enterprisename'] = self.cur_mc
            for k in row:
                col = family + ':' + k
                val = row[k]
                self.json_result[family][-1][col] = val

    def get_fen_zhi_ji_gou_sz(self):
        fen_zhi_ji_gou_data = []
        li_list = self.soup.select('div#InformationOfAffiliatedAgency ul li')
        for li_ele in li_list:
            mc = li_ele.select('h4')[0].text.strip()
            dm = li_ele.select('span')[0].text.strip()
            djjg = li_ele.select('span')[1].text.strip()
            fen_zhi_ji_gou_data.append({'brname': mc, 'regno': dm, 'regorgName': djjg})
        family = 'Branches'
        table_id = '08'
        self.json_result[family] = []
        for i in range(len(fen_zhi_ji_gou_data)):
            row = fen_zhi_ji_gou_data[i]
            self.json_result[family].append({})
            self.json_result[family][-1]['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.reg_code, self.today, i + 1)
            self.json_result[family][-1][family + ':registrationno'] = self.reg_code
            self.json_result[family][-1][family + ':enterprisename'] = self.cur_mc
            for k in row:
                col = family + ':' + k
                val = row[k]
                self.json_result[family][-1][col] = val

    def get_qing_suan_sz(self):
        tr_list = self.soup.select('div#ClearInformation table tr')
        # print tr_list
        # print re.sub('\\s', '', tr_list[1].text), [re.sub('\\s', '', tr_list[1].text)], [u'清算组负责人'], re.sub('\\s', '', tr_list[1].text) == u'清算组负责人'
        qszfzr = re.sub('\\s', '', tr_list[1].text).replace(u'清算组负责人', '')
        qszcy = re.sub('\\s', '', tr_list[2].text).replace(u'清算组成员', '')
        # qszfzr = qszfzr.replace(u'清算组负责人', '')
        # qszcy = qszcy.replace(u'清算组成员', '')
        if qszfzr or qszcy:
            qing_suan_data = [{u'清算组负责人': qszfzr, u'清算组成员': qszcy}]
            family = 'liquidation_Information'
            table_id = '09'
            self.json_result[family] = []
            for i in range(len(qing_suan_data)):
                row = qing_suan_data[i]
                self.json_result[family].append({})
                self.json_result[family][-1]['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.reg_code, self.today, i + 1)
                self.json_result[family][-1][family + ':registrationno'] = self.reg_code
                self.json_result[family][-1][family + ':enterprisename'] = self.cur_mc
                for k in row:
                    col = family + ':' + GuangDongConfig.qing_suan_dict[k]
                    val = row[k]
                    self.json_result[family][-1][col] = val

    def get_xing_zheng_chu_fa_sz(self):
        tr_list = self.soup.select('div#XZCFXX table tr')
        th_list = tr_list[0].select('th')
        desc_list = [th_ele.text.strip() for th_ele in th_list]
        xing_zheng_chu_fa_data = []
        for tr_ele in tr_list[1:]:
            if tr_ele.text.strip() == u'暂无相关信息':
                continue
            xing_zheng_chu_fa_data.append({})
            td_list = tr_ele.select('td')
            for i in range(len(desc_list)):
                desc = desc_list[i]
                if desc == u'序号':
                    continue
                # col = GuangDongConfig.bian_geng_dict[desc]
                val = td_list[i].text.strip()
                xing_zheng_chu_fa_data[-1][desc] = val
                # print desc, val

        family = 'Administrative_Penalty'
        table_id = '13'
        self.json_result[family] = []
        for i in range(len(xing_zheng_chu_fa_data)):
            row = xing_zheng_chu_fa_data[i]
            self.json_result[family].append({})
            self.json_result[family][-1]['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.reg_code, self.today, i + 1)
            self.json_result[family][-1][family + ':registrationno'] = self.reg_code
            self.json_result[family][-1][family + ':enterprisename'] = self.cur_mc
            for k in row:
                col = family + ':' + GuangDongConfig.xing_zheng_chu_fa_dict[k]
                val = row[k]
                self.json_result[family][-1][col] = val
                # print col, val

    def get_jing_ying_yi_chang_sz(self):
        tr_list = self.soup.select('div#JYYCMLXX table tr')
        th_list = tr_list[0].select('th')
        desc_list = [th_ele.text.strip() for th_ele in th_list]
        jing_ying_yi_chang_data = []
        for tr_ele in tr_list[1:]:
            if tr_ele.text.strip() == u'暂无相关信息':
                continue
            jing_ying_yi_chang_data.append({})
            td_list = tr_ele.select('td')
            for i in range(len(desc_list)):
                desc = desc_list[i]
                if desc == u'序号':
                    continue
                # col = GuangDongConfig.bian_geng_dict[desc]
                val = td_list[i].text.strip()
                jing_ying_yi_chang_data[-1][desc] = val

        family = 'Business_Abnormal'
        table_id = '14'
        self.json_result[family] = []
        for i in range(len(jing_ying_yi_chang_data)):
            row = jing_ying_yi_chang_data[i]
            self.json_result[family].append({})
            self.json_result[family][-1]['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.reg_code, self.today, i + 1)
            self.json_result[family][-1][family + ':registrationno'] = self.reg_code
            self.json_result[family][-1][family + ':enterprisename'] = self.cur_mc
            for k in row:
                col = family + ':' + GuangDongConfig.jing_ying_yi_chang_dict[k]
                val = row[k]
                self.json_result[family][-1][col] = val

    def get_chou_cha_jian_cha_sz(self):
        tr_list = self.soup.select('div#UpdatePanel10 table tr')
        th_list = tr_list[0].select('th')
        desc_list = [th_ele.text.strip() for th_ele in th_list]
        chou_cha_jian_cha_data = []
        for tr_ele in tr_list[1:]:
            if tr_ele.text.strip() == u'暂无相关信息':
                continue
            chou_cha_jian_cha_data.append({})
            td_list = tr_ele.select('td')
            for i in range(len(desc_list)):
                desc = desc_list[i]
                if desc == u'序号':
                    continue
                # col = GuangDongConfig.bian_geng_dict[desc]
                val = td_list[i].text.strip()
                chou_cha_jian_cha_data[-1][desc] = val

        family = 'Spot_Check'
        table_id = '16'
        self.json_result[family] = []
        for i in range(len(chou_cha_jian_cha_data)):
            row = chou_cha_jian_cha_data[i]
            self.json_result[family].append({})
            self.json_result[family][-1]['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.reg_code, self.today, i + 1)
            self.json_result[family][-1][family + ':registrationno'] = self.reg_code
            self.json_result[family][-1][family + ':enterprisename'] = self.cur_mc
            for k in row:
                col = family + ':' + GuangDongConfig.chou_cha_jian_cha_dict[k]
                val = row[k]
                self.json_result[family][-1][col] = val

    def get_gu_quan_chu_zhi_sz(self):
        """
        数据存在bug待系统更新
        :return:
        """
        pass

    def get_dong_chan_di_ya_sz(self):
        """
        数据存在bug待系统更新
        :return:
        """
        pass

    def submit_search_request(self, keyword, account_id='null', task_id='null'):
        if check(keyword):
            is_xydm = True
        else:
            is_xydm = False
            keyword = self.process_mc(keyword)
        self.json_result = {'inputCompanyName': keyword, 'accountId': account_id, 'taskId': task_id}
        self.today = TimeUtils.get_today().replace('-', '')
        mc, xydm = '', ''
        self.info(u'从数据库获取tag_a。。。')
        self.tag_a = self.get_tag_a_from_db(mc)
        if not self.tag_a:
            self.info(u'从页面解析tag_a')
            self.tag_a = self.get_tag_a_from_page(keyword)
            if self.tag_a:
                self.info(u'保存tag_a')
                self.save_tag_a_to_db(self.tag_a)
        # print tag_a
        if self.tag_a:

            if 'szcredit' in self.tag_a:
                area = u'深圳'
                # return 999
            elif 'gzaic' in self.tag_a:
                area = u'广州'
            else:
                area = u'其他'

            # tag_a = tag_a.replace('https:', 'http:')
            # print self.tag_a
            self.info(keyword)
            self.info(u'获取详情。。。')
            # r = self.get_request(self.tag_a, verify=False)
            # self.soup = BeautifulSoup(r.text, 'lxml')
            # print self.soup
            if area == u'深圳':
                self.session.proxies = None
                r = self.get_request_sz(self.tag_a, verify=False)
                r.encoding = 'gbk'
                self.soup = BeautifulSoup(r.text, 'html5lib')
                self.host = None
                self.__VIEWSTATEGENERATOR = self.soup.select('input#__VIEWSTATEGENERATOR')[0].attrs['value']
                self.txtrid = self.soup.select('input#txtrid')[0].attrs['value']
                self.info(u'获取营业执照信息。。。')
                self.get_ying_ye_zhi_zhao_sz()  # 营业执照
                self.info(u'获取股东信息。。。')
                self.get_gu_dong_sz()  #
                self.info(u'获取变更信息。。。')
                self.get_bian_geng_sz()  #
                self.info(u'获取主要人员信息。。。')
                self.get_zhu_yao_ren_yuan_sz()  #
                # if not self.session.proxies:
                #     self.session.proxies = self.proxy_config.get_proxy()
                # self.get_fen_zhi_ji_gou_sz()  #
                # self.get_qing_suan_sz()
                # self.get_dong_chan_di_ya_sz()
                # self.get_gu_quan_chu_zhi_sz()
                # self.get_xing_zheng_chu_fa_sz()  #
                # self.get_jing_ying_yi_chang_sz()  # 经营异常
                # self.get_chou_cha_jian_cha_sz()  # 抽查检查
                # self.session.proxies = self.proxy_config.get_proxy()
            elif area == u'广州':
                r = self.get_request(self.tag_a, verify=False)
                self.soup = BeautifulSoup(r.text, 'lxml')
                self.host = "gsxt.gzaic.gov.cn"
                self.info(u'获取营业执照信息。。。')
                self.get_ying_ye_zhi_zhao()
                self.info(u'获取变更信息。。。')
                self.get_bian_geng()
                self.info(u'获取股东信息。。。')
                self.get_gu_dong()
                self.info(u'获取主要人员信息。。。')
                self.get_zhu_yao_ren_yuan()
                # self.get_fen_zhi_ji_gou()
                # self.get_qing_suan()
                # self.get_dong_chan_di_ya()
                # self.get_gu_quan_chu_zhi()
                # self.get_xing_zheng_chu_fa()
                # self.get_jing_ying_yi_chang()
                # self.get_chou_cha_jian_cha()

            else:
                r = self.get_request(self.tag_a, verify=False)
                self.soup = BeautifulSoup(r.text, 'lxml')
                self.host = "gd.gsxt.gov.cn"
                self.info(u'获取营业执照信息。。。')
                self.get_ying_ye_zhi_zhao()
                self.info(u'获取变更信息。。。')
                self.get_bian_geng()
                self.info(u'获取股东信息。。。')
                self.get_gu_dong()
                self.info(u'获取主要人员信息。。。')
                self.get_zhu_yao_ren_yuan()
                # self.get_fen_zhi_ji_gou()
                # self.get_qing_suan()
                # self.get_dong_chan_di_ya()
                # self.get_gu_quan_chu_zhi()
                # self.get_xing_zheng_chu_fa()
                # self.get_jing_ying_yi_chang()
                # self.get_chou_cha_jian_cha()
            # print json.dumps(self.json_result, ensure_ascii=False)
            if 'Registered_Info' in self.json_result:
                self.json_result['inputCompanyName'] = self.json_result['Registered_Info'][0]['Registered_Info:enterprisename']
            self.send_msg_to_kafka(json.dumps(self.json_result, ensure_ascii=False))
            return 1
        else:
            return 0
            # print json.dumps(self.json_result, ensure_ascii=False)

    def post_request_sz(self, url, **kwargs):
        for t in range(self.max_try_times):
            proxy_config = self.get_proxy()
            kwargs['proxies'] = {'http': 'http://%(user)d:%(pwd)s@%(proxy)s' % proxy_config,
                                 'https': 'https://%(user)d:%(pwd)s@%(proxy)s' % proxy_config}
            kwargs['timeout'] = proxy_config['timeout']
            kwargs.setdefault('headers', {})
            kwargs['headers']['Connection'] = 'close'
            kwargs['headers']['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:45.0) Gecko/20100101 Firefox/45.0'
            try:
                self.expected_ip = ''
                self.keep_ip = True
                if self.session:
                    r = self.session.post(url=url, **kwargs)
                else:
                    r = requests.post(url=url, **kwargs)
                self.keep_ip = False
                return r
            except requests.exceptions.RequestException, e:
                if t == self.max_try_times - 1:
                    raise e

    def get_request_sz(self, url, **kwargs):
        for t in range(self.max_try_times):
            proxy_config = self.get_proxy()
            # print json.dumps(proxy_config, ensure_ascii=False, indent=4)
            kwargs['proxies'] = {'http': 'http://%(user)d:%(pwd)s@%(proxy)s' % proxy_config,
                                 'https': 'https://%(user)d:%(pwd)s@%(proxy)s' % proxy_config}
            kwargs['timeout'] = proxy_config['timeout']
            kwargs.setdefault('headers', {})
            kwargs['headers']['Connection'] = 'close'
            kwargs['headers']['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:45.0) Gecko/20100101 Firefox/45.0'
            try:
                self.expected_ip = ''
                self.keep_ip = True
                if self.session:
                    r = self.session.get(url=url, **kwargs)
                else:
                    r = requests.get(url=url, **kwargs)
                self.keep_ip = False
                return r
            except requests.exceptions.RequestException, e:
                if t == self.max_try_times - 1:
                    raise e

if __name__ == '__main__':
    searcher = GuangDongSearcher()
    # searcher.submit_search_request(u'东莞中科云聚创业投资合伙企业（有限合伙）')
    # for i in range(50):
    print searcher.submit_search_request(u'91440882590076127B')
