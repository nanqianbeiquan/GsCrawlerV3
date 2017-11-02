# coding=utf-8

import PackageTool
from KafkaAPI import KafkaAPI
from ProxyConf import key1 as app_key
import traceback

from guang_dong.GuangDongSearcher import GuangDongSearcher
from shang_hai.ShangHaiSearcher import ShangHaiSearcher
from bei_jing.BeiJingSearcher import BeiJing
from bei_jing_qi_ye_xin_xi import BeiJingQiYeXinXi
from zhe_jiang.ZheJiangSearcher import ZheJiangSearcher
from jiang_su.JiangSuSearcher import JiangSuSearcher
from shan_dong.ShanDongSearcher import ShanDongSearcher
from fu_jian.FuJianSearcher import FuJianSearcher
from he_bei.HeBei import HeBei
from tian_jin.TianJin import TianJinSearcher
from hu_bei.HuBeiSearcher import HuBeiSearcher
from zong_ju.ZongJuSearcher import ZongJuSearcher
from si_chuan.SiChuanSearcher import SiChuan
from liao_ning.LiaoNingSearcher import LiaoNingSearcher
from an_hui.AnHui import AnHui
import Logger
import sys
import json
import USCC
reload(sys)
sys.setdefaultencoding('utf8')
REAL_TIME = False  # 是否是实时更新，False表示实时更新不需proxy


class GsCrawler(object):

    print_msg = True
    crawler_class_dict = {
        u'北京市': BeiJingQiYeXinXi.BeiJingQiYeXinXiCrawler,
        u'辽宁省': LiaoNingSearcher,
        u'上海市': ShangHaiSearcher,
        u'浙江省': ZheJiangSearcher,
        u'广东省': GuangDongSearcher,
        u'河南省': ZongJuSearcher,
        u'福建省': FuJianSearcher,
        u'江苏省': JiangSuSearcher,
        u'宁夏回族自治区': ZongJuSearcher,
        # u'湖北省': HuBeiSearcher,
        u'海南省': ZongJuSearcher,
        u'重庆市': ZongJuSearcher,
        u'江西省': ZongJuSearcher,
        u'贵州省': ZongJuSearcher,
        u'四川省': SiChuan,
        u'天津市': TianJinSearcher,
        u'安徽省': AnHui,
        u'湖南省': ZongJuSearcher,
        u'河北省': HeBei,
        u'陕西省': ZongJuSearcher,
        u'山西省': ZongJuSearcher,
        u'山东省': ShanDongSearcher,
        u'黑龙江省': ZongJuSearcher,
        u'吉林省': ZongJuSearcher,
        u'内蒙古自治区': ZongJuSearcher,
        u'广西壮族自治区': ZongJuSearcher,
        u'云南省': ZongJuSearcher,
        u'西藏自治区': ZongJuSearcher,
        u'青海省': ZongJuSearcher,
        u'新疆维吾尔自治区': ZongJuSearcher,
        u'甘肃省': ZongJuSearcher,
        u'工商总局': ZongJuSearcher
    }

    crawler_dict = {}
    app_key = app_key
    log_name = None
    dst_topic = None
    dst_topic2 = None

    def __init__(self):
        pass

    def set_app_key(self, key=app_key):
        self.app_key = key

    def crawl(self, keyword, province, task_id='null', account_id='null'):
        if province not in self.crawler_dict:
            if province in self.crawler_class_dict:
                self.crawler_dict[province] = self.crawler_class_dict[province](dst_topic=self.dst_topic)  # 根据各爬虫的设置确定是否使用代理
                if self.dst_topic2:
                    self.crawler_dict[province].dst_topic2 = self.dst_topic2
                # if not self.print_msg:
                #     self.crawler_dict[province].turn_off_print()
                self.crawler_dict[province].set_real_time(REAL_TIME)
                self.crawler_dict[province].add_proxy(self.app_key)
            else:
                print(province+u'爬虫未上线!')
                return 999
        # print type(company_name)
        self.crawler_dict[province].province = province
        return self.crawler_dict[province].submit_search_request(keyword=keyword, account_id=account_id, task_id=task_id)

    def delete_tag_a_from_db(self, mc, province):
        if province in self.crawler_dict:
            self.crawler_dict[province].delete_tag_a_from_db(mc)

    def release_lock_id(self, province):
        if province in self.crawler_dict:
            self.crawler_dict[province].release_lock_id()

    def turn_off_print(self):
        self.print_msg = False

    def info(self, msg):
        Logger.write(msg, name=u'工商爬虫', print_msg=self.print_msg)


def get_args():
    args = dict()
    for arg in sys.argv:
        kv = arg.split('=')
        if len(kv) == 2:
            k = kv[0]
            if k != 'topic':
                v = kv[1].decode('gbk', 'ignore')
            else:
                v = kv[1]
            args[k] = v
    return args


if __name__ == '__main__':
    REAL_TIME = True
    # reload(sys)
    # sys.setdefaultencoding('utf8')
    # searcher = Guangdong()
    # searcher.submit_search_request(u"深圳市华为集成电路设计有限公司")
    args_dict = get_args()
    if len(args_dict) < 2:
        args_dict = {'companyName': u'桐乡其乐针织制衣有限公司', 'province': u'浙江省',
                     'taskId': '123', 'accountId': '456',
                     }
    # print json.dumps(args_dict, ensure_ascii=False)
    crawler = GsCrawler()
    # crawler.dst_topic = "GSCrawlerTest"
    # crawler.dst_topic = "GSCrawlerResultTest"
    crawler.dst_topic = "GsCrawlerOnline"
    # crawler.dst_topic = None
    try:
        print crawler.crawl(keyword=args_dict['companyName'], province=args_dict['province'],
                            task_id=args_dict['taskId'], account_id=args_dict['accountId'])
        print u'success'
    except Exception, e:
        traceback.print_exc(e)
        crawler.crawler_dict[args_dict['province']].info(traceback.format_exc(e))
        print u'fail'
