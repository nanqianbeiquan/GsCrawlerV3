# coding=utf-8


import PackageTool
from gs.UpdateFromTableMySQL import UpdateFromTable
from gs import MySQL
import traceback
from gs import TimeUtils
from ZongJuSearcher import ZongJuSearcher


class DtjkUpdateJob(UpdateFromTable):

    def __init__(self):
        super(DtjkUpdateJob, self).__init__()

    def set_config(self):
        self.searcher = ZongJuSearcher()
        self.src_table = 'enterprise_credit_info.dtjk_company_src'
        self.pk_name = 'mc'

    def run(self):
        cnt_0 = 0
        cnt_1 = 0
        cnt_2 = 0
        while True:
            sql_1 = "select mc,province from " \
                    "(" \
                    "select * from %s where update_status=-1 limit 30 " \
                    ") t " \
                    "order by RAND() limit 1" % self.src_table
            # print sql_1
            res_1 = MySQL.execute_query(sql_1)
            if len(res_1) > 0:
                mc = res_1[0][0]

                last_update_date = TimeUtils.get_today()

                sql_2 = "update %s set update_status=-2 " \
                        "where mc='%s'" \
                        % (self.src_table, mc)
                MySQL.execute_update(sql_2)
                try:
                    update_status = self.searcher.submit_search_request(keyword=mc)
                    sql_3 = "update %s set update_status=%d, last_update_time=now() " \
                            "where mc='%s'" % \
                            (self.src_table, update_status, mc)
                except Exception, e:
                    self.info(traceback.format_exc(e))
                    update_status = -1
                    self.info(str(e))
                    sql_3 = "update %s set update_status=%d,last_update_time=now() " \
                            "where mc='%s'" % \
                            (self.src_table, update_status, mc)
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


if __name__ == '__main__':
    job = DtjkUpdateJob()
    job.run()