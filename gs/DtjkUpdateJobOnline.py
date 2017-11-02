# coding=utf-8


import PackageTool
from gs.UpdateFromTableMySQL import UpdateFromTable
from gs import MySQL
import traceback
from DtjkUpdateJob import DtjkUpdateJob
from Crawler import GsCrawler
import json


class DtjkUpdateJobOnline(DtjkUpdateJob):
    online_province = [
        u'上海市',
        # u'北京市',
        u'广东省',
        u'江苏省',
        u'浙江省',
        u'山东省',
        u'河北省', u'福建省',
        u'天津市', u'湖北省',
        u'河南省',
        u'海南省',
        u'重庆市',
        u'贵州省',
        u'湖南省',
        u'陕西省',
        u'山西省',
        u'黑龙江省',
        u'吉林省',
        u'内蒙古自治区',
        u'广西壮族自治区',
        u'云南省',
        u'西藏自治区',
        u'工商总局',
        u'宁夏回族自治区',
        u'甘肃省',
        u'青海省',
        u'江西省',
        u'新疆维吾尔自治区',
        u'四川省',
        u'辽宁省',
        u'安徽省',
    ]

    def __init__(self):
        super(DtjkUpdateJobOnline, self).__init__()
    # def set_config(self):
    #     self.searcher = GsCrawler()
    #     # self.searcher.dst_topic = 'GSCrawlerTest'
    #     self.src_table = 'enterprise_credit_info.dtjk_company_src'
    #     self.pk_name = 'mc'

    def set_config(self):
        self.searcher = GsCrawler()
        self.searcher.dst_topic = "GsOnline"
        self.src_table = 'enterprise_credit_info.dtjk_company_src'
        self.pk_name = 'mc'


if __name__ == '__main__':
    job = DtjkUpdateJobOnline()
    job.run()
