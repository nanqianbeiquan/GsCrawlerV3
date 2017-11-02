# coding=utf-8
import re
import os
import sys
import MySQL
import json
from ProxyConf import ProxyConf, key1
import urllib
from requests.exceptions import ReadTimeout
from requests.exceptions import ConnectTimeout
from requests.exceptions import ProxyError
from requests.exceptions import ConnectionError
from requests.exceptions import ChunkedEncodingError
import requests
from MyException import StatusCodeException
import datetime
import Logger
import uuid
import subprocess
import random
from KafkaAPI import KafkaAPI
import mysql


class Searcher(object):

    pattern = re.compile("\s")
    cur_mc = ''  # 当前查询公司名称
    cur_zch = ''  # 当前查询公司注册号
    json_result = {}  # json输出结果
    plugin_path = None  # 验证码插件路径
    kafka = None  # kafka客户端
    dst_topic = "GSCrawlerTest"

    kafka2 = None
    dst_topic2 = None

    save_tag_a = True  # 是否需要存储tag_a
    today = None  # 当天
    session = None  # 提交请求所用session
    province = None  # 省份
    group = None  # 获取公司名称的组
    use_proxy = False  # 是否需要用代理
    input_company_name = None  # 输入的公司名称

    lock_id = '0'  # ip锁定标识
    release_id = '0'  # 要释放的ip
    proxy_config = None  # 代理浏览器头生成器
    timeout = 15  # request最大等待时间

    log_name = ''  # 日志文件名
    print_msg = True  # 是否打印日志
    headers = {}
    real_time = False
    crawler_id = str(uuid.uuid1())
    app_key = key1

    def __init__(self, use_proxy=False, dst_topic="GSCrawlerTest"):
        self.session = requests.session()
        self.use_proxy = use_proxy
        self.add_proxy(self.app_key)
        self.dst_topic = dst_topic

    def turn_off_print(self):
        # print '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.'
        self.print_msg = False

    @staticmethod
    def process_mc(mc):
        mc = mc.replace('(', u'（').replace(')', u'）')
        mc = re.sub(u'[ \u3000]', '', mc)
        return mc

    def info(self, msg):
        if self.real_time:
            name = self.province
        else:
            name = self.province + '_' + self.crawler_id
        Logger.write(msg, name=name, print_msg=self.print_msg)

    def add_proxy(self, key):
        # self.app_key = key  # 刘文海修改, 方便在submit中调用
        if self.use_proxy:
            self.proxy_config = ProxyConf(key)
            self.session.proxies = self.proxy_config.get_proxy()

    def reset_session(self):
        self.session = requests.session()
        self.add_proxy(self.app_key)

    def set_request_timeout(self, t):
        self.timeout = t

    def set_real_time(self, real_time):
        self.real_time = real_time

    def send_msg_to_kafka(self, msg):
        if not self.dst_topic:
            print msg
        else:
            if not self.kafka:
                self.kafka = KafkaAPI(self.dst_topic)
                self.kafka.init_producer()
            # print '-》', msg
            self.kafka.send(msg)
        if self.dst_topic2:
            if not self.kafka2:
                self.kafka2 = KafkaAPI(self.dst_topic2)
                self.kafka2.init_producer()
            self.kafka2.send(msg)

    def set_config(self):
        """
        设置参数(self.plugin_path)
        :return:
        """
        pass

    def submit_search_request(self, keyword, flags=True, account_id='null', task_id='null'):
        """
        提交查询请求
        :param keyword: 查询关键词(公司名称或者注册号)
        :param flags: True表示keyword代表公司名，False表示keyword代表注册号
        :param account_id: 在线更新,kafka所需参数
        :param task_id: 在线更新kafka所需参数
        :return:
        """
        keyword = self.process_mc(keyword)  # 公司名称括号统一转成全角
        self.input_company_name = keyword
        self.session = requests.session()  # 初始化session
        self.add_proxy(self.app_key)  # 为session添加代理
        res = 0
        self.cur_mc = ''  # 当前查询公司名称
        self.cur_zch = ''  # 当前查询公司注册号
        self.today = str(datetime.date.today()).replace('-', '')
        self.json_result.clear()
        self.json_result['inputCompanyName'] = keyword
        self.json_result['accountId'] = account_id
        self.json_result['taskId'] = task_id
        self.save_tag_a = True
        self.info(u'keyword: %s' % keyword)
        tag_a = self.get_tag_a_from_db(keyword)
        # print 'first_tag_a', tag_a
        if not tag_a:
            # print 'not _tag_a'
            if not flags:
                tag_a = self.get_tag_a_from_page(keyword, flags) # flags False:不需校验公司名称是否匹配
            else:
                tag_a = self.get_tag_a_from_page(keyword)
        # if not tag_a:  # 等所有省份都修改结束，使用此段代码代替以上代码
        #     tag_a = self.get_tag_a_from_page(keyword, flags)
        if tag_a:
            # print 'have _tag_a', tag_a
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
        # print json.dumps(self.json_result, ensure_ascii=False)
        self.send_msg_to_kafka(json.dumps(self.json_result, ensure_ascii=False))
        # self.info(json.dumps(self.json_result, ensure_ascii=False))
        return res

    def get_search_args(self, tag_a, keyword):
        """
        :param tag_a: tag_a
        :param keyword: 查询关键词
        根据tag_a解析查询所需参数, 如果查询结果和输入公司名不匹配返回空列表
        :rtype: list
        :return: 查询所需参数
        """
        pass

    def get_tag_a_from_db(self, keyword):
        """
        从数据库中查询tag_a, 如果数据库中存在tag_a,直接返回,否则需要提交验证码进行查询
        :param keyword: 查询关键词
        :rtype: str
        :return: 查询详情所需的tag_a
        """
        sql_1 = "select * from enterprise_credit_info.tag_a where mc='%s' and province='%s'" % (keyword, self.province)
        res_1 = MySQL.execute_query(sql_1)
        if len(res_1) > 0:
            self.save_tag_a = False
            tag_a = res_1[0][1]
            return tag_a
        else:
            return None

    def get_tag_a_from_page(self, keyword, flags=True):
        """
        从页面上通过提交验证码获取tag_a
        :param keyword: 查询关键词
        :param flags:true需要校验公司名，false不需校验(使用注册号查询)
        :rtype: str
        :return: tag_a
        """
        pass

    def save_tag_a_to_db(self, tag_a):
        """
        将通过提交验证码获取到的tag_a存储到数据库中
        :param tag_a: 查询关键词
        :return:
        """
        sql = "insert into enterprise_credit_info.tag_a values ('%s','%s',now(),'%s')" % (self.cur_mc, tag_a, self.province)
        try:
            MySQL.execute_update(sql)
        except mysql.connector.errors.IntegrityError:
            sql = "update enterprise_credit_info.tag_a " \
                  "set province='%s',tag_a='%s',last_update_time=now() where mc='%s'" \
                  % (self.province, tag_a, self.cur_mc)
            MySQL.execute_update(sql)

    def save_mc_to_db(self, mc):
        """
        将查询衍生出的公司名称存入数据库
        :param mc: 公司名称
        :return:
        """
        pass
        # mc = mc.replace("'", '"').replace(u"‘", '"')
        # sql = "insert into %s(mc,update_status,last_update_time,province) values ('%s',-1,now(),'%s')" \
        #       % (self.topic, mc, self.province)
        # try:
        #     MSSQL.execute_update(sql)
        # except mysql.connector.errors.IntegrityError:
        #     pass

    def get_yzm(self):
        """
        获取验证码
        :rtype: str
        :return: 验证码识别结果
        """
        self.info(u'下载验证码...')
        yzm_path = self.download_yzm()
        self.info(u'识别验证码...')
        yzm = self.recognize_yzm(yzm_path)
        os.remove(yzm_path)
        return yzm

    def get_yzm_path(self):
        self
        return os.path.join(sys.path[0], '../temp/' + str(random.random())[2:] + '.jpg')

    def download_yzm(self):
        """
        下载验证码图片
        :rtype str
        :return 验证码保存路径
        """
        return ""

    def recognize_yzm(self, yzm_path):
        """
        识别验证码
        :param yzm_path: 验证码保存路径
        :return: 验证码识别结果
        """
        cmd = self.plugin_path + " " + yzm_path
        process = subprocess.Popen(cmd.encode('GBK', 'ignore'), stdout=subprocess.PIPE)
        process_out = process.stdout.read()
        answer = process_out.split('\r\n')[6].strip()
        return answer.decode('gbk', 'ignore')

    def parse_detail(self):
        """
        解析公司详情信息
        :param kwargs:
        :return:
        """
        self.info(u'解析基本信息...')
        self.get_ji_ben()
        self.info(u'解析股东信息...')
        self.get_gu_dong()
        self.info(u'解析变更信息...')
        self.get_bian_geng()
        self.info(u'解析主要人员信息...')
        self.get_zhu_yao_ren_yuan()
        self.info(u'解析分支机构信息...')
        self.get_fen_zhi_ji_gou()
        self.info(u'解析清算信息...')
        self.get_qing_suan()
        self.info(u'解析动产抵押信息...')
        self.get_dong_chan_di_ya()
        self.info(u'解析股权出质信息...')
        self.get_gu_quan_chu_zhi()
        self.info(u'解析行政处罚信息...')
        self.get_xing_zheng_chu_fa()
        self.info(u'解析经营异常信息...')
        self.get_jing_ying_yi_chang()
        self.info(u'解析严重违法信息...')
        self.get_yan_zhong_wei_fa()
        self.info(u'解析抽查检查信息...')
        self.get_chou_cha_jian_cha()
        # self.get_nian_bao_link(*kwargs)
        self.info(u'获取年报信息...')
        # self.get_nian_bao()

    def get_ji_ben(self):
        """
        获取基本信息
        :return:
        """
        pass

    def get_gu_dong(self):
        """
        获取股东信息
        :return:
        """
        pass

    def get_bian_geng(self):
        """
        获取变更信息
        :return:
        """
        pass

    def get_zhu_yao_ren_yuan(self):
        """
        获取主要人员信息
        :return:
        """
        pass

    def get_fen_zhi_ji_gou(self):
        """
        获取分支机构信息
        :return:
        """
        pass

    def get_qing_suan(self):
        """
        获取清算信息
        :return:
        """
        pass

    def get_dong_chan_di_ya(self):
        """
        获取动产抵押信息
        :return:
        """
        pass

    def get_gu_quan_chu_zhi(self):
        """
        获取股权出质信息
        :return:
        """
        pass

    def get_xing_zheng_chu_fa(self):
        """
        获取行政处罚信息
        :return:
        """
        pass

    def get_jing_ying_yi_chang(self):
        """
        获取经营异常信息
        :return:
        """
        pass

    def get_yan_zhong_wei_fa(self):
        """
        获取严重违法信息
        :return:
        """
        pass

    def get_chou_cha_jian_cha(self):
        """
        获取抽查检查信息
        :return:
        """
        pass

    def get_nian_bao_link(self):
        """
        获取年报信息
        :return:
        """
        pass

    def get_nian_bao(self):
        """
        获取年报信息
        :return:
        """
        pass

    def save_company_name_to_db(self, company_name):
        pass
        # sql = "insert into %s(mc,update_status,province) values ('%s',-1,'%s')" % (self.topic, company_name, self.province)
        # try:
        #     MySQL.execute_update(sql)
        # except pyodbc.IntegrityError:
        #     pass

    def delete_tag_a_from_db(self, keyword):
        """
        从数据库中删除现存的tag_a
        :param keyword: 查询关键词
        """
        sql_1 = "delete from enterprise_credit_info.tag_a where mc='%s' and province='%s'" % (keyword, self.province)
        MySQL.execute_update(sql_1)

    def get_request(self, url, t=0, **kwargs):
        """
        发送get请求,包含添加代理,锁定ip与重试机制
        :param url: 请求的url
        :param t: 重试次数
        """
        try:
            if 'timeout' not in kwargs:
                kwargs['timeout'] = self.timeout
            if 'headers' not in kwargs:
                kwargs['headers'] = self.headers
            if self.use_proxy:
                kwargs['headers']['Proxy-Authorization'] = self.proxy_config.get_auth_header(lock_id=self.lock_id, release_id=self.release_id)
            r = self.session.get(url=url, **kwargs)
            if r.status_code != 200:
                # print r.status_code
                self.info(u'错误的响应代码 -> %d\n%s' % (r.status_code, url))
                # print r.text
                # if self.province == u'浙江省' and r.status_code == 504:
                #     del self.session
                #     self.session = requests.session()
                #     self.session.proxies = self.proxy_config.get_proxy()
                #     raise Exception(u'504错误')
                # if r.status_code == 403:
                #     if self.use_proxy:
                #         if self.lock_id != '0':
                #             self.proxy_config.release_lock_id(self.lock_id)
                #             self.lock_id = self.proxy_config.get_lock_id()
                #             self.release_id = self.lock_id
                #     else:
                #         raise Exception(u'IP被封')
                if r.status_code in (400, 403, 404, 407, 303):
                    return r
                raise StatusCodeException(u'错误的响应代码 -> %d\n%s' % (r.status_code, url))
            else:
                # print self.release_id
                if self.release_id != '0':
                    self.release_id = '0'
                # print r.headers
                return r
        except (ChunkedEncodingError, StatusCodeException, ReadTimeout, ConnectTimeout, ProxyError, ConnectionError) as e:
            if t == 5:
                raise e
            else:
                # print 't->', t
                return self.get_request(url, t+1, **kwargs)

    def post_request(self, url, t=0, **kwargs):
        """
        发送post请求,包含添加代理,锁定ip与重试机制
        :param url: 请求的url
        :param t: 重试次数
        :return:
        """
        try:
            if 'timeout' not in kwargs:
                kwargs['timeout'] = self.timeout
            if 'headers' not in kwargs:
                kwargs['headers'] = self.headers
            if self.use_proxy:
                kwargs['headers']['Proxy-Authorization'] = self.proxy_config.get_auth_header(lock_id=self.lock_id, release_id=self.release_id)
            r = self.session.post(url=url, **kwargs)
            if r.status_code != 200:
                self.info(u'错误的响应代码 -> %d\n%s' % (r.status_code, url))
                # if self.province in (u'浙江省', u'北京市') and r.status_code == 504:
                #     del self.session
                #     self.session = requests.session()
                #     self.session.proxies = self.proxy_config.get_proxy()
                #     raise Exception(u'504错误')
                # if r.status_code == 403:
                #     if self.use_proxy:
                #         if self.lock_id != '0':
                #             self.proxy_config.release_lock_id(self.lock_id)
                #             self.lock_id = self.proxy_config.get_lock_id()
                #             self.release_id = self.lock_id
                #     else:
                #         raise Exception(u'IP被封')
                if r.status_code in (400, 403, 404, 407, 303):
                    return r
                raise StatusCodeException(u'错误的响应代码 -> %d\n%s' % (r.status_code, url))
            else:
                if self.release_id != '0':
                    self.release_id = '0'
                return r
        except (ChunkedEncodingError, StatusCodeException, ReadTimeout, ConnectTimeout, ProxyError, ConnectionError) as e:
            if t == 5:
                raise e
            else:
                return self.post_request(url, t+1, **kwargs)

    def get(self, url, **kwargs):
        self.headers.update(kwargs.get('headers', {}))
        return self.get_request(url, **kwargs)

    def get_request_302(self, url, t=0, **kwargs):
        """
        手动处理包含302的请求
        :param url:
        :param t:
        :return:
        """
        try:
            for i in range(10):
                if self.use_proxy:
                    self.headers['Proxy-Authorization'] = self.proxy_config.get_auth_header(lock_id=self.lock_id, release_id=self.release_id)
                r = self.session.get(url=url, headers=self.headers, allow_redirects=False, timeout=self.timeout, **kwargs)
                # print '+' * 500
                # print r.status_code
                # print r.text
                # print '+' * 500
                if r.status_code != 200:
                    # print '+'*500
                    # print r.status_code
                    # print r.text
                    # print '+' * 500
                    if 300 <= r.status_code < 400:
                        self.release_id = '0'
                        protocal, addr = urllib.splittype(url)
                        url = protocal + '://' + urllib.splithost(addr)[0] + r.headers['Location']
                        continue
                    # elif self.province in (u'浙江省', u'北京市') and r.status_code == 504:
                    #     del self.session
                    #     self.session = requests.session()
                    #     self.session.proxies = self.proxy_config.get_proxy()
                    #     raise Exception(u'504错误')
                    # elif r.status_code == 403:
                    #     if self.use_proxy:
                    #         if self.lock_id != '0':
                    #             self.proxy_config.release_lock_id(self.lock_id)
                    #     else:
                    #         raise Exception(u'IP被封')
                    raise StatusCodeException(u'错误的响应代码 -> %d' % r.status_code)
                else:
                    if self.release_id != '0':
                        self.release_id = '0'
                    return r
        except (ChunkedEncodingError, StatusCodeException, ReadTimeout, ConnectTimeout, ProxyError, ConnectionError) as e:
            if t == 5:
                raise e
            else:
                return self.get_request_302(url, t+1, **kwargs)

    def post_request_302(self, url, t=0, **kwargs):
        """
        手动处理包含302的请求
        :param url:
        :param t:
        :return:
        """
        try:
            for i in range(10):
                if self.use_proxy:
                    self.headers['Proxy-Authorization'] = self.proxy_config.get_auth_header(lock_id=self.lock_id, release_id=self.release_id)
                r = self.session.post(url=url, headers=self.headers, allow_redirects=False, timeout=self.timeout, **kwargs)
                print 'r.status_code', r.status_code
                print 'r.headers', r.headers
                if r.status_code != 200:
                    if 300 <= r.status_code < 400:
                        protocal, addr = urllib.splittype(url)
                        if r.headers['Location'].startswith('http'):
                            url = r.headers['Location']
                        else:
                            url = protocal + '://' + urllib.splithost(addr)[0] + r.headers['Location']
                        print '302 url', url
                        continue
                    elif self.province in (u'浙江省', u'北京市') and r.status_code == 504:
                        del self.session
                        self.session = requests.session()
                        self.session.proxies = self.proxy_config.get_proxy()
                        raise Exception(u'504错误')
                    elif r.status_code == 403:
                        if self.use_proxy:
                            if self.lock_id != '0':
                                self.proxy_config.release_lock_id(self.lock_id)
                                self.lock_id = self.proxy_config.get_lock_id()
                                self.release_id = self.lock_id
                        else:
                            raise Exception(u'IP被封')
                    raise StatusCodeException(u'错误的响应代码 -> %d' % r.status_code)
                else:
                    if self.release_id != '0':
                        self.release_id = '0'
                    return r
        except (ChunkedEncodingError, StatusCodeException, ReadTimeout, ConnectTimeout, ProxyError, ConnectionError) as e:
            if t == 5:
                raise e
            else:
                return self.post_request_302(url, t+1, **kwargs)

    def get_lock_id(self):
        if self.use_proxy:
            self.release_lock_id()
            self.lock_id = self.proxy_config.get_lock_id()
            self.release_id = self.lock_id

    def release_lock_id(self):
        if self.use_proxy and self.lock_id != '0':
            self.proxy_config.release_lock_id(self.lock_id)
            self.lock_id = '0'


def get_args():
    args = dict()
    for arg in sys.argv:
        kv = arg.split('=')
        if kv[0] == 'companyName':
            args['companyName'] = kv[1].decode(sys.stdin.encoding, 'ignore')
        elif kv[0] == 'taskId':
            args['taskId'] = kv[1].decode(sys.stdin.encoding, 'ignore')
        elif kv[0] == 'accountId':
            args['accountId'] = kv[1].decode(sys.stdin.encoding, 'ignore')
    return args


if __name__ == '__main__':
   pass
