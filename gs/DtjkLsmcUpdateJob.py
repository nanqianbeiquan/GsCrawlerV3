# coding=utf-8

import PackageTool
import MySQL
from zong_ju.ZongJuSearcher import ZongJuSearcher
import traceback
from USCC import check
import json


class DtjkLsmcUpdateJob(object):
    src_table = None  #
    searcher = None  #
    pk_name = 'mc'

    def __init__(self):
        self.set_config()
        self.searcher.turn_off_print()
        self.log_name = u'历史名称更新'

    def set_config(self):
        """
        设置查询器和kafka队列参数
        示例
        self.searcher = LiaoNing()  # 因为kakfa 客户端需要从searcher中读取group和topic,因此一定要先生成searcher再生成kafka 客户端
        :return:
        """
        self.pk_name = 'mc'
        self.src_table = 'enterprise_credit_info.lsmc_src'  # 福建
        self.searcher = ZongJuSearcher()

    def info(self, msg):
        self.searcher.info(msg)

    def run(self):
        # 更新状态{0：无结果，1：有结果，-1：未更新，-2：更新中，10：非有限公司，11：编码有误，无法打印，99：只更新了一年的年报}
        cnt_0 = 0
        cnt_1 = 0
        cnt_2 = 0
        cnt_3 = 0
        while True:
            sql_1 = "select %s,xydm,province,last_update_time from " \
                    "(" \
                    "select * from %s where update_status=-1 order by last_update_time limit 15 " \
                    ") t " \
                    "order by RAND() limit 1" % (self.pk_name, self.src_table)
            res_1 = MySQL.execute_query(sql_1)
            if len(res_1) > 0:
                pk = res_1[0][0].decode('utf-8')
                province = res_1[0][2].decode('utf-8')
                last_update_time = res_1[0][3]
                # print pk, res_1[0][1], check(str(res_1[0][1]))
                xydm = str(res_1[0][1])
                if not check(xydm):
                    xydm = ''
                # print pk, [pk]
                sql_2 = "update %s set update_status=-2 where %s='%s'" % (self.src_table, self.pk_name, pk)
                MySQL.execute_update(sql_2)
                try:
                    self.info(json.dumps({'mc': pk, 'xydm': xydm}, ensure_ascii=False))
                    self.searcher.province = province
                    if last_update_time is None:
                        self.searcher.new_flag = True
                    if self.searcher.get_tag_a_from_page(keyword=pk, xydm=xydm):
                        update_status = 1
                        if self.searcher.has_lsmc:
                            update_status = 2
                            self.info(u'存在历史名称')
                    else:
                        update_status = 0
                except Exception, e:
                    # traceback.print_exc(e)
                    self.info(traceback.format_exc(e))
                    update_status = -1
                    # self.info(str(e))
                sql_3 = "update %s set update_status=%d,last_update_time=now() where %s='%s'" % \
                        (self.src_table, update_status, self.pk_name, pk)
                # print sql_3
                MySQL.execute_update(sql_3)
                if update_status == 0:
                    cnt_0 += 1
                elif update_status == 1:
                    cnt_1 += 1
                elif update_status == 2:
                    cnt_3 += 1
                else:
                    cnt_2 += 1
                self.info(u'查询有结果: %d, 查询无结果: %d, 查询失败:%d, 存在历史名称:%d ' % (cnt_1, cnt_0, cnt_2, cnt_3))
            else:
                self.info(u'更新完毕')
                break


if __name__ == '__main__':
    job = DtjkLsmcUpdateJob()
    job.run()
