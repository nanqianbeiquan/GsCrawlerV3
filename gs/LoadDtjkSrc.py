# coding=utf-8
import PackageTool
import mysql.connector
from gs import MySQL
from gs import Logger
import traceback
import TimeUtils
import datetime
import time


data_type = [u'工商']
UPDATE_PERIOD = 60*60*24*14


def info(msg):
    Logger.write(msg, name=u"生成每日查询条件", print_msg=False)


def load_company_test():
    config = {'host': '172.16.0.102',
              'user': 'bigdata1',
              'password': 'aaBigDataZZ123$',
              'port': 3306,
              'database': 'ljzxdb',
              'charset': 'utf8mb4'
              }

    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    sql = "select CompanyName,AreaName from v_monitorcompany"
    cursor.execute(sql)

    last_update_date_dict = {}
    update_status_dict = {}
    sql_1 = "select mc,date(last_update_time),update_status from enterprise_credit_info.dtjk_company_src_test"
    res_1 = MySQL.execute_query(sql_1)
    for row in res_1:
        last_update_date_dict[row[0]] = row[1]
        update_status_dict[row[0]] = row[2]
    while True:
        res = cursor.fetchmany(1000)
        insert_args = []
        update_args = []
        for row in res:
            mc = row[0]
            province = row[1]
            # city = row[4]
            # print type(name), type(province), type(city)
            info(mc)
            if not mc.isdigit() and len(mc) > 1:
                # sql_2 = u"select date(last_update_time),update_status from enterprise_credit_info.dtjk_company_src_test where mc='%s'" % mc
                # res_2 = MySQL.execute_query(sql_2)
                if mc not in update_status_dict:
                    insert_args.append((mc, province))
                else:
                    if not(last_update_date_dict[mc] == datetime.date.today() and update_status_dict[mc] in (0, 1) or update_status_dict[mc] == -1):
                        update_args.append((mc,))
        if insert_args:
            insert_sql = u"insert into enterprise_credit_info.dtjk_company_src_test " \
                    u"values(%s,-1,null,'动态监控测试',%s,null)"
            MySQL.execute_many_update(insert_sql, insert_args)
        if update_args:
            update_sql = u"update enterprise_credit_info.dtjk_company_src_test set update_status=-1 where mc=%s"
            MySQL.execute_many_update(update_sql, update_args)
        if len(res) < 1000:
            break
    sql_3 = '''
                UPDATE dtjk_company_src_test d, yyzz y
                SET d.xydm = y.xydm
                WHERE d.xydm is null and d.mc = y.mc;
            '''
    MySQL.execute_update(sql_3)


def load_company():
    config = {'host': '172.16.0.11',
              'user': 'bigdata1',
              'password': 'aaBigDataZZ123$',
              'port': 3306,
              'database': 'ljzxdb',
              'charset': 'utf8mb4'
              }

    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    sql = "select CompanyName,AreaName from v_monitorcompany"
    cursor.execute(sql)

    last_update_date_dict = {}
    update_status_dict = {}
    sql_1 = "select mc,date(last_update_time),update_status from enterprise_credit_info.dtjk_company_src"
    res_1 = MySQL.execute_query(sql_1)
    for row in res_1:
        last_update_date_dict[row[0]] = row[1]
        update_status_dict[row[0]] = row[2]

    while True:
        res = cursor.fetchmany(1000)
        insert_args = []
        update_args = []
        for row in res:
            mc = row[0]
            province = row[1]
            info(mc)
            if not mc.isdigit() and len(mc) > 1:
                if mc not in update_status_dict:
                    insert_args.append((mc, province))
                else:
                    if not(last_update_date_dict[mc] == datetime.date.today() and update_status_dict[mc] in (0, 1) or update_status_dict[mc] == -1):
                        update_args.append((mc,))
        if insert_args:
            insert_sql = u"insert into enterprise_credit_info.dtjk_company_src " \
                    u"values(%s,-1,null,'动态监控测试',%s,null)"
            MySQL.execute_many_update(insert_sql, insert_args)
        if update_args:
            update_sql = u"update enterprise_credit_info.dtjk_company_src set update_status=-1 where mc=%s"
            MySQL.execute_many_update(update_sql, update_args)
        if len(res) < 1000:
            break
    sql_3 = '''
            UPDATE dtjk_company_src d, yyzz y
            SET d.xydm = y.xydm
            WHERE d.xydm is null and d.mc = y.mc;
        '''
    MySQL.execute_update(sql_3)


def load_company_test_to_news():
    config = {'host': '172.16.0.102',
              'user': 'bigdata1',
              'password': 'aaBigDataZZ123$',
              'port': 3306,
              'database': 'ljzxdb',
              'charset': 'utf8mb4'
              }

    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    sql = "select CompanyName,MonitorDate from v_monitorcompany"
    cursor.execute(sql)
    while True:
        res = cursor.fetchmany(1000)
        values = []
        for row in res:
            mc = row[0]
            monitor_date = row[1]
            values.append((mc, monitor_date))

        if values:
            insert_sql = u"insert into news.dtjk_company_src(mc,monitor_date) values(%s,%s) on duplicate key update update_status=-1"
            MySQL.execute_many_update(insert_sql, values)
        if len(res) < 1000:
            break


def load_company_to_news():
    MySQL.execute_update('truncate table news.dtjk_company_src')
    config = {'host': '172.16.0.11',
              'user': 'bigdata1',
              'password': 'aaBigDataZZ123$',
              'port': 3306,
              'database': 'ljzxdb',
              'charset': 'utf8mb4'
              }

    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    sql = "select CompanyName,MonitorDate from v_monitorcompany"
    cursor.execute(sql)
    while True:
        res = cursor.fetchmany(1000)
        values = []
        for row in res:
            mc = row[0]
            monitor_date = row[1]
            values.append((mc, monitor_date))

        if values:
            insert_sql = u"insert into news.dtjk_company_src(mc,monitor_date) values(%s,%s) on duplicate key update update_status=-1"
            MySQL.execute_many_update(insert_sql, values)
        if len(res) < 1000:
            break


def load_zhangjiang():
    config = {'host': '172.16.0.11',
              'user': 'bigdata1',
              'password': 'aaBigDataZZ123$',
              'port': 3306,
              'database': 'dataterminaldbzj',
              'charset': 'utf8mb4'
              }
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    sql = "select * from monitortodaycompany"
    cursor.execute(sql)
    res = cursor.fetchall()
    # MySQL.execute_update("truncate table law.dtjk_company_src")
    for row in res:
        mc = row[1]
        if not mc.isdigit() and len(mc) > 1:
            sql2 = u"insert into enterprise_credit_info.dtjk_company_src values('%s',-1,null,null,'张江')" % mc
            # print sql2
            try:
                MySQL.execute_update(sql2)
            except mysql.connector.errors.IntegrityError:
                sql3 = "update enterprise_credit_info.dtjk_company_src set update_status=-1 where mc='%s'" % mc
                MySQL.execute_update(sql3)


def load_dtjk_nb_test():
    config = {'host': '172.16.0.102',
              'user': 'bigdata1',
              'password': 'aaBigDataZZ123$',
              'port': 3306,
              'database': 'ljzxdb',
              'charset': 'utf8mb4'
              }

    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    sql = "select CompanyName,MonitorDate from v_monitorcompany where MonitorDate in ('%s','%s','%s')" \
          % (
              str(int(TimeUtils.get_today()[:4]) - 1) + TimeUtils.get_today()[4:],
              str(int(TimeUtils.get_yesterday()[:4]) - 1) + TimeUtils.get_yesterday()[4:],
              str(int(TimeUtils.get_the_day_before_yesterday()[:4]) - 1) + TimeUtils.get_the_day_before_yesterday()[4:]
          )
    # print sql
    cursor.execute(sql)
    res = cursor.fetchall()
    for row in res:
        mc = row[0]
        monitor_date = str(row[1])
        monitor_date = str(int(monitor_date[:4]) + 1) + monitor_date[4:] + ' 00:00:00'
        # info(mc)
        if not mc.isdigit() and len(mc) > 1:
            sql_2 = u"""select last_update_time from enterprise_credit_info.nb where entname='%s' and ancheyear='2016'
                                    union all
                                    select last_update_time from enterprise_credit_info.gtnb where traName='%s' and ancheyear='2016'
                                    union all
                                    select last_update_time from enterprise_credit_info.sfcnb where farSpeArtName='%s' and ancheyear='2016'
                        """ % (mc, mc, mc)
            res_2 = MySQL.execute_query(sql_2)
            if len(res_2) == 0:
                sql_3 = u"replace into enterprise_credit_info.dtjk_company_src_nb(mc,update_status,last_update_time) " \
                        u"values('%s',-1,'%s')" % (mc, monitor_date)
                MySQL.execute_update(sql_3)


def load_dtjk_nb():
    config = {'host': '172.16.0.11',
              'user': 'bigdata1',
              'password': 'aaBigDataZZ123$',
              'port': 3306,
              'database': 'ljzxdb',
              'charset': 'utf8mb4'
              }

    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    sql = "select CompanyName,MonitorDate from v_monitorcompany where MonitorDate in ('%s','%s','%s')" \
          % (
              str(int(TimeUtils.get_today()[:4]) - 1) + TimeUtils.get_today()[4:],
              str(int(TimeUtils.get_yesterday()[:4]) - 1) + TimeUtils.get_yesterday()[4:],
              str(int(TimeUtils.get_the_day_before_yesterday()[:4]) - 1) + TimeUtils.get_the_day_before_yesterday()[4:]
          )
    # print sql
    cursor.execute(sql)
    res = cursor.fetchall()
    for row in res:
        mc = row[0]
        monitor_date = str(row[1])
        monitor_date = str(int(monitor_date[:4]) + 1) + monitor_date[4:] + ' 00:00:00'
        if not mc.isdigit() and len(mc) > 1:
            sql_2 = u"""select last_update_time from enterprise_credit_info.nb where entname='%s' and ancheyear='2016'
                        union all
                        select last_update_time from enterprise_credit_info.gtnb where traName='%s' and ancheyear='2016'
                        union all
                        select last_update_time from enterprise_credit_info.sfcnb where farSpeArtName='%s' and ancheyear='2016'
            """ % (mc, mc, mc)
            res_2 = MySQL.execute_query(sql_2)
            if len(res_2) == 0:
                sql_3 = u"replace into enterprise_credit_info.dtjk_company_src_nb(mc,update_status,last_update_time) " \
                        u"values('%s',-1,'%s')" % (mc, monitor_date)
                MySQL.execute_update(sql_3)
                # print sql_3


def load_dtjk_lsmc_src():
    global UPDATE_PERIOD
    config = {'host': '172.16.0.11',
              'user': 'bigdata1',
              'password': 'aaBigDataZZ123$',
              'port': 3306,
              'database': 'ljzxdb',
              'charset': 'utf8mb4'
              }

    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    sql = u'''select CompanyName,AreaName from v_monitorcompany where MonitorDate in ('%s','%s')''' % (
        str(int(TimeUtils.get_today()[:4]) - 1) + TimeUtils.get_today()[4:],
        str(int(TimeUtils.get_yesterday()[:4]) - 1) + TimeUtils.get_yesterday()[4:],
    )
    cursor.execute(sql)
    while True:
        res = cursor.fetchmany(1000)
        params = []
        for row in res:
            mc = row[0]
            province = row[1]
            if not mc.isdigit() and len(mc) > 1:
                params.append((mc, province))
        if params:
            insert_sql = u"insert ignore into enterprise_credit_info.lsmc_src " \
                         u"values(%s,-1,null, null,%s)"
            MySQL.execute_many_update(insert_sql, params)

        if len(res) < 1000:
            break

    sql_2 = '''
            insert ignore into enterprise_credit_info.lsmc_src
            select mc,-1,null,null,province from enterprise_credit_info.dtjk_company_src where update_status=0
            union all
            select mc,-1,null,null,province from enterprise_credit_info.dtjk_company_src_test where update_status=0
    '''
    MySQL.execute_update(sql_2)
    while True:
        res = cursor.fetchmany(1000)
        params = []
        for row in res:
            mc = row[0]
            province = row[1]
            if not mc.isdigit() and len(mc) > 1:
                params.append((mc, province))
        if params:
            insert_sql = u"insert ignore into enterprise_credit_info.lsmc_src " \
                         u"values(%s,-1,null, null,%s)"
            MySQL.execute_many_update(insert_sql, params)

        if len(res) < 1000:
            break

    sql_3 = '''
                UPDATE lsmc_src l, yyzz y
                SET l.xydm = y.xydm
                WHERE l.xydm is null and l.mc = y.mc;
            '''
    MySQL.execute_update(sql_3)


def load_dtjk_lsmc_src_test():
    global UPDATE_PERIOD
    config = {'host': '172.16.0.102',
              'user': 'bigdata1',
              'password': 'aaBigDataZZ123$',
              'port': 3306,
              'database': 'ljzxdb',
              'charset': 'utf8mb4'
              }

    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    sql = u'''select CompanyName,AreaName from v_monitorcompany where MonitorDate in ('%s','%s')''' % (
        str(int(TimeUtils.get_today()[:4]) - 1) + TimeUtils.get_today()[4:],
        str(int(TimeUtils.get_yesterday()[:4]) - 1) + TimeUtils.get_yesterday()[4:],
    )
    cursor.execute(sql)
    while True:
        res = cursor.fetchmany(1000)
        params = []
        for row in res:
            mc = row[0]
            province = row[1]
            if not mc.isdigit() and len(mc) > 1:
                params.append((mc, province))
        if params:
            insert_sql = u"insert ignore into enterprise_credit_info.lsmc_src " \
                         u"values(%s,-1,null, null,%s)"
            MySQL.execute_many_update(insert_sql, params)

        if len(res) < 1000:
            break
    sql_3 = '''
                    UPDATE lsmc_src l, yyzz y
                    SET l.xydm = y.xydm
                    WHERE l.xydm is null and l.mc = y.mc;
                '''
    MySQL.execute_update(sql_3)


def load_all_lsmc():
    sql = "select mc from law.dtjk_company_src"
    res = MySQL.execute_query(sql)
    mc_set = set([])
    for row in res:
        mc = row[0]
        mc_set.add(mc)
    sql2 = "select mc from enterprise_credit_info.dtjk_company_src_history"
    res2 = MySQL.execute_query(sql2)
    insert_params = []
    update_params = []
    replace_params = []
    for row in res2:
        mc = row[0].decode('utf-8')
        if mc in mc_set:
            update_params.append((mc,))
        else:
            insert_params.append((mc,))
        replace_params.append((mc,))
        # insert_params
    MySQL.execute_many_update(u"insert into law.dtjk_company_src values(%s,-1,null,null,'曾用名')", insert_params)
    MySQL.execute_many_update(u"update law.dtjk_company_src set update_status=-1 where mc=%s", update_params)
    MySQL.execute_many_update(u"replace into law.dtjk_company_shixin values(%s,-1,null,'曾用名')", replace_params)
    MySQL.execute_many_update(u"replace into law.dtjk_company_beizhixing values(%s,-1,null,'曾用名')", replace_params)
    MySQL.execute_many_update(u"replace into news.news_lsmc values(%s,-1,null,date(now()))", replace_params)


def load_today_input_lsmc():
    '''
    加载当日加入公司的历史名称（企查查数据显示有新名称的）
    :return:
    '''
    config = {'host': '172.16.0.102',
              'user': 'bigdata1',
              'password': 'aaBigDataZZ123$',
              'port': 3306,
              'database': 'ljzxdb',
              'charset': 'utf8mb4'
              }

    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    sql = u"select Company_Name from company_usedname where create_time>'%s 18:30:00'" % TimeUtils.get_yesterday()
    cursor.execute(sql)
    res = cursor.fetchall()
    # for row in res:
    #     mc = row[0]

    sql1 = u"insert into law.dtjk_company_src values(%s,-1,null,null,'曾用名') on duplicate key update update_status=-1"
    sql2 = u"insert into law.dtjk_company_shixin values(%s,-1,null,'曾用名') on duplicate key update update_status=-1"
    sql3 = u"insert into law.dtjk_company_beizhixing values(%s,-1,null,'曾用名') on duplicate key update update_status=-1"
    sql4 = u"insert into news.news_lsmc values(%s,-1,null,date(now())) on duplicate key update update_status=-1,add_date=date(now())"
    MySQL.execute_many_update(sql1, res)
    MySQL.execute_many_update(sql2, res)
    MySQL.execute_many_update(sql3, res)
    MySQL.execute_many_update(sql4, res)


if __name__ == '__main__':
    # load_zhangjiang()
    # info(u"张江数据加载完毕!")
    ERROR = False
    try:
        load_dtjk_lsmc_src()
        info(u'动态监控正式版历史名称加载完毕!')
    except Exception, e:
        info(traceback.format_exc(e))
        ERROR = True
    try:
        load_dtjk_lsmc_src_test()
        info(u'动态监控测试版历史名称加载完毕!')
    except Exception, e:
        info(traceback.format_exc(e))
        ERROR = True
    try:
        load_company()
        info(u"动态监控公司正式版数据加载完毕!")
    except Exception, e:
        info(traceback.format_exc(e))
        ERROR = True
    try:
        load_company_test()
        info(u"动态监控公司测试版数据加载完毕!")
    except Exception, e:
        info(traceback.format_exc(e))
        ERROR = True
    try:
        load_dtjk_nb()
        info(u'动态监控正式版年报待更新公司加载完毕!')
    except Exception, e:
        info(traceback.format_exc(e))
        ERROR = True
    try:
        load_dtjk_nb_test()
        info(u'动态监控测试版年报待更新公司加载完毕!')
    except Exception, e:
        info(traceback.format_exc(e))
        ERROR = True
    try:
        load_today_input_lsmc()
        info(u'动态监控测试版加入企业为曾用名加载完毕!')
    except Exception, e:
        info(traceback.format_exc(e))
        ERROR = True

    try:
        load_company_test_to_news()
        info(u'动态监控测试版舆情名称加载完毕!')
    except Exception, e:
        info(traceback.format_exc(e))
        ERROR = True
    try:
        load_company_to_news()
        info(u'动态监控正式版舆情名称加载完毕!')
    except Exception, e:
        info(traceback.format_exc(e))
        ERROR = True

    if ERROR:
        raise Exception(u'数据导入存在失败环节！')
