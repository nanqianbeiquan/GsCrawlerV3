# coding=utf-8

import MSSQL
from KafkaAPI import KafkaAPI
import pyodbc


def load_from_kafka(topic_name):

    kafka = KafkaAPI(topic_name)
    consumer = kafka.topic.get_balanced_consumer(
        consumer_group='Crawler',
        consumer_timeout_ms=30*1000,
        auto_commit_enable=True,
        auto_commit_interval_ms=3 * 1000,
        num_consumer_fetchers=1,
        zookeeper_connect=kafka.zookeeper,
        compacted_topic=False,
        rebalance_max_retries=10
    )
    i = 0
    for msg in consumer:
        company_name = msg.value.decode('utf-8', 'ignore')\
            .replace('(', u'（')\
            .replace(')', u'）')\
            .replace(' ', '')\
            .replace("'", '')\
            .replace('?', '')\
            .replace(u'？', '')
        # print '->', msg.partition.id, company_name
        if '.0' in company_name:
            continue
        sql = "insert into %s(mc,update_status) values('%s',-1)" % (topic_name, company_name)
        try:
            MSSQL.execute_update_without_commit(sql)
        except pyodbc.IntegrityError:
            pass
        i += 1
        if i % 100 == 0:
            print 'commit...'
            MSSQL.commit()
            print '-> ', i


if __name__ == '__main__':
    load_from_kafka('GsSrc22')

