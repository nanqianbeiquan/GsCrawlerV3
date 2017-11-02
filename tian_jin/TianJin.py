# coding=utf-8

import PackageTool
import sys
import re
from gs import TimeUtils
from gs.Searcher import Searcher
from bs4 import BeautifulSoup
import random
import json
from gs.TimeUtils import *
from geetest_broker.GeetestBroker import GeetestBrokerRealTime
import TianJinConfig

reload(sys)
sys.setdefaultencoding('utf8')


class TianJinSearcher(Searcher, GeetestBrokerRealTime):
    """
    工商天津，各个表格相对独立，每个需要发送请求，返回内容需要
    重新寻找对应字段的意义（标注做好）
    """

    reg_code = None
    province = u'天津市'
    tag_a = None

    bian_geng_url = None
    gu_dong_url = None
    gu_quan_chu_zhi_url = None
    dong_chan_di_ya_url = None
    jing_ying_yi_chang_url = None
    zhu_yao_ren_yuan_url = None
    xing_zheng_chu_fa_url = None
    chou_cha_jian_cha_url = None
    nian_bao_url = None

    ignore_pattern = re.compile(u'[ ~`@$%\^&*_\-—+=\[\]{}|:;"\',.<>?/，。？、：；“”‘’【】．'
                                u'《》１２３４５６７８９０ｑｗｅｒｔｙｕｉｏｐａｓｄｆｇｈｊｋｌｚｘｃｖ'
                                u'ｂｎｍＱＷＥＲＴＹＵＩＯＰＡＳＤＦＧＨＪＫＬＺＸＣＶＢＮＭ]')

    def __init__(self, dst_topic=None):
        """
        设置查询结果存放的kafka的topic
        :param dst_topic: 调用kafka程序的目标topic，topic分测试环境和正式环境
        :return:
        """
        super(TianJinSearcher, self).__init__(use_proxy=True, dst_topic=dst_topic)
        self.error_judge = False  # 判断网站是否出错，False正常，True错误
        # self.session = requests.session()
        # self.proxy_config = ProxyConf(app_key)
        self.tag_a = ''
        self.corp_id = ''
        self.corp_org = ''
        self.corp_seq_id = ''
        self.set_config()
        self.headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:45.0) Gecko/20100101 Firefox/45.0",
                        }
        self.dengji_tree = ""
        self.beian_tree = ""
        self.ent_id = ''
        self.log_name = 'tian_jin'
        self.set_geetest_config()

    def set_config(self):
        """
        加载配置信息，注释掉的由调用程序统一配置
        :return:
        """
        # self.plugin_path = os.path.join(sys.path[0],  r'..\tian_jin\ocr\tianjinnewocr.exe')
        # self.group = 'Crawler'  # 正式
        # self.kafka = KafkaAPI("GSCrawlerResult")  # 正式
        # # self.group = 'CrawlerTest'  # 测试
        # # self.kafka = KafkaAPI("GSCrawlerTest")  # 测试
        # self.topic = 'GsSrc12'
        self.province = u'天津市'
        # self.kafka.init_producer()

    def get_token(self):
        """
        url地址随机参数方法
        :return:
        """
        return str(random.randint(50000000, 60000000))

    def set_geetest_config(self):
        """
        极验验证码版本参数配置
        :return:
        """
        # self.geetest_js_path = '/static/js/geetest.5.10.10.js'
        self.geetest_product = 'popup'
        self.geetest_referer = 'http://tj.gsxt.gov.cn/index.html'

    def get_gt_challenge(self):
        """
        获取极验验证码参数gt和challenge
        :return:
        """
        url_1 = 'http://tj.gsxt.gov.cn/SearchItemCaptcha?v=%s' % get_cur_ts_mil()
        # print url_1
        r_1 = self.get_request(url_1)
        self.gt = str(json.loads(r_1.text)['gt'])
        self.challenge = str(json.loads(r_1.text)['challenge'])
        # print 'gtx', self.gt, 'challenge', self.challenge

    def get_tag_a_from_page(self, keyword, flags=True):
        """
        获取查询结果
        :param keyword:
        :param flags:
        :return:
        """
        self.get_lock_id()
        validate = self.get_geetest_validate()
        # url_1 = "http://tj.gsxt.gov.cn/pc-geetest/validate"
        # params_1 = {
        #     'geetest_challenge': self.challenge,
        #     'geetest_validate': validate,
        #     'geetest_seccode': '%s|jordan' % validate,
        # }
        # r_1 = self.post_request(url=url_1, params=params_1)
        # print r_1.text

        # self.headers['Host'] = 'tj.gsxt.gov.cn'
        # self.headers['Referer'] = '	http://tj.gsxt.gov.cn/index.html'
        # self.headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        # self.headers['Accept-Language'] = 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3'
        # self.headers['Accept-Encoding'] = 'gzip, deflate'
        # self.headers['Connection'] = 'keep-alive'

        url_2 = 'http://tj.gsxt.gov.cn/corp-query-search-1.html'
        params_2 = {
            'geetest_challenge': self.challenge,
            'geetest_seccode': '%s|jordan' % validate,
            'geetest_validate': '%s' % validate,
            'searchword': keyword,
            'tab': 'ent_tab',
            'token': self.get_token()
        }
        # print params_2
        r = self.post_request(url=url_2, data=params_2)
        # print 'sssp', r.content
        self.release_lock_id()
        soup = BeautifulSoup(r.text, 'lxml')
        item_list = soup.select('a.search_list_item.db')
        if len(item_list) == 0 and u'查询到<span class="search_result_span1">0</span>条信息' not in r.text:
            raise Exception(u'查询异常')
        res_tag_a = None
        for item_ele in item_list:
            xydm, zch = '', ''
            # print '------->', item_ele
            mc = item_ele.select('h1')[0].text.replace('(', u'（').replace(')', u'）')
            mc = re.sub(r'\s', '', mc)
            history_name = u''
            if len(item_ele.select('div.div-info-circle3')) > 0:
                history_name = item_ele.select('div.div-info-circle3')[0].text
            tag_a = item_ele.attrs['href']
            # tag_a = tag_a[:-16]+'__cur_ts_mil__%7D'
            code_ele = item_ele.select('div.div-map2')[0]
            code_text = code_ele.text
            code_type, self.reg_code = [s.strip() for s in re.split(u'[:：]', code_text)]
            if mc == keyword or xydm or keyword in history_name:
                res_tag_a = tag_a
                self.cur_mc = mc
                break
            self.save_tag_a_to_db(tag_a, mc, xydm, zch)

        return res_tag_a

    def save_tag_a_to_db(self, tag_a, mc, xydm, zch):
        """
        存入公司详情信息url
        :param tag_a:
        :param mc:
        :param xydm:
        :param zch:
        :return:
        """
        pass

    def get_tag_a_from_db(self, keyword, xydm):
        """
        数据库获取公司url方法
        :param keyword:
        :param xydm:
        :return:
        """
        return None

    def submit_search_request(self, keyword, flags=True, account_id='null', task_id='null'):
        """
        提交详细查询请求，解析详情内容
        :param keyword: 查询输入内容
        :param flags: 查询内容信用代码还是公司名
        :param account_id: 账户id
        :param task_id: 任务id
        :return:
        """
        self.json_result = {}
        self.today = TimeUtils.get_today()
        keyword = keyword.replace('(', u'（').replace(')', u'）').replace(' ', '')
        mc, xydm = '', ''
        if flags:
            mc = keyword
        else:
            xydm = keyword

        self.tag_a = self.get_tag_a_from_page(keyword)
        if self.tag_a:
            self.json_result['inputCompanyName'] = keyword
            self.json_result['taskId'] = task_id
            self.json_result['accountId'] = account_id
            # self.info('jiben')
            self.get_ying_ye_zhi_zhao()
            # self.info('zhuyaorenyuan')
            try:
                self.get_zhu_yao_ren_yuan()
            except Exception as e:
                self.info(u'主要人员表失败:%s' %e)
                pass
            # self.info('biangeng')
            self.get_bian_geng()
            # self.info('gudong')
            self.get_gu_dong()
            # self.get_gu_quan_chu_zhi()
            # self.get_dong_chan_di_ya()
            # self.get_jing_ying_yi_chang()
            # self.get_chou_cha_jian_cha()
            # self.get_xing_zheng_chu_fa()
            # self.send_msg(json.dumps(self.json_result, ensure_ascii=False))  # 已失效

            self.send_msg_to_kafka(json.dumps(self.json_result, ensure_ascii=False))
            return 1
        else:
            return 0
            # print json.dumps(self.json_result, ensure_ascii=False)

    def get_ying_ye_zhi_zhao(self):
        ji_ben_url = 'http://tj.gsxt.gov.cn' + self.tag_a
        r = self.get_request(ji_ben_url)
        if r.status_code in (404, 400) or (r.text.startswith('{') and r.text.endswith('}')):
            return
        soup = BeautifulSoup(r.text, 'lxml')
        dl_list = soup.select('div#wrap-base dl')
        ying_ye_zhi_zhao_data = {}
        yyzz_data = dict()
        for dl in dl_list:
            desc = dl.select('dt')[0].text.strip().strip(u'：:')
            val = dl.select('dd')[0].text.strip()

            if desc in TianJinConfig.ying_ye_zhi_zhao_dict:
                col = TianJinConfig.ying_ye_zhi_zhao_dict[desc]
                ying_ye_zhi_zhao_data[col] = val
                yyzz_data[desc] = val
            else:
                raise UnknownColumnException(mc=self.cur_mc, col=desc)
        # print json.dumps(ying_ye_zhi_zhao, ensure_ascii=False)
        family = 'Registered_Info'
        table_id = '01'
        self.json_result[family] = []
        self.json_result[family].append({})
        for k in ying_ye_zhi_zhao_data:
            col = family + ':' + k
            val = ying_ye_zhi_zhao_data[k]
            self.json_result[family][-1][col] = val
        self.json_result[family][-1]['rowkey'] = '%s_%s_%s_' % (self.cur_mc, table_id, self.reg_code)
        # self.json_result[family][-1][family + ':registrationno'] = self.cur_zch
        self.json_result[family][-1][family + ':enterprisename'] = self.cur_mc
        self.json_result[family][-1][family + ':province'] = self.province
        self.json_result[family][-1][family + ':lastupdatetime'] = get_cur_time()

        # 获取其他模块url
        self.bian_geng_url = self.get_url('alterInfoUrl', r.text)
        self.gu_dong_url = self.get_url('shareholderUrl', r.text)
        self.jing_ying_yi_chang_url = self.get_url('entBusExcepUrl', r.text)
        self.gu_quan_chu_zhi_url = self.get_url('stakQualitInfoUrl', r.text)
        self.dong_chan_di_ya_url = self.get_url('mortRegInfoUrl', r.text)
        self.xing_zheng_chu_fa_url = self.get_url('punishmentDetailInfoUrl', r.text)
        self.chou_cha_jian_cha_url = self.get_url('spotCheckInfoUrl', r.text)
        self.nian_bao_url = self.get_url('anCheYearInfo', r.text)
        if 'enterprisetype' in ying_ye_zhi_zhao_data and ying_ye_zhi_zhao_data['enterprisetype'] not in (u'分公司', u'有限合伙企业'):
            self.zhu_yao_ren_yuan_url = self.get_url('keyPersonUrl', r.text)
        else:
            self.zhu_yao_ren_yuan_url = None
        return yyzz_data
        # print r.text

    @ staticmethod
    def get_url(flag, text):
        """
        静态方法，不继承self，可在class内部调用
        :param flag:
        :param text:
        :return:
        """
        pattern = re.compile('var ' + flag + '( )?=( )?"[^"]+"')
        res = pattern.search(text)
        if res:
            return 'http://tj.gsxt.gov.cn' + res.group().split('"')[1]
        else:
            return None

    def get_bian_geng(self):
        """
        获取变更信息内容
        :return:
        """
        draw = 1
        bian_geng_data = []
        while True:
            params = {
                'draw': draw,
                'length': 5,
                'start': 5*(draw-1),
            }
            # print 'get_bian_geng draw ->', draw
            # print params
            r = self.post_request(self.bian_geng_url, data=params)
            # print r.content
            json_obj = json.loads(r.text)
            data = json_obj['data']
            # print data
            if not data:
                self.info(u'无变更数据')
                return
            for item in data:
                bian_geng_data.append({})
                for k in item:
                    col = TianJinConfig.bian_geng_dict[k]
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
                    self.json_result[family][-1]['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.reg_code, self.today, i + 1)
                    self.json_result[family][-1][family + ':registrationno'] = self.reg_code
                    self.json_result[family][-1][family + ':enterprisename'] = self.cur_mc
                    for k in row:
                        col = family + ':' + k
                        val = row[k]
                        self.json_result[family][-1][col] = val
                break

    def get_gu_dong(self):
        """
        获取股东信息内容
        :return:
        """
        self.today = str(datetime.date.today()).replace('-', '')
        draw = 1
        gu_dong_data = []
        family = 'Shareholder_Info'
        table_id = '04'
        url_list = []
        while True:
            params = {
                'draw': draw,
                'length': 5,
                'start': 5*(draw-1),
            }
            r = self.post_request(self.gu_dong_url, data=params)
            json_obj = json.loads(r.text)
            data = json_obj['data']
            # print 'gddata', data
            url_list_a = [data[l]['invId'] for l in range(len(data))]
            url_list.extend(url_list_a)
            for item in data:
                gu_dong_data.append({})
                for k in item:
                    if k in TianJinConfig.gu_dong_dict:
                        col = TianJinConfig.gu_dong_dict[k]
                        val = item[k]
                        # print 'gcol', col, 'gval', val
                        if type(val) == unicode:
                            if '<span' in val:
                                val = re.sub('<span[^<]*</span>', '', val)
                            if '<div' in val:
                                val = re.sub('<div[^<]*</div>', '', val)
                            val = re.sub(r'\s', '', val)
                        gu_dong_data[-1][col] = val
            if int(json_obj['draw']) < int(json_obj['totalPage']):
                draw += 1
                # self.get_gu_dong(draw + 1, gu_dong_data)
            else:
                self.json_result[family] = []
                # url_list = [data[l]['invId'] for l in range(len(data))]
                # print 'url_list',url_list
                # divu = data[0]['invId']
                # print 'divu:',divu
                # print json.dumps(gu_dong_data, ensure_ascii=False)

                # print 'rjsj', rjsj, 'sjsj', sjsj
                for i in range(len(gu_dong_data)):
                    rjmx_list = []
                    sjmx_list = []
                    rjmx_dic = {}
                    sjmx_dic = {}
                    row = gu_dong_data[i]
                    # print i, row
                    self.json_result[family].append({})
                    for k in row:
                        col = family + ':' + k
                        val = row[k]
                        self.json_result[family][-1][col] = val
                    self.json_result[family][-1]['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.reg_code, self.today, i + 1)
                    self.json_result[family][-1][family + ':registrationno'] = self.reg_code
                    self.json_result[family][-1][family + ':enterprisename'] = self.cur_mc

                    # self.json_result[family][-1][family + ':subscripted_capital'] = gu_dong_data[i]['subscripted_amount']
                    # self.json_result[family][-1][family + ':actualpaid_capital'] = gu_dong_data[i]['actualpaid_amount']


                    # print 'len_url',len(url_list),'len_gudong', len(gu_dong_data)
                    url = 'http://tj.gsxt.gov.cn/corp-query-entprise-info-shareholderDetail-%s.html' %url_list[i]
                    # print url
                    r = self.get_request(url=url)
                    json_obj = json.loads(r.text)
                    data_dat = json_obj['data']

                    # print data_dat
                    sjn = len(data_dat[0])
                    rjn = len(data_dat[1])
                    # print 'sjnda0',sjn,'rjnda1',rjn
                    if sjn>0:
                        # data_dat[0]为实缴list
                        sjfs = data_dat[0][-1]['conForm_CN']

                        sjsj = data_dat[0][-1]['conDate']/1000
                        sjsj = time.strftime('%Y-%m-%d',time.localtime(int(sjsj)))
                    else:
                        sjfs = ''
                        sjsj = ''
                        self.json_result[family][-1][family + ':actualpaid_capital'] = ''

                    if rjn>0:
                        # data_dat[1]为认缴list
                        rjfs = data_dat[1][-1]['conForm_CN']
                        rjsj = data_dat[1][-1]['conDate']/1000
                        rjsj = time.strftime('%Y-%m-%d',time.localtime(int(rjsj)))
                    else:
                        rjfs = ''
                        rjsj = ''
                        self.json_result[family][-1][family + ':subscripted_capital'] = ''

                    self.json_result[family][-1][family + ':subscripted_method'] = rjfs
                    self.json_result[family][-1][family + ':subscripted_time'] = rjsj
                    self.json_result[family][-1][family + ':actualpaid_method'] = sjfs
                    self.json_result[family][-1][family + ':actualpaid_time'] = sjsj

                    if rjn>0:
                        rj_g = 0
                        for t in range(rjn):
                            rjmx_dic[u'认缴出资方式'] = data_dat[1][t]['conForm_CN']
                            rjmx_dic[u'认缴出资额(万元)'] = data_dat[1][t]['subConAm']
                            try:
                                rj_g = rj_g+float(data_dat[1][t]['subConAm'])
                            except:
                                rj_g = rj_g+0
                            rjsj_t = data_dat[1][t]['conDate']/1000
                            rjsj_t = time.strftime('%Y-%m-%d',time.localtime(int(rjsj_t)))
                            rjmx_dic[u'认缴出资日期'] = rjsj_t
                            rjmx_list.append(rjmx_dic)
                            rjmx_dic={}
                        # print 'rj_g',rj_g
                        self.json_result[family][-1][family + ':rjmx'] = rjmx_list
                        self.json_result[family][-1][family + ':subscripted_capital'] = rj_g

                    if sjn>0:
                        sj_g = 0
                        for t in range(sjn):
                            # print 'sj_t', t
                            sjmx_dic[u'实缴出资方式'] = data_dat[0][t]['conForm_CN']
                            sjmx_dic[u'实缴出资额(万元)'] = data_dat[0][t]['acConAm']
                            try:
                                sj_g = sj_g+float(data_dat[0][t]['acConAm'])
                            except:
                                sj_g = sj_g+0
                            sjsj_t = data_dat[0][t]['conDate']/1000
                            sjsj_t = time.strftime('%Y-%m-%d',time.localtime(int(sjsj_t)))
                            sjmx_dic[u'实缴出资日期'] = sjsj_t
                            sjmx_list.append(sjmx_dic)
                            sjmx_dic = {}
                        # print 'sj_g:',sj_g
                        self.json_result[family][-1][family + ':sjmx'] = sjmx_list
                        self.json_result[family][-1][family + ':actualpaid_capital'] = sj_g

                break

    def get_gu_quan_chu_zhi(self):
        """
        获取股权出质信息
        :return:
        """
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
                    if k in TianJinConfig.gu_quan_chu_zhi_dict:
                        col = TianJinConfig.gu_quan_chu_zhi_dict[k]
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
                    self.json_result[family][-1]['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.reg_code, self.today, i + 1)
                    self.json_result[family][-1][family + ':registrationno'] = self.reg_code
                    self.json_result[family][-1][family + ':enterprisename'] = self.cur_mc
                    for k in row:
                        col = family + ':' + k
                        val = row[k]
                        self.json_result[family][-1][col] = val
                break

    def get_dong_chan_di_ya(self):
        """
        获取动产抵押信息
        :return:
        """
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
                    if k in TianJinConfig.dong_chan_di_ya_dict:
                        col = TianJinConfig.dong_chan_di_ya_dict[k]
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
                    self.json_result[family][-1]['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.reg_code, self.today, i + 1)
                    self.json_result[family][-1][family + ':registrationno'] = self.reg_code
                    self.json_result[family][-1][family + ':enterprisename'] = self.cur_mc
                    for k in row:
                        col = family + ':' + k
                        val = row[k]
                        self.json_result[family][-1][col] = val
                break

    def get_dong_chan_di_ya_detail(self, dy_id, output_data):
        """
        获取动产抵押详情信息
        :param dy_id:
        :param output_data:
        :return:
        """
        # 抵押权人信息
        dyqrxx_url = 'http://tj.gsxt.gov.cn/corp-query-entprise-info-mortregpersoninfo-%s.html' % dy_id
        dyqrxx_res = self.get_request(dyqrxx_url)
        dyqrxx_data = json.loads(dyqrxx_res.text)['data']
        dyqrxx_dict = {
            'bLicType_CN': 'dyqr_zzlx',  # 抵押权人证照类型
            'more': 'dyqr_mc',  # 抵押权人名称
            'bLicNo': 'dyqr_zzhm',  # 证照号码
            # '': '',  # 住所地
        }
        # 被担保主债权信息
        bdbzzqxx_url = 'http://tj.gsxt.gov.cn/corp-query-entprise-info-mortCreditorRightInfo-%s.html' % dy_id
        bdbzzqxx_res = self.get_request(bdbzzqxx_url)
        bdbzzqxx_data = json.loads(bdbzzqxx_res.text)['data']
        bdbzzqxx_dict = {
            'priClaSecKind_CN': 'dbzq_zl',  # 种类
            'priClaSecAm': 'dbzq_sl',  # 数额
            'warCov': 'dbzq_fw',  # 担保的范围
            'remark': 'dbzq_bz',  # 备注
        }
        # 抵押物信息
        dywxx_url = 'http://tj.gsxt.gov.cn/corp-query-entprise-info-mortGuaranteeInfo-%s.html' % dy_id
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
        """
        获取主要人员信息
        :return:
        """
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
            # print url
            res = self.get_request(url)
            print res.text
            if u'您访问的页面不存在' in res.text:
                self.info(u'主要人员页面不存在')
                return
            if len(res.text)<3:
                print len(res.text)
                self.info(u'主要人员网页表单网站故障')
                return
            data = json.loads(res.text)['data']
            if not data:
                self.info(u'无主要人员信息')
                return
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
                        position = TianJinConfig.key_person_role_dict[position]
                    else:
                        position = person['position_CN']
                zhu_yao_ren_yuan_data.append({'keyperson_name': name, 'keyperson_position': position})
            # print json.dumps(zhu_yao_ren_yuan_data, ensure_ascii=False)

            total_page = int(json.loads(res.text)['totalPage'])
            # print page, total_page
            if page != total_page:
                start = json.loads(res.text)['start'] + json.loads(res.text)['perPage']
                page += 1
            else:
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
                break

    def get_jing_ying_yi_chang(self):
        """
        获取经营异常信息
        :return:
        """
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
                    if k in TianJinConfig.jing_ying_yi_chang_dict:
                        col = TianJinConfig.jing_ying_yi_chang_dict[k]
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
                    self.json_result[family][-1]['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.reg_code, self.today, i + 1)
                    self.json_result[family][-1][family + ':registrationno'] = self.reg_code
                    self.json_result[family][-1][family + ':enterprisename'] = self.cur_mc
                    for k in row:
                        col = family + ':' + k
                        val = row[k]
                        self.json_result[family][-1][col] = val
                break

    def get_xing_zheng_chu_fa(self):
        """
        获取行政处罚信息
        :return:
        """
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
                    if k in TianJinConfig.xing_zheng_chu_fa_dict:
                        col = TianJinConfig.xing_zheng_chu_fa_dict[k]
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
                    detail_url = 'http://tj.gsxt.gov.cn/doc/%s/casefiles/%s' % (item['nodeNum'], item['vPunishmentDecision']['fileName'])
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
                    self.json_result[family][-1]['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.reg_code, self.today, i + 1)
                    self.json_result[family][-1][family + ':registrationno'] = self.reg_code
                    self.json_result[family][-1][family + ':enterprisename'] = self.cur_mc
                    for k in row:
                        col = family + ':' + k
                        val = row[k]
                        self.json_result[family][-1][col] = val
                break

    def get_chou_cha_jian_cha(self):
        """
        获取抽查检查信息
        :return:
        """
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
                    if k in TianJinConfig.chou_cha_jian_cha_dict:
                        col = TianJinConfig.chou_cha_jian_cha_dict[k]
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
                    self.json_result[family][-1]['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.reg_code, self.today, i + 1)
                    self.json_result[family][-1][family + ':registrationno'] = self.reg_code
                    self.json_result[family][-1][family + ':enterprisename'] = self.cur_mc
                    for k in row:
                        col = family + ':' + k
                        val = row[k]
                        self.json_result[family][-1][col] = val
                break

    def get_nian_bao(self):
        """
        获取年报信息
        :return:
        """
        if not self.nian_bao_url:
            return
        nian_bao_links_res = self.get_request(self.nian_bao_url)
        try:
            nian_bao_links_json = json.loads(nian_bao_links_res.text)
        except ValueError:
            return
        an_che_id = None
        an_che_year = '0000'
        ent_type = None
        # print nian_bao_links_res.text
        if type(nian_bao_links_json) == list:
            for link_ele in nian_bao_links_json:
                # print json.dumps(link_ele, ensure_ascii=False)
                if 'anCheYear' in link_ele and link_ele['anCheYear'] > an_che_year:
                    an_che_year = link_ele['anCheYear']
                    an_che_id = link_ele['anCheId']
                    ent_type = link_ele['entType']
        # print 'an_che_id', an_che_id
        if an_che_id:
            self.get_nian_bao_detail(an_che_id, ent_type)

    def get_nian_bao_detail(self, an_che_id, ent_type):
        """
        获取年报详情信息
        :param an_che_id:
        :param ent_type:
        :return:
        """
        # print an_che_id, ent_type
        if not an_che_id:
            return
        if ent_type == 'pb':
            detail_url = "http://tj.gsxt.gov.cn/corp-query-entprise-info-vAnnualReportPbBaseinfo-%s.html" % an_che_id
            dst_table = "enterprise_credit_info.gtnb"
        else:
            detail_url = "http://tj.gsxt.gov.cn/corp-query-entprise-info-annualReportBaseinfo-%s.html" % an_che_id
            dst_table = "enterprise_credit_info.nb"
        detail_res = self.post_request(detail_url)
        # print detail_url
        # print detail_res.text
        detail_json = json.loads(detail_res.text)

        sql_1 = "select anCheId from %s where anCheId='%s'" % (dst_table, an_che_id)
        res_1 = MySQL.execute_query(sql_1)
        if len(res_1) == 0:
            cols = ['last_update_time', 'last_update_date']
            vals = ['now(),date(now())']
            for c in detail_json:
                v = detail_json[c]
                cols.append(c)
                if type(v) == unicode:
                    vals.append("'%s'" % v.replace("'", r"\'"))
                else:
                    if v:
                        v = str(v)
                    else:
                        v = 'null'
                    vals.append(v)
            sql_2 = "insert into %s(%s) values(%s)" % (dst_table, ','.join(cols), ','.join(vals))
            # print sql_2
            MySQL.execute_update(sql_2)
        else:
            c_v_list = ['last_update_time=now()', 'last_update_date=date(now())']
            for c in detail_json:
                v = detail_json[c]
                if type(v) == unicode:
                    v = "'%s'" % v.replace("'", r"\'")
                else:
                    if v:
                        v = str(v)
                    else:
                        v = 'null'
                c_v_list.append(c + '=' + v)

            sql_2 = "update %s set %s where anCheId='%s'" % (dst_table, ",".join(c_v_list), an_che_id)
            MySQL.execute_update(sql_2)
            # print sql_2

    def load_nian_bao_msg(self, mc, xydm):
        try:
            print mc, type(mc)
        except UnicodeEncodeError:  # 无法转码打印
            return 11
        self.tag_a = self.get_tag_a_from_page(mc, xydm)

        # print self.tag_a
        if self.tag_a:
            yyzz_data = self.get_ying_ye_zhi_zhao()
            if not yyzz_data or len(yyzz_data) == 0:
                return 0
            # print json.dumps(yyzz_data, ensure_ascii=False)
            mc = yyzz_data[u'企业名称'] if u'企业名称' in yyzz_data else yyzz_data[u'名称']
            sql_1 = "select * from enterprise_credit_info.yyzz where mc='%s'" % mc
            res_1 = MySQL.execute_query(sql_1)
            if len(res_1) == 0:
                cols = ['last_update_time', 'last_update_date']
                vals = ['now(),date(now())']
                for d in yyzz_data:
                    c = TianJinConfig.ying_ye_zhi_zhao_table[d]
                    v = yyzz_data[d]
                    cols.append(c)
                    if type(v) == unicode:
                        vals.append("'%s'" % v.replace("'", r"\'"))
                    else:
                        vals.append(str(v))
                sql_2 = "insert into enterprise_credit_info.yyzz(%s) values(%s)" % (','.join(cols), ','.join(vals))
            else:
                c_v_list = ['last_update_time=now()', 'last_update_date=date(now())']
                for d in yyzz_data:
                    c = TianJinConfig.ying_ye_zhi_zhao_table[d]
                    v = yyzz_data[d]
                    if type(v) == unicode:
                        v = "'%s'" % v.replace("'", r"\'")
                    else:
                        v = str(v)
                    c_v_list.append(c + '=' + v)
                sql_2 = "update enterprise_credit_info.yyzz set %s where mc='%s'" % (",".join(c_v_list), mc)
            MySQL.execute_update(sql_2)
            # print sql_2
            self.get_nian_bao()
            # print 'res', 1
            return 1
        else:
            return 0

    def get_lock_id(self):
        """
        请求过程加载动态代理ip锁定程序，1为锁定ip
        :param self:
        :return:
        """
        if self.use_proxy:
            self.release_lock_id()
            self.lock_id = self.proxy_config.get_lock_id()
            self.release_id = self.lock_id

    def release_lock_id(self):
        """
        请求过程锁定ip释放程序，0为释放ip
        :param self:
        :return:
        """
        if self.use_proxy and self.lock_id != '0':
            self.proxy_config.release_lock_id(self.lock_id)
            self.lock_id = '0'

# if __name__ == '__main__':
#     searcher = TianJinSearcher('GSCrawlerTest')
#     args_dict = get_args()
#     if args_dict:
#         searcher.submit_search_request(keyword=args_dict['companyName'], account_id=args_dict['accountId'], task_id=args_dict['taskId'])
#     else:
#         searcher.submit_search_request(u"天津市文光集团有限公司")
#         searcher.info(json.dumps(searcher.json_result, ensure_ascii=False))

if __name__ == '__main__':
    searcher = TianJinSearcher('GSCrawlerTest')
    searcher.submit_search_request(u"黛美服饰（厦门）有限公司天津分公司")
    searcher.info(json.dumps(searcher.json_result, ensure_ascii=False))


# test part
# if __name__ == '__main__':
#     searcher = TianJinSearcher('GSCrawlerTest')
#     f = open('E:\\tj301.txt', 'r').readlines()
#     # print f, len(f), f[0].strip().decode('gbk').encode('utf8')
#     cnt = 1
#     for name in f:
#         try:
#             word = name.strip().decode('gbk')#.encode('utf8')
#             print 'word',word,type(word)#.strip().decode('gbk').encode('utf8')
#         except:
#             word = name.strip()
#             print 'word2',word
#         try:
#             searcher.submit_search_request(word)
#             print cnt, json.dumps(searcher.json_result, ensure_ascii=False)
#         except Exception as e:
#             print '***error***:', word, e
#             pass
#         cnt += 1