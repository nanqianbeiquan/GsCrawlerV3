# coding=utf-8

import PackageTool
import sys
from gs.KafkaAPI import KafkaAPI
import os
import uuid
import subprocess
from gs.SpiderMan import SpiderMan
# from gs.Searcher import Searcher
# from gs.Searcher import get_args
import json
from gs.TimeUtils import get_cur_time
from gs.TimeUtils import get_cur_ts_mil
from gs.CompareStatus import status_dict
from lxml import html
import requests
import datetime
from bs4 import BeautifulSoup
import re
import random
import time
from gs.MaYiLockId import get_lock_id

"""developer  fengyuanhua"""


class BeiJingQiYeXinXiCrawler(SpiderMan):
    def __init__(self, dst_topic=None):
        # super(BeiJingQiYeXinXiCrawler, self).__init__(use_proxy=True, dst_topic=dst_topic)
        super(BeiJingQiYeXinXiCrawler, self).__init__(dst_topic=dst_topic, keep_session=True, keep_ip=True)
        self.error_judge = False  # 判断网站是否出错，False正常，True错误
        self.set_config()
        self.cur_time = ''
        self.host_url = ''
        self.inner_url = ''
        self.bgq = ''
        self.bgh = ''
        self.reg_bus_ent_id = self.ent_id = ''
        self.cur_zch = ''  # 当前查询公司注册号或者统一社会信用代码
        self.cur_mc = ''  # 当前查询公司名称
        self.today = str(datetime.date.today()).replace('-', '')
        self.credit_ticket = ''

    def set_config(self):
        self.plugin_path = os.path.join(sys.path[0], r'..\bei_jing_qi_ye_xin_xi\ocr\beijing.bat')
        self.province = u'北京市'

    def download_yzm(self):
        image_url = 'http://qyxy.baic.gov.cn/CheckCodeYunSuan?currentTimeMillis=%s' % self.cur_time
        r = self.get_request(image_url)
        yzm_path = self.get_yzm_path()
        with open(yzm_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
                    f.flush()
            f.close()
        return yzm_path

    def recognize_yzm(self, yzm_path):
        """
        识别验证码
        :param yzm_path: 验证码保存路径
        :return: 验证码识别结果
        """
        cmd = self.plugin_path + " " + yzm_path
        # print self.plugin_path
        print yzm_path
        self.info(cmd)
        process = subprocess.Popen(cmd.encode('GBK', 'ignore'), stdout=subprocess.PIPE)
        process_out = process.stdout.read()
        # self.info('process_out', process_out
        answer = process_out.split('\r\n')[6].strip()
        # self.info('answer: ' + answer)
        return answer.decode('gbk', 'ignore')

    def get_contents(self, keyword, content_url):
        h3_tags = p_lists = []
        for i in range(15):
            print 'i', i
            data = {'queryStr': keyword, 'module': '', 'idFlag': 'qyxy'}
            r = self.post_request(content_url, data=data, timeout=15)
            r.encoding = 'utf-8'
            res = BeautifulSoup(r.text, 'html5lib')
            div = res.findAll('div', {'class': 'bx1'})
            if div:
                if u'无查询结果' in div[0].text.strip():
                    self.info(u'无查询结果')
                    return h3_tags, p_lists
                else:
                    try:
                        p_text = re.findall(u'记录总数\d+条', div[0].findAll('p')[-2].text.strip())[0]
                        all_records = int(re.findall(u'\d+', p_text)[0])
                        if all_records > 10:
                            for j in range(10):
                                data_new = {'queryStr': keyword, 'module': '', 'idFlag': 'qyxy', 'SelectPageSize': '50',
                                            'EntryPageNo': '1', 'pageNo': '1', 'pageSize': '50', 'clear': 'true'}
                                r_new = self.post_request(content_url, data=data_new, timeout=15)
                                r_new.encoding = 'utf-8'
                                res_new = BeautifulSoup(r.text, 'html5lib')
                                div_new = res_new.findAll('div', {'class': 'bx1'})
                                if div_new:
                                    h3_tags = div_new[0].findAll('h3')
                                    p_lists = div_new[0].findAll('p')[:len(h3_tags)]
                                    return h3_tags, p_lists
                                else:
                                    if j == 9:
                                        h3_tags = div[0].findAll('h3')
                                        p_lists = div[0].findAll('p')[:len(h3_tags)]
                                        return h3_tags, p_lists
                        else:
                            h3_tags = div[0].findAll('h3')
                            p_lists = div[0].findAll('p')[:len(h3_tags)]
                            return h3_tags, p_lists
                    except:
                        h3_tags = div[0].findAll('h3')
                        p_lists = div[0].findAll('p')[:len(h3_tags)]
                        return h3_tags, p_lists
            else:
                if i == 14:
                    return h3_tags, p_lists

    def get_inner_url(self, keyword, flags=True):
        check_code = ''
        inner_url = ''
        results = corp_prioritys = []
        self.host_url = 'http://qyxy.baic.gov.cn'
        self.get_request(self.host_url)  # 初始化headers的set-cookie
        yzm_path = self.download_yzm()
        for t in range(10):
            ticket_url = 'http://qyxy.baic.gov.cn/simple/dealSimpleAction!transport_ww.dhtml?' \
                         'fourth=fourth&sysid=0150008788304366b7d3903b5067bb8c&module=wzsy&styleFlag=sy'
            r_ticket = self.post_request(ticket_url)
            r_ticket.encoding = 'utf-8'
            res_ticket = BeautifulSoup(r_ticket.text, 'html5lib')
            res_str = res_ticket.encode('utf-8')
            self.credit_ticket = re.findall('var credit_ticket = ".*?"', res_str)
            if self.credit_ticket:
                self.credit_ticket = self.credit_ticket[0].split('"')[1]
                self.cur_time = res_ticket.find(id="currentTimeMillis").get('value')
                print self.credit_ticket, self.cur_time
                break
        for t in range(15):
            random_num = int(random.random() * 100000)
            # check_code = self.get_yzm()
            check_code = self.recognize_yzm(yzm_path)
            os.remove(yzm_path)
            print check_code, self.cur_time, random_num
            yz_url = 'http://qyxy.baic.gov.cn/login/loginAction!checkCode.dhtml?check_code=' + check_code \
                     + '&currentTimeMillis=' + self.cur_time + '&random=' + str(random_num)
            r_yz = self.post_request(yz_url)
            if r_yz.text.strip() == u'true':
                self.info(u'验证成功')
                break
            else:
                yzm_path = self.download_yzm()
                print r_yz.text.strip()
        content_url = 'http://qyxy.baic.gov.cn/es/esAction!entlist.dhtml?' \
                      'currentTimeMillis=%s&credit_ticket=%s&check_code=%s' % (
                          self.cur_time, self.credit_ticket, check_code)
        h3_tags, p_list = self.get_contents(keyword, content_url)
        if h3_tags:
            for i in range(len(h3_tags)):
                company_name = h3_tags[i].text.strip().split(u'\n')[0].strip()
                p_text = ''.join([text.strip().replace(u' ', u'') for text in p_list[i].text.strip().split(u'\n')])
                # print p_text
                tyshxydm = p_text.split(u'，')[0].split(u'：')[1].strip()
                print company_name, tyshxydm
                if keyword == company_name or tyshxydm == keyword or len(tyshxydm) == 15:
                    corp_status = h3_tags[i].text.strip().split(u'\n')[1].strip().replace(u'（', '').replace(u'）', '')
                    print corp_status
                    href = h3_tags[i].get('onclick').split("'")[1]
                    inner_url = self.host_url + href
                    print inner_url
                    corp_priority = status_dict[corp_status]
                    results.append({'corp_name': company_name, 'reg_no': tyshxydm, 'corp_priority': corp_priority,
                                    'inner_url': inner_url})
                    corp_prioritys.append(corp_priority)
            if corp_prioritys:
                corp_highest_priority = min(corp_prioritys)
            else:
                corp_highest_priority = 1
            if results:
                for result in results:
                    name = result['corp_name'].replace('(', u'（').replace(')', u'）')
                    tyshxydm = result['reg_no']
                    if flags:
                        if name == keyword or tyshxydm == keyword or len(tyshxydm) == 15:
                            priority_condition = result['corp_priority'] == corp_highest_priority
                            if priority_condition:
                                self.cur_mc = name
                                return result['inner_url']
                    else:
                        return result['inner_url']
            else:
                return inner_url
        else:
            return inner_url

    def parse_detail(self):
        """
        解析公司详情信息
        :param kwargs:
        :return:
        """
        pass
        self.get_ji_ben()
        self.get_gu_dong()
        self.get_bian_geng()
        self.get_zhu_yao_ren_yuan()
        # self.get_fen_zhi_ji_gou()
        # # self.get_qing_suan()
        # self.get_dong_chan_di_ya()
        # self.get_gu_quan_chu_zhi()
        # self.get_xing_zheng_chu_fa()
        # self.get_jing_ying_yi_chang()
        # self.get_yan_zhong_wei_fa()
        # self.get_chou_cha_jian_cha()
        # self.get_si_fa_xie_zhu()

    def get_ji_ben(self):
        """
        查询基本信息
        :return: 基本信息结果
        """
        family = 'Registered_Info'
        table_id = '01'
        result_values = dict()
        r = self.get_request(url=self.inner_url)
        r.encoding = 'utf-8'
        self.info(u'基本信息')
        res = BeautifulSoup(r.text, 'html5lib')
        jbxx_div = res.findAll('div', {'class': 'jic'})
        if not jbxx_div:
            self.error_judge = True
            self.info(res)
            raise ValueError('!!!!!!!!!!!!website is wrong!!!!!!!!!!!!!')
        # gdxx_divs = res.findAll('div', {'class': 'cha-1-du'})
        # self.gu_dong_url = gdxx_divs[0].find('table').get('onclick').split("'")[1]
        tables = jbxx_div[0].findAll('table', {'class': 'f-lbiao'})
        trs = tables[0].findAll('tr')[:8]
        self.cur_zch = trs[0].findAll('td')[-1].text.strip()
        zhu_ce_zi_ben_html = re.findall('<td width="182">.*?</td>', trs[2].encode('utf-8'), re.S)[0]
        td_soup = BeautifulSoup(zhu_ce_zi_ben_html, "html.parser")  # 实例化一个BeautifulSoup对象
        if self.cur_zch:
            if len(self.cur_zch) == 18:
                result_values[family + ':tyshxy_code'] = self.cur_zch
            else:
                result_values[family + ':zch'] = self.cur_zch
        result_values[family + ':registrationno'] = self.cur_zch
        result_values[family + ':enterprisename'] = trs[0].findAll('td')[1].text.strip()
        # result_values[family + ':enterprisename'] = trs[0].findAll('td', {'id': 'yanzheng'})[0].text.strip()
        result_values[family + ':legalrepresentative'] = trs[1].findAll('td')[-1].text.strip()
        result_values[family + ':enterprisetype'] = trs[1].findAll('td')[1].text.strip()
        result_values[family + ':establishmentdate'] = trs[2].findAll('td')[-1].text.strip()
        result_values[family + ':registeredcapital'] = td_soup.text.strip()
        result_values[family + ':residenceaddress'] = trs[3].findAll('td')[-1].text.strip()
        result_values[family + ':validityto'] = trs[4].findAll('td')[-1].text.strip()
        result_values[family + ':validityfrom'] = trs[4].findAll('td')[1].text.strip()
        result_values[family + ':businessscope'] = trs[5].findAll('td')[-1].text.strip()
        result_values[family + ':approvaldate'] = trs[6].findAll('td')[-1].text.strip()
        result_values[family + ':registrationinstitution'] = trs[6].findAll('td')[1].text.strip()
        result_values[family + ':registrationstatus'] = trs[7].findAll('td')[-1].text.strip()
        result_values['rowkey'] = '%s_%s_%s_' % (self.cur_mc, table_id, self.cur_zch)
        result_values[family + ':province'] = u'北京市'
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
        url = 'http://qyxy.baic.gov.cn/xycx/queryCreditAction!tzrlist_all.dhtml?' \
              'reg_bus_ent_id=%s&ent_page=1&moreInfo=&newInv=newInv&fqr=&SelectPageSize=1000&EntryPageNo=' \
              '1&pageNo=1&pageSize=1000&clear=true' % self.reg_bus_ent_id
        self.info(u'股东信息')
        r = self.get_request(url)
        result_values = dict()
        r.encoding = 'utf-8'
        res = BeautifulSoup(r.text, 'html5lib')
        table = res.findAll('table', {'id': 'tableIdStyle'})[0]
        trs = table.findAll('tr')[1:]
        new_trs = [tr for tr in trs if len(tr.findAll('td')) > 1]
        # tr_title = table.findAll('tr')[0]
        # ths = tr_title.findAll('th')
        for tr in new_trs:
            tds = tr.findAll('td')
            if len(tds) == 5:
                result_values[family + ':shareholder_name'] = tds[1].text.strip()
                result_values[family + ':shareholder_type'] = tds[2].text.strip()
                result_values[family + ':shareholder_certificationtype'] = tds[3].text.strip()
                result_values[family + ':shareholder_certificationno'] = tds[4].text.strip()
                result_values['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.cur_zch, self.today, j)
                result_values[family + ':registrationno'] = self.cur_zch
                result_values[family + ':enterprisename'] = self.cur_mc
                result_values[family + ':id'] = j
                result_list.append(result_values)
                result_values = {}
                j += 1
            else:
                self.info(u'其他新格式' + str(len(tds)))
                print tr
        self.json_result["Shareholder_Info"] = result_list

    def get_detail(self, res_detail):  # 变更详情专用by张晓刚
        row_data = []
        # tables=self.driver.find_elements_by_xpath("//*[@id='tableIdStyle']/tbody")
        tables = res_detail.find_all(id='tableIdStyle')
        for t in tables:
            time.sleep(1)
            trs = t.find_all("tr")
            bt = trs[0].text
            ths = trs[1].find_all("th")
            for tr in trs[2:]:
                tds = tr.find_all("td")
                col_nums = len(ths)
                for j in range(col_nums):
                    col = ths[j].text.strip().replace('\n', '')
                    if len(tds) == col_nums and u'无' not in tr.text:
                        td = tds[j]
                        val = td.text.strip()
                    else:
                        val = u'无'
                    row = col + u'：' + val
                    # print 'row', j, row
                    row_data.append(row)
            if u'变更前' in bt:
                self.bgq = u'；'.join(row_data)
                # print 'bgq',self.bgq
            elif u'变更后' in bt:
                self.bgh = u'；'.join(row_data)
                # print 'bgh',self.bgh
            row_data = []

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
        url = 'http://qyxy.baic.gov.cn/newChange/newChangeAction!bgxx_view.dhtml?reg_bus_ent_id=%s' % self.reg_bus_ent_id
        r = self.get_request(url)
        self.info(u'变更信息')
        result_values = dict()
        r.encoding = 'utf-8'
        res = BeautifulSoup(r.text, 'html5lib')
        table = res.findAll('table', {'id': 'tableIdStyle'})
        trs = table[0].findAll('tr')[1:]
        new_trs = [tr for tr in trs if len(tr.findAll('td')) > 1]
        for tr in new_trs:
            tds = tr.findAll('td')
            result_values[family + ':changedannouncement_date'] = tds[1].text.strip()
            result_values[family + ':changedannouncement_events'] = tds[2].text.strip()
            href = tds[3].find('a').get('onclick').split("'")[1]
            detail_url = self.host_url + href
            r_detail = self.get_request(detail_url)
            r_detail.encoding = 'utf-8'
            res_detail = BeautifulSoup(r_detail.text, 'html5lib')
            self.get_detail(res_detail)
            result_values[family + ':changedannouncement_before'] = self.bgq
            result_values[family + ':changedannouncement_after'] = self.bgh
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
        url = 'http://qyxy.baic.gov.cn/xycx/queryCreditAction!queryTzrxx_all.dhtml?' \
              'reg_bus_ent_id=%s&moreInfo=&SelectPageSize=1000&EntryPageNo=1' \
              '&pageNo=1&pageSize=1000&clear=true' % self.reg_bus_ent_id
        r = self.get_request(url)
        self.info(u'主要人员信息')
        r.encoding = 'utf-8'
        res = BeautifulSoup(r.text, 'html5lib')
        table = res.findAll('table', {'id': 'tableIdStyle'})
        trs = table[0].findAll('tr')[1:]
        new_trs = [tr for tr in trs if len(tr.findAll('td')) > 1]
        result_values = dict()
        for tr in new_trs:
            tds = tr.findAll('td')
            result_values[family + ':keyperson_name'] = tds[1].text.strip()
            result_values[family + ':keyperson_position'] = tds[2].text.strip()
            result_values['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.cur_zch, self.today, j)
            result_values[family + ':registrationno'] = self.cur_zch
            result_values[family + ':enterprisename'] = self.cur_mc
            result_values[family + ':id'] = j
            result_list.append(result_values)
            result_values = {}
            j += 1
        self.json_result["KeyPerson_Info"] = result_list

    def submit_search_request(self, keyword, flags=True, account_id='null', task_id='null'):
        """
        提交查询请求
        :param keyword: 查询关键词(公司名称或者注册号)
        :param flags: True表示keyword代表公司名，False表示keyword代表注册号
        :param account_id: 在线更新,kafka所需参数
        :param task_id: 在线更新kafka所需参数
        :return:
       """
        # self.session = requests.session()  # 初始化session
        # self.add_proxy(self.app_key)  # 为session添加代理
        # self.lock_id = get_lock_id(self.app_key['app_key'])
        # print self.lock_id
        out_come = 0
        # self.cur_mc = ''  # 当前查询公司名称
        # self.cur_zch = ''  # 当前查询公司注册号
        keyword = keyword.replace('(', u'（').replace(')', u'）')  # 公司名称括号统一转成全角
        self.info(u'keyword: %s' % keyword)
        self.json_result.clear()
        self.json_result['inputCompanyName'] = keyword
        self.json_result['accountId'] = account_id
        self.json_result['taskId'] = task_id
        inner_url = ''
        if not inner_url:
            if not flags:
                inner_url = self.get_inner_url(keyword, flags)  # flags False:不需校验公司名称是否匹配
            else:
                inner_url = self.get_inner_url(keyword)
        if inner_url:
            self.inner_url = inner_url
            self.reg_bus_ent_id = self.ent_id = self.inner_url.split('=')[1].split('&')[0]
            self.info(u'解析详情信息')
            self.parse_detail()
            out_come = 1
            # print r_inner.text
        else:
            self.info(u'查询无结果')
        self.info(u'消息写入kafka')
        self.send_msg_to_kafka(json.dumps(self.json_result, ensure_ascii=False))
        return out_come

    def delete_tag_a_from_db(self, keyword):
        pass


if __name__ == '__main__':
    searcher = BeiJingQiYeXinXiCrawler()
    # searcher.get_tag_a_from_page(u'锤子科技')
    searcher.submit_search_request(u'百度在线网络技术（北京）有限公司')
    # searcher.submit_search_request('91110105MA00G1W6X1')  # 锤子（北京）广告有限公司
    # searcher.submit_search_request('911101085977433169')  # 锤子科技（北京）股份有限公司
    # searcher.submit_search_request('91110108768478888D')  # 北京航天运通科技有限公司
    # 北京金商祺科技股份有限公司, 北京声迅电子股份有限公司
    # 买买电子商务股份有限公司 9111010539965913X2
    # 北京绿创声学工程股份有限公司 91110114766755618N
    # 昆腾微电子股份有限公司 911101087934019542
    # 北京市电影股份有限公司 91110101101316397E
    # 北京华环电子股份有限公司 9111010860000278XK
    # 北京富卓电子科技股份有限公司 911101081012078791
    # 蚁筹电子商务股份有限公司 91110105MA00348W73
    # 北京雅达养老产业股份有限公司 91110114774721901J
    # 中蜀万众创业电子科技股份有限公司 91110108MA0069HB2U
    searcher.info(json.dumps(searcher.json_result, ensure_ascii=False))
