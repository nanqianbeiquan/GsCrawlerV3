# coding=utf-8
from KafkaAPI import KafkaAPI
import json
import traceback
import time
from codecs import open
import uuid
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


class GsSrcCousumer(object):

    kafka = None
    searcher = None
    failed_times = 0

    def __init__(self):
        self.set_config()
        self.init_kafka()

    def set_config(self):
        """
        设置查询器和kafka队列参数
        示例
        self.searcher = LiaoNing()  # 因为kakfa 客户端需要从searcher中读取group和topic,因此一定要先生成searcher再生成kafka 客户端
        :return:
        """
        pass

    def init_kafka(self):
        """
        初始化kafka客户端
        :return:
        """
        if not self.searcher:
            print u"请先初始化 self.searcher!"
        self.kafka = KafkaAPI(self.searcher.topic)
        self.kafka.init_producer()
        self.kafka.init_consumer(self.searcher.group)

    def get_company_name(self):
        """
        从队列中获取未消费的公司名
        :return: 队列中未消费的公司名
        :rtype: unicode
        """
        try:
            print u'获取公司名...'
            message = self.kafka.fetch_one()
            if message:
                json_text = message.value.decode('utf-8', 'ignore')
                partition = message.partition.id
                print partition, json_text
                if json_text.startswith('{') and json_text.endswith('}'):
                    json_obj = json.loads(json_text)
                    company = json_obj['companyName']
                    return company
                else:
                    return json_text
            else:
                return None
        except Exception, e:
            traceback.print_exc(e)
            self.rebuild_kafka()
            return self.get_company_name()

    def rebuild_kafka(self):
        try:
            print u'关闭kafka'
            self.kafka.consumer.stop()
        except Exception, e2:
            print u'kafka关闭失败'
            traceback.print_exc(e2)
        print u'重现建立kafka连接'
        del self.kafka
        self.init_kafka()

    def run(self):
        """
        执行更新任务
        :return:
        """
        company_name = self.get_company_name()
        while company_name:
            # print u'更新 %s' % company_name
            try:
                self.searcher.submit_search_request(company_name)
                self.failed_times = 0
            except Exception, e:
                traceback.print_exc(e)
                print u'更新出错，放回更新队列'
                keyword = company_name.replace('(', u'`（').replace(')', u'）')
                self.searcher.delete_tag_a_from_db(keyword)
                self.kafka.send(company_name)
                self.failed_times += 1
                if self.failed_times == 50:
                    print u'连续失败50次,休眠5分钟退出程序'
                    time.sleep(300)
                    break
            company_name = self.get_company_name()
            # for i in range(4):
            #     if company_name:
            #         break
            #     self.rebuild_kafka()
            #     company_name = self.get_company_name()
        print u'更新完毕'

