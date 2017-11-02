# coding=utf-8

from pykafka import KafkaClient
import time
import pykafka
import traceback
from pykafka.exceptions import ProducerStoppedException
from pykafka.exceptions import ConsumerStoppedException


class KafkaAPI(object):

    client = None
    topic = None
    producer = None
    consumer = None
    topic_name = None
    group = None

    def __init__(self, topic_name):
        self.hosts = "hadoop10:9092,hadoop11:9092"
        self.zookeeper = "hadoop2:2181,hadoop1:2181,hadoop3:2181,hadoop4:2181,hadoop5:2181"
        self.topic_name = topic_name
        self.init_topic()

    def init_topic(self):
        # print u'初始化kafka集群连接 topic：%s' % self.topic_name
        self.client = KafkaClient(hosts=self.hosts)
        self.topic = self.client.topics[self.topic_name]

    def init_producer(self):
        """
        初始化producer
        :return:
        """
        # print u'初始化producer'
        self.producer = self.topic.get_sync_producer(max_request_size=5000000)

    def init_consumer(self, group=None):
        """
        初始化consumer
        :param group:
        :return:
        """
        # print u'初始化consumer'
        if group:
            self.group = group
        else:
            group = self.group
        self.consumer = self.topic.get_balanced_consumer(
            consumer_group=group,
            # consumer_timeout_ms=2*60*1000,
            auto_commit_enable=True,
            auto_commit_interval_ms=3*1000,
            num_consumer_fetchers=1,
            zookeeper_connect=self.zookeeper,
            compacted_topic=False,
            rebalance_max_retries=10
        )

    def send(self, message):
        """
        向broker发送消息,需要初始化producer之后才可调用
        :param message:
        :return:
        """
        if type(message) == unicode:
            message = message.encode('utf-8', 'ignore')
        try:
            self.producer.produce(message)
            return 0
        except ProducerStoppedException:
            del self.producer
            self.init_producer()
        except Exception, e:
            traceback.print_exc(e)
            # del self.client
            # del self.topic
            self.init_topic()
            try:
                self.producer.stop()
            except:
                pass
            del self.producer
            self.init_producer()
            if self.consumer:
                try:
                    self.consumer.stop()
                except:
                    pass
                del self.consumer
                self.init_consumer()
        return self.send(message)

    def fetch_one(self):
        """
        从broker获取一条消息,需要初始化consumer后才可调用
        如果指定时间内无法获取消息,返回None
        :return:
        """
        try:
            message = self.consumer.consume()
            # self.consumer.commit_offsets()
            return message
        except ConsumerStoppedException:
            del self.consumer
            self.init_consumer()
        except Exception, e:
            traceback.print_exc(e)
            # del self.client
            # del self.topic
            self.init_topic()
            if self.producer:
                try:
                    self.producer.stop()
                except:
                    pass
                del self.producer
                self.init_producer()
            try:
                self.consumer.stop()
            except:
                pass
            del self.consumer
            self.init_consumer()
        return self.fetch_one()

    def reset_offset(self):
        self.consumer.reset_offsets()

if __name__ == '__main__':
    kafka = KafkaAPI('GsOnline')
    kafka.init_consumer('gscrawlerresulttest')
    # print kafka.group
    kafka.reset_offset()
    # kafka.topic.partitions
    # print kafka.fetch_one()
    # while True:
    #     message = kafka.fetch_one()
    #     # print message.partition
    #     print message.value, message.offset



