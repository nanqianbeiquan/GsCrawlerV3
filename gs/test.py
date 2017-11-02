# coding=utf-8
import re
from KafkaAPI import KafkaAPI
import codecs

kafka = KafkaAPI('GsCrawlerOnline')
kafka.init_consumer('likaitest')
# kafka.consumer.reset_offsets()
# f = codecs.open('a.txt', 'a', 'utf-8')
while True:
    msg = kafka.fetch_one().value
    # print msg, type(msg)
    if msg:
        # print msg
        if '深圳市赢时通汽车服务有限公司' in msg:
            print msg

        #     f.write(msg.decode('utf-8','ignore')+'\n')
    else:
        break
# f.close()
