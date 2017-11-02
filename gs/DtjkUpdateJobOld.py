# coding=utf-8


import PackageTool
from gs.UpdateFromTableMySQL import UpdateFromTable
from gs import MySQL
import traceback
from Crawler import GsCrawler
import sys
import platform
if platform.system() == 'Windows':
    coding = 'gbk'
else:
    coding = 'utf-8'


class DtjkUpdateJobOld(UpdateFromTable):

    province = None

    def __init__(self, province):
        super(DtjkUpdateJobOld, self).__init__()
        self.province = province

    def set_config(self):
        self.searcher = GsCrawler()
        # self.searcher.dst_topic = 'GSCrawlerTest'
        self.searcher.dst_topic = 'GSCrawlerResultTest'
        self.src_table = 'enterprise_credit_info.dtjk_company_src_old'
        self.pk_name = 'mc'

    def run(self):
        cnt_0 = 0
        cnt_1 = 0
        cnt_2 = 0
        while True:
            sql_1 = "select mc,province from " \
                    "(" \
                    "select * from %s where update_status=-1 " \
                    "and province='%s'" \
                    "limit 30 " \
                    ") t " \
                    "order by RAND() limit 1 " % (self.src_table, self.province)
            # print sql_1
            res_1 = MySQL.execute_query(sql_1)
            if len(res_1) > 0:
                mc = res_1[0][0]
                province = res_1[0][1]
                self.info(mc+'|'+province)
                sql_2 = "update %s set update_status=-2 " \
                        "where mc='%s'" \
                        % (self.src_table, mc)
                MySQL.execute_update(sql_2)
                try:
                    update_status = self.searcher.crawl(keyword=mc, province=province)
                    sql_3 = "update %s set update_status=%d, last_update_time=now() " \
                            "where mc='%s'" % \
                            (self.src_table, update_status, mc)
                except Exception, e:
                    traceback.print_exc(e)
                    update_status = -1
                    self.info(str(e))
                    sql_3 = "update %s set update_status=%d,last_update_time=now() " \
                            "where mc='%s'" % \
                            (self.src_table, update_status, mc)
                    self.searcher.delete_tag_a_from_db(mc, province)
                MySQL.execute_update(sql_3)
                if update_status == 0:
                    cnt_0 += 1
                elif update_status == 1:
                    cnt_1 += 1
                else:
                    cnt_2 += 1
                self.info(u'查询有结果: %d, 查询无结果: %d, 查询失败:%d' % (cnt_1, cnt_0, cnt_2))
            else:
                self.info(u'更新完毕')
                break


def get_args():
    args = dict()
    for arg in sys.argv:
        kv = arg.split('=')
        if len(kv) == 2:
            args[kv[0]] = kv[1]
    return args

if __name__ == '__main__':
    args = get_args()
    prov = args['province'].decode(coding)
    print prov, type(prov)
    job = DtjkUpdateJobOld(province=prov)
    job.run()
