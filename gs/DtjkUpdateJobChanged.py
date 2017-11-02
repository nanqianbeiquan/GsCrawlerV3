# coding=utf-8


import PackageTool
from gs.UpdateFromTableMySQL import UpdateFromTable
from gs import MySQL
import traceback
from gs import TimeUtils
from Crawler import GsCrawler
import json
import time


class DtjkUpdateJobChanged(UpdateFromTable):
    online_province = [
        u'上海市', u'北京市', u'广东省',
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
        super(DtjkUpdateJobChanged, self).__init__()
    # def set_config(self):
    #     self.searcher = GsCrawler()
    #     # self.searcher.dst_topic = 'GSCrawlerTest'
    #     self.src_table = 'enterprise_credit_info.dtjk_company_src'
    #     self.pk_name = 'mc'

    def set_config(self):
        self.searcher = GsCrawler()
        self.searcher.dst_topic = "GsCrawlerOnline"
        self.searcher.dst_topic2 = 'GSCrawlerResultTest'
        self.src_table = 'enterprise_credit_info.changed_mc_src'
        self.pk_name = 'mc'

    def run(self):
        # cnt_0 = 0
        # cnt_1 = 0
        # cnt_2 = 0
        # cnt_999 = 0
        fail_dict = dict()
        update_result = {u'更新成功': 0, u'查无结果': 0, u'更新失败': 0, u'未上线': 0}

        while True:
            # print json.dumps(fail_dict, ensure_ascii=False)
            sql_1 = "select mc,province from " \
                    "(" \
                    "select * from %s where update_status=-1 order by last_update_time limit 30 " \
                    ") t " \
                    "order by RAND() limit 1" % self.src_table
            # print sql_1
            res_1 = MySQL.execute_query(sql_1)
            if len(res_1) > 0:
                mc = res_1[0][0].decode('utf-8')
                province = res_1[0][1].decode('utf-8')
                # print mc, province
                self.info(mc + '|' + province)
                sql_2 = "update %s set update_status=-2,last_update_time=now() " \
                        "where mc='%s'" \
                        % (self.src_table, mc)
                MySQL.execute_update(sql_2)
                try:
                    if province in self.online_province:
                        update_status = self.searcher.crawl(keyword=mc, province=province)
                    else:
                        update_status = 999
                    sql_3 = "update %s set update_status=%d, last_update_time=now() " \
                            "where mc='%s'" % \
                            (self.src_table, update_status, mc)
                    if mc in fail_dict:
                        fail_dict.pop(mc)
                except Exception, e:
                    # traceback.print_exc(e)
                    self.info(traceback.format_exc(e))
                    if fail_dict.get(mc, 0) > 10:
                        update_status = 3
                        if mc in fail_dict:
                            fail_dict.pop(mc)
                    else:
                        update_status = -1
                        fail_dict[mc] = fail_dict.get(mc, 0) + 1
                    # self.info(str(e))
                    sql_3 = "update %s set update_status=%d " \
                            "where mc='%s'" % \
                            (self.src_table, update_status, mc)
                    self.searcher.delete_tag_a_from_db(mc, province)
                MySQL.execute_update(sql_3)
                # print 'update_status', update_status
                if update_status == 0:
                    update_result[u'查无结果'] += 1
                elif update_status == 1:
                    update_result[u'更新成功'] += 1
                elif update_status == 999:
                    update_result[u'未上线'] += 1
                else:
                    update_result[u'更新失败'] += 1
                self.info(json.dumps(update_result, ensure_ascii=False))
            else:
                self.info(u'更新完毕')
                time.sleep(5*60)

if __name__ == '__main__':
    job = DtjkUpdateJobChanged()
    job.run()
