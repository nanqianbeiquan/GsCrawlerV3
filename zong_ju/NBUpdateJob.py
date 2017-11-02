# coding=utf-8
import PackageTool
from geetest_broker import MySQL
from ZongJuSearcher import ZongJuSearcher
from gs import ProxyConf
import traceback


class NBUpdateJob(object):
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
        self.pk_name = 'mc'
        # self.src_table = 'enterprise_credit_info.bei_shang_guang_src'  # 北上广
        # self.src_table = 'enterprise_credit_info.jiang_zhe_src'  # 江浙
        self.src_table = 'enterprise_credit_info.fujian_src'  # 福建
        self.searcher = ZongJuSearcher()
        self.searcher.add_proxy(ProxyConf.key2)

    def info(self, msg):
        self.searcher.info(msg)

    def run(self):
        # 更新状态{0：无结果，1：有结果，-1：未更新，-2：更新中，10：非有限公司，11：编码有误，无法打印，99：只更新了一年的年报}
        cnt_0 = 0
        cnt_1 = 0
        cnt_2 = 0
        while True:
            sql_1 = "select %s from " \
                    "(" \
                    "select * from %s where update_status=-1 limit 100 " \
                    ") t " \
                    "order by RAND() limit 1" % (self.pk_name, self.src_table)
            # print sql_1
            res_1 = MySQL.execute_query(sql_1)
            if len(res_1) > 0:
                pk = str(res_1[0][0]).decode('utf-8')
                # print pk, [pk]
                sql_2 = "update %s set update_status=-2 where %s='%s'" % (self.src_table, self.pk_name, pk)
                MySQL.execute_update(sql_2)
                try:
                    update_status = self.searcher.load_nian_bao_msg(mc=pk, xydm="")
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
                else:
                    cnt_2 += 1
                self.info(u'查询有结果: %d, 查询无结果: %d, 查询失败:%d' % (cnt_1, cnt_0, cnt_2))
            else:
                self.info(u'更新完毕')
                break


if __name__ == '__main__':
    job = NBUpdateJob()
    job.run()
