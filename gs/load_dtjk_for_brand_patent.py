# coding=utf-8
import MySQL
import MSSQL
import json
import pyodbc
import Logger

LOG_NAME = u'为商标专利导入动态监控待更新数据'


def info(msg):
    global LOG_NAME
    Logger.write(msg, LOG_NAME, True)

cnt = 0
data_type_list = [u'商标', u'专利']

sql_0 = "delete from GsSrc.dbo.DtjkSrc where source='%s' and data_type in ('%s') and update_status not in (-2, -1)" % (u'动态监控', "','".join(data_type_list))
MSSQL.execute_update(sql_0)

sql = "select * from monitortodaycompany"
res = MySQL.execute_query(sql)

for row in res:
    cnt += 1
    if cnt % 100 == 0:
        info('cnt: %d' % cnt)
    row2 = [unicode(val) for val in row]
    mc = row2[1]
    province = row2[2]
    for data_type in data_type_list:
        sql2 = "insert into GsSrc.dbo.DtjkSrc(mc,province,update_status,last_update_time,source,data_type) " \
               "values('%s','%s',-1,getDate(),'%s','%s')" % (mc, province, u'动态监控', data_type)
        # print sql2
        try:
            MSSQL.execute_update_without_commit(sql2)
        except pyodbc.IntegrityError:
            print sql2
MSSQL.commit()
info(u'动态监控公司总数量:%d' % cnt)
info(u'动态监控公司导入成功!')


