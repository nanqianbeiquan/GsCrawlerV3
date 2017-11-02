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
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
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
    save_tag_a = False
    tag_a = None
    resdetail = None
    # token = None

    def __init__(self):
        super(ShanDongSearcher, self).__init__(use_proxy=False)
        # super(ShanDongSearcher, self).__init__(use_proxy=True)
        self.headers = {'Accept': 'application/json, text/javascript, */*; q=0.01',
                        'Accept-Encoding': 'gzip, deflate',
                        'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                        'Connection': 'keep-alive',
                        'Content-Length': '0',
                        'Host': 'sd.gsxt.gov.cn',
                        'X-Requested-With': 'XMLHttpRequest',
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

    def get_tag_a_from_page(self, keyword, flags=0):
        return self.get_tag_a_from_page0(keyword)

    def get_tag_a_from_page0(self, keyword):
        # self.flag = self.get_the_mc_or_code(keyword)
        # print self.flag
        url = 'http://sd.gsxt.gov.cn/'
        r = self.get_request(url)
        # print "r.text:", r.text
        start_page_handle_bak = None
        driver = webdriver.Firefox()
        self.driver = driver
        driver.set_window_size(1920, 1080)
        driver.get(url)
        input_path = r".//*[@id='keywords']"
        submit_path = r".//*[@id='btnsearch']"
        submit_detail = r".//*[@class='searchentname']"
        driver.find_element_by_xpath(input_path).clear()
        driver.find_element_by_xpath(input_path).send_keys(keyword)
        driver.find_element_by_xpath(submit_path).click()
        WebDriverWait(driver, 15).until(lambda the_driver: the_driver.find_element_by_xpath(".//*[@class='gt_slider_knob gt_show']"))
        time.sleep(2)
        # print 'before:', time.ctime()
        fa = 0
        element = driver.find_element_by_xpath(".//*[@class='gt_slider_knob gt_show']")
        try:
            for i in range(1, 20):
                # print '%d step1--click' % i
                ActionChains(driver).click_and_hold(on_element=element).perform()
                time.sleep(1)
                driver.get_screenshot_as_file('E:\\losg.jpg')
                time.sleep(1)
                img = Image.open('E:\\losg.jpg')
                # img.show()
                img_crop = img.crop((818, 419, 1078, 535))
                # img_crop.show()
                # img_path = os.path.join(sys.path[0], '../temp/' + str(random.random())[2:] + '.png')
                img_path = 'E:\\hebeijpg\\' + str(random.random())[2:] + '.png'
                # print 'img_path', img_path
                # img_path = 'E:\\losk.jpg'
                ocr_path = os.path.join(sys.path[0], '../shan_dong/slideocr/' + 'huadongjuli.exe')
                img_path1 = 'E:\\zfjpg300\\' + str(random.random())[2:] + '.png'
                # print 'img_path1', img_path1
                img_crop.save(img_path)
                if i == 11:
                    img_crop.save(img_path1)
                cmd = ocr_path + '  ' + img_path
                p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
                results = p.stdout.readlines()
                offset = int(results[0].strip())
                ActionChains(driver).move_to_element_with_offset(to_element=element, xoffset=offset+i*2, yoffset=10).perform()
                time.sleep(1)
                ActionChains(driver).release(on_element=element).perform()
                time.sleep(1)
                try:
                    WebDriverWait(driver, 5).until(lambda the_driver: the_driver.find_element_by_xpath(".//*[@class='resultitem']"))
                    break
                except Exception as e:
                    print 'yzm_exception', e
                    # continue
                fa += 1
        except:
            # print 'geetest--pass--success!'
            driver.get_screenshot_as_file(r'E:\\hbgee.jpg')
        # print 'after:', time.ctime()
        # 结果页面
        try:
            # source = driver.find_element_by_xpath(".//*[@class='searchresult']")
            html_content = driver.find_element_by_xpath("html")
            html = html_content.get_attribute("innerHTML")
            # print 'html_content:', html
            driver.quit()
        except:
            driver.quit()
            return None
        soup = BeautifulSoup(html, 'html5lib')
        # print 'soup:', soup
        token = soup.select('meta')[2].attrs['content']
        # print "token:", token
        session_1 = soup.find('body').find('input')
        session = session_1.attrs['value']
        # print "session:", session
        results = soup.find_all(class_='resultitem')
        # print 'results_lens', len(results)
        self.xydm_if = ''
        self.zch_if = ''
        cnt = 0
        if len(results) > 0:
            for r in results:
                cnt += 1
                name = r.find(class_='searchentname').find(target='_blank').text.strip()
                name = name.split('\n')[0]
                tag_a = r.find(class_='searchentname').a['href']
                print "parse_tag_a", tag_a
                driver.find_element_by_xpath(submit_detail).click()
                time.sleep(1)
                driver.switch_to.window(driver.window_handles[-1])
                time.sleep(1)
                detail_content = driver.find_element_by_xpath("html/body/div[1]")
                detail_html = detail_content.get_attribute("innerHTML")
                # token = detail_html.select('meta')[1].attrs['content']
                # all_handles = driver.window_handles #获取所有窗口句柄
                # for handle in all_handles:
                #     if handle != now_handle:
                #         print handle    #输出待选择的窗口句柄
                #         driver.switch_to.window(handle)
                #         time.sleep(5)
                #         driver.close()       #关闭当前窗口
                # print driver.find_element_by_xpath(".//*[@class='detailheader']")
                # WebDriverWait(driver, 20).until(lambda the_driver: the_driver.find_element_by_xpath(".//*[@class='detailheader']"))
                # WebDriverWait(driver, 20).until(lambda the_driver: the_driver.find_element_by_xpath(".//*[@class='detailheader']"))
                # detail_content = driver.find_element_by_xpath("html/body/div[1]")
                # detail_html = detail_content.get_attribute("innerHTML")
                # self.detail_html = detail_html
                # print "detail_html", detail_html
                url = 'http://sd.gsxt.gov.cn/pub/jbxx/qy/'+tag_a.split('/', 5)[4]
                print 'url_11', url
                self.headers['Referer'] = 'http://sd.gsxt.gov.cn'+tag_a
                self.headers['X-CSRF-TOKEN'] = token
                self.headers['Cookie'] = 'SESSION='+ session
                # print 'url:', url
                # print 'self.headers:', self.headers
                r = self.post_request(url=url, headers=self.headers)
                # print "r.text", r.text
                r.encoding = 'utf-8'
                self.detail_html = r.text
                # print "self.detail", r.text

        else:
            self.info(u'查询无结果')
            driver.quit()
            return None
        return tag_a

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
        self.get_gu_dong()
        self.get_bian_geng()
        self.get_zhu_yao_ren_yuan()
        # if u'主要人员信息' in self.resdetail.text:
        #     token = self.resdetail.select('meta')[3].attrs['content']
        #     self.token = token
        #     self.get_zhu_yao_ren_yuan(tag_a)
        # elif u'主管部门（出资人）信息' in self.resdetail.text:
        #     token = self.resdetail.select('meta')[2].attrs['content']
        #     self.token = token
        #     self.get_zhu_guan_bu_men(tag_a)
        self.get_fen_zhi_ji_gou()
        self.get_qing_suan()
        self.get_dong_chan_di_ya()
        self.get_gu_quan_chu_zhi()
        # self.get_xing_zheng_chu_fa(tag_a)
        self.get_jing_ying_yi_chang()
        # self.get_yan_zhong_wei_fa(tag_a)
        self.get_chou_cha_jian_cha()

    def get_ji_ben(self):
        """
        查询基本信息
        :return:
        """
        self.info(u'解析基本信息...')
        family = 'Registered_Info'
        table_id = '01'
        self.json_result[family] = []
        self.json_result[family].append({})
        content = self.detail_html.encode('utf-8').replace("\n", '').replace("\r\n", '').replace("\r\n", '')
        # print "content", content
        result_text = json.loads(content)
        result_json = result_text['jbxx']
        # result_json = content['jbxx']
        # print "result_json:", result_json
        for j in result_json:
            if j in ji_ben_dict:
                # self.json_result[family].append({})
                col = family + ':' + ji_ben_dict[j]
                val = result_json[j]
                self.json_result[family][-1][col] = val
            if j =='entname':
                self.cur_mc = result_json[j]
            if j == 'uniscid':
                self.cur_zch = result_json[j]
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
        for j in result_json:
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
        for i in range(len(self.json_result[family])):
            self.json_result[family][i]['rowkey'] = '%s_%s_%s_%s%d' % (self.cur_mc, table_id, self.cur_zch, self.today, i+1)
            self.json_result[family][i][family + ':registrationno'] = self.cur_zch
            self.json_result[family][i][family + ':enterprisename'] = self.cur_mc
            self.json_result[family][i][family + ':id'] = i+1
            # print json.dumps(self.json_result[family][i], ensure_ascii=False)

if __name__ == '__main__':
    args_dict = get_args()
    searcher = ShanDongSearcher()
    # searcher.delete_tag_a_from_db(u'山东天兴生物科技有限公司')
    # searcher.submit_search_request(u'山东远大板业科技有限公司')
    searcher.submit_search_request(u'山东天兴生物科技有限公司')
    # searcher.info(json.dumps(searcher.json_result, ensure_ascii=False))
    print json.dumps(searcher.json_result, ensure_ascii=False)
