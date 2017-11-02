# coding=utf-8

import requests
import json
import time
import re
from KafkaAPI import KafkaAPI
import MySQL
import mysql.connector
import os
import uuid

import sys
import random
import Logger
import subprocess


class SpiderMan(object):
    session = None
    manager_host = '118.190.114.196'
    manager_port = 8080
    order = None
    real_time = False
    dst_topic = None
    kafka = None
    dst_topic2 = None
    kafka2 = None
    json_result = {}  # json输出结果
    save_tag_a = True
    print_msg = True
    province = None
    use_proxy = False
    cur_mc = None
    crawler_id = str(uuid.uuid1())
    plugin_path = None  # 验证码插件路径

    def __init__(self, keep_session=True, keep_ip=False, max_try_times=3, dst_topic="GSCrawlerTest"):
        self.order = '5fe6cf97-5592-11e7-be16-f45c89a63279'
        self.keep_ip = keep_ip
        self.expected_ip = ''
        if keep_session:
            self.session = requests.session()
        if max_try_times:
            self.max_try_times = max_try_times
        self.dst_topic = dst_topic

    @staticmethod
    def process_mc(mc):
        mc = mc.replace('(', u'（').replace(')', u'）')
        mc = re.sub(u'[ \u3000]', '', mc)
        return mc

    def add_proxy(self, order):
        pass

    def reset_session(self):
        self.session = requests.session()

    def turn_off_print(self):
        self.print_msg = False

    # def parse_detail(self):
    #     """
    #     解析公司详情信息
    #     :param kwargs:
    #     :return:
    #     """
    #     self.info(u'解析基本信息...')
    #     self.get_ji_ben()
    #     self.info(u'解析股东信息...')
    #     self.get_gu_dong()
    #     self.info(u'解析变更信息...')
    #     self.get_bian_geng()
    #     self.info(u'解析主要人员信息...')
    #     self.get_zhu_yao_ren_yuan()
    #     self.info(u'解析分支机构信息...')
    #     self.get_fen_zhi_ji_gou()
    #     self.info(u'解析清算信息...')
    #     self.get_qing_suan()
    #     self.info(u'解析动产抵押信息...')
    #     self.get_dong_chan_di_ya()
    #     self.info(u'解析股权出质信息...')
    #     self.get_gu_quan_chu_zhi()
    #     self.info(u'解析行政处罚信息...')
    #     self.get_xing_zheng_chu_fa()
    #     self.info(u'解析经营异常信息...')
    #     self.get_jing_ying_yi_chang()
    #     self.info(u'解析严重违法信息...')
    #     self.get_yan_zhong_wei_fa()
    #     self.info(u'解析抽查检查信息...')
    #     self.get_chou_cha_jian_cha()
    #     # self.get_nian_bao_link(*kwargs)
    #     self.info(u'获取年报信息...')
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

    # def delete_tag_a_from_db(self, keyword):
    #     """
    #     从数据库中删除现存的tag_a
    #     :param keyword: 查询关键词
    #     """
    #     sql_1 = "delete from enterprise_credit_info.tag_a where mc='%s' and province='%s'" % (keyword, self.province)
    #     MySQL.execute_update(sql_1)

    def delete_tag_a_from_db(self, keyword):
        """
        从数据库中删除现存的tag_a
        :param keyword: 查询关键词
        """
        sql_1 = "delete from enterprise_credit_info.tag_a where mc='%s' and province='%s'" % (keyword, self.province)
        MySQL.execute_update(sql_1)

    # def save_tag_a_to_db(self, tag_a):
    #     """
    #     将通过提交验证码获取到的tag_a存储到数据库中
    #     :param tag_a: 查询关键词
    #     :return:
    #     """
    #     sql = "insert into enterprise_credit_info.tag_a values ('%s','%s',now(),'%s')" % (
    #     self.cur_mc, tag_a, self.province)
    #     try:
    #         MySQL.execute_update(sql)
    #     except mysql.connector.errors.IntegrityError:
    #         sql = "update enterprise_credit_info.tag_a " \
    #               "set province='%s',tag_a='%s',last_update_time=now() where mc='%s'" \
    #               % (self.province, tag_a, self.cur_mc)
    #         MySQL.execute_update(sql)

    # def get_tag_a_from_db(self, keyword):
    #     """
    #     从数据库中查询tag_a, 如果数据库中存在tag_a,直接返回,否则需要提交验证码进行查询
    #     :param keyword: 查询关键词
    #     :rtype: str
    #     :return: 查询详情所需的tag_a
    #     """
    #     self.save_tag_a = True
    #     sql_1 = "select * from enterprise_credit_info.tag_a where mc='%s' and province='%s'" % (keyword, self.province)
    #     res_1 = MySQL.execute_query(sql_1)
    #     if len(res_1) > 0:
    #         self.save_tag_a = False
    #         tag_a = res_1[0][1]
    #         return tag_a
    #     else:
    #         return None

    def get_request(self, url, **kwargs):
        for t in range(self.max_try_times):
            proxy_config = self.get_proxy()
            # print json.dumps(proxy_config, ensure_ascii=False, indent=4)
            kwargs['proxies'] = {'http': 'http://%(user)d:%(pwd)s@%(proxy)s' % proxy_config,
                                 'https': 'https://%(user)d:%(pwd)s@%(proxy)s' % proxy_config}
            kwargs['timeout'] = proxy_config['timeout']
            kwargs.setdefault('headers', {})
            kwargs['headers']['Connection'] = 'close'
            kwargs['headers'][
                'User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:45.0) Gecko/20100101 Firefox/45.0'
            # if 'headers' in kwargs:
            #     kwargs['headers']['Proxy-Authentication'] = proxy_config['secret_key']
            # else:
            #     kwargs['headers'] = {'Proxy-Authentication': proxy_config['secret_key']}
            # print json.dumps(kwargs['headers'], ensure_ascii=False, indent=4)
            try:
                if self.session:
                    return self.session.get(url=url, **kwargs)
                else:
                    return requests.get(url=url, **kwargs)
            except requests.exceptions.RequestException, e:
                if t == self.max_try_times - 1:
                    raise e

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

    def get(self, url, **kwargs):
        return self.get_request(url, **kwargs)

    def post_request(self, url, **kwargs):
        for t in range(self.max_try_times):
            proxy_config = self.get_proxy()
            kwargs['proxies'] = {'http': 'http://%(user)d:%(pwd)s@%(proxy)s' % proxy_config,
                                 'https': 'https://%(user)d:%(pwd)s@%(proxy)s' % proxy_config}
            kwargs['timeout'] = proxy_config['timeout']
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
                    return self.session.post(url=url, **kwargs)
                else:
                    return requests.post(url=url, **kwargs)
            except requests.exceptions.RequestException, e:
                if t == self.max_try_times - 1:
                    raise e

    def reset_ip(self):
        self.expected_ip = ''

    def get_proxy(self, domain=None):
        while True:
            url = 'http://%s:%d/get-proxy-api' % (self.manager_host, self.manager_port)
            params = {'order': self.order}
            if self.keep_ip:
                params['expected_ip'] = self.expected_ip
            if domain is not None:
                params['domain'] = domain
            res = requests.get(url, params=params)
            # print res.text
            if res.status_code == 200 and res.text != '{}':
                json_obj = json.loads(res.text)
                if self.keep_ip:
                    self.expected_ip = json_obj['proxy'].split(':')[0]
                return json_obj
            else:
                time.sleep(1)
                print u'暂无可用代理'

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

    def add_to_black_list(self, domain, proxy_ip):
        params = {'domain': domain, 'proxy_ip': proxy_ip, 'order': self.order}
        print u'黑名单', params
        url = 'http://%s:%d/add-proxy-to-blacklist-api' % (self.manager_host, self.manager_port)
        r = requests.post(url, params=params)
        # print r.status_code

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

    def info(self, msg):
        if self.real_time:
            name = self.province
        else:
            name = self.province + '_' + self.crawler_id
        Logger.write(msg, name=name, print_msg=self.print_msg)

    def save_tag_a_to_db(self, tag_a):
        """
        将通过提交验证码获取到的tag_a存储到数据库中
        :param tag_a: 查询关键词
        :return:
        """
        sql = "insert ignore into enterprise_credit_info.tag_a values ('%s','%s',now(),'%s')" % (self.cur_mc, tag_a, self.province)
        try:
            print sql
            MySQL.execute_update(sql)
        except mysql.connector.errors.IntegrityError:
            sql = "update enterprise_credit_info.tag_a " \
                  "set province='%s',tag_a='%s',last_update_time=now() where mc='%s'" \
                  % (self.province, tag_a, self.cur_mc)
            MySQL.execute_update(sql)


if __name__ == '__main__':
    order_nbr = '5fe6cf97-5592-11e7-be16-f45c89a63279'
    crawler = SpiderMan(keep_session=True)
    r = crawler.get_request('http://1212.ip138.com/ic.asp',
                            headers={
                                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:45.0) Gecko/20100101 Firefox/45.0'}
                            )
    r.encoding = 'gbk'
    print r.text
