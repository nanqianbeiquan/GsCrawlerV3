# coding=utf-8

import MySQL
import codecs

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
# for line in codecs.open('/Users/likai/Downloads/oldmc.txt', 'r', 'gbk'):
#     mc = line.strip()
for row in res2:
    mc = row[0].decode('utf-8')
    if len(mc) > 4:
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