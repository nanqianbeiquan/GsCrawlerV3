# coding=utf-8

from UpdateNew import UpdateNew
from KafkaAPI import KafkaAPI
from ProxyConf import key2 as app_key


class UpdateNewLockId(UpdateNew):

    def __init__(self):
        super(UpdateNewLockId, self).__init__()

    def init_kafka(self):
        """
        初始化kafka客户端
        :return:
        """
        self.kafka = KafkaAPI('NewRegisteredCompanyLockId')
        self.kafka.init_producer()
        self.kafka.init_consumer('Crawler')

if __name__ == '__main__':
    job = UpdateNewLockId()
    job.run()
