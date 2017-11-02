# coding=utf-8

import pykafka
import MSSQL
from KafkaAPI import KafkaAPI
import time
import sys

producer = KafkaAPI('BackupPlanZhongShu')
producer.init_producer()

sql = "select * from DtjkSrc where data_type='%s' and update_status not in (0,1)" % u'工商'
res = MSSQL.execute_query(sql)
for r in res:
	mc = r[0] + '|' + r[1]+ '|' + r[4]+ '|' + r[5]+ '|' + str(r[6]) + '|' + 'UncrawledCompany' + '|' + str(long(time.time()*1000))
	producer.send(mc)
MSSQL.database_client_connection.close()



