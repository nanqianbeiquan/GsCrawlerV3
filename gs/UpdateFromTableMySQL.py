# coding=utf-8

import traceback
import MySQL
import time


class UpdateFromTable(object):

    src_table = None  #
    searcher = None  #
    pk_name = 'mc'

    def __init__(self):
        self.set_config()
        self.searcher.turn_off_print()
        self.log_name = self.searcher.log_name

    def set_config(self):
        """
        设置查询器和kafka队列参数
        示例
        self.searcher = LiaoNing()  # 因为kakfa 客户端需要从searcher中读取group和topic,因此一定要先生成searcher再生成kafka 客户端
        :return:
        """
        pass

    def info(self, msg):
        self.searcher.info(msg)

    def run(self):
        cnt_0 = 0
        cnt_1 = 0
        cnt_2 = 0
        cnt_3 = 0
        cnt_4 = 0
        while True:
            sql_1 = "select %s,page_idx from " \
                    "(" \
                    "select * from %s where update_status=-1 limit 30 " \
                    ") t " \
                    "order by RAND() limit 1" % (self.pk_name, self.src_table)
            # print sql_1
            res_1 = MySQL.execute_query(sql_1)
            if len(res_1) > 0:
                pk = res_1[0][0]
                page_idx = res_1[0][1]
                if not page_idx:
                    page_idx = 1
                sql_2 = "update %s set update_status=-2 where %s='%s'" % (self.src_table, self.pk_name, pk)
                MySQL.execute_update(sql_2)
                try:
                    update_status = self.searcher.submit_search_request(pk, page_idx=page_idx)
                except Exception, e:
                    self.info(traceback.format_exc(e))
                    update_status = -1
                    self.info(str(e))
                page_idx = self.searcher.page_idx
                sql_3 = "update %s set update_status=%d,last_update_time=now(),page_idx=%d where %s='%s'" % \
                        (self.src_table, update_status, page_idx, self.pk_name, pk)
                MySQL.execute_update(sql_3)
                if update_status == 0:
                    cnt_0 += 1
                elif update_status == 1:
                    cnt_1 += 1
                elif update_status == 9:
                    cnt_3 += 1
                elif update_status == 8:
                    cnt_4 += 1
                else:
                    cnt_2 += 1
                self.info(u'查询有结果: %d, 查询无结果: %d, 查询失败:%d, 拆分条件:%d, 无法拆分:%d' % (cnt_1, cnt_0, cnt_2, cnt_3, cnt_4))
            else:
                sql_4 = "update %s set update_status=-1 where update_status=-2 and " \
                        "TIMESTAMPDIFF(SECOND, last_update_time, now())>300" % self.src_table
                MySQL.execute_update(sql_4)

                sql_5 = "select ROW_COUNT()"
                res_5 = MySQL.execute_query(sql_5)
                if res_5[0][0] == 0:
                    self.info(u'更新完毕')
                    time.sleep(300)
