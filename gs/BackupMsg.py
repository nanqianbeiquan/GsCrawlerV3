# coding=utf-8

from pykafka import KafkaClient
import datetime
from codecs import open
import os
import sys
import time


class BackupMsg(object):

    hosts = "hadoop10:9092,hadoop11:9092"
    zookeeper = "hadoop2:2181,hadoop1:2181,hadoop3:2181,hadoop4:2181,hadoop5:2181"
    group = 'backup'
    topic_name = None
    client = None
    topic = None
    consumer = None
    f_out = None
    cur_dt = None
    cur_min = None
    cnt = 0

    def __init__(self, topic_name):
        self.topic_name = topic_name
        self.init_kafka()

    def init_kafka(self):
        self.client = KafkaClient(hosts=self.hosts)
        self.topic = self.client.topics[self.topic_name]
        self.consumer = self.topic.get_balanced_consumer(
            consumer_group=self.group,
            # consumer_timeout_ms=2*60*1000,
            auto_commit_enable=True,
            # auto_commit_interval_ms=1*1000,
            num_consumer_fetchers=1,
            zookeeper_connect=self.zookeeper,
            compacted_topic=False,
            rebalance_max_retries=10
        )

    def save_text(self, text):
        dt = str(datetime.date.today())
        if dt != self.cur_dt:
            if self.f_out:
                self.f_out.close()
            parent_dir = 'data/%s' % dt
            if not os.path.exists(parent_dir):
                os.mkdir(parent_dir)
            self.f_out = open(os.path.join(parent_dir, self.topic_name + '_' + str(int(time.time()))), 'w', 'utf-8', 'ignore')
        self.f_out.write(text+'\n')
        self.cur_dt = dt

    def run(self):
        try:
            for msg in self.consumer:
                text = msg.value.decode('utf-8', 'ignore')
                self.save_text(text)
                self.cnt += 1
                minute = time.localtime().tm_min
                if minute != self.cur_min:
                    print '%s -> %d' % (time.strftime('%Y-%m-%d %X', time.localtime()), self.cnt)
                self.cur_min = minute
        except:
            print u'kafka连接断开，休眠60秒后重新连接'
            time.sleep(60)
            try:
                self.consumer.stop()
            except:
                pass
            del self.consumer
            del self.topic
            del self.client
            self.init_kafka()
            self.run()


def get_args():
    args = dict()
    for arg in sys.argv:
        kv = arg.split('=')
        if len(kv) == 2:
            k = kv[0]
            v = kv[1]
            args[k] = v
    return args

if __name__ == '__main__':
    args_dict = get_args()
    topic = args_dict['topic']
    job = BackupMsg(topic)
    job.run()
