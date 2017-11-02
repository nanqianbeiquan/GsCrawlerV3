# coding=utf-8
from KafkaAPI import KafkaAPI
import json
import traceback
from Crawler import GsCrawler
from ProxyConf import key1 as app_key
import MSSQL
from Searcher import delete_tag_a_from_db
# from zhe_jiang.ZheJiangSearcherQW import ZheJiangSearcherQW
# from bei_jing.BeiJingQW import BeiJingQW


class UpdateNew(object):

    crawler = GsCrawler()
    kafka = None
    failed_times = 0
    failed_pool = []

    def __init__(self):
        self.init_kafka()
        self.crawler.set_app_key(app_key)  # 使用key1
        # self.crawler.crawler_class_dict[u'浙江省'] = ZheJiangSearcherQW
        # self.crawler.crawler_class_dict[u'北京市'] = BeiJingQW
        self.fill_failed_pool()

    def fill_failed_pool(self):
        sql = "select * from GsSrc.dbo.company_pool where datediff(second,add_time,getdate())>=60"
        res = MSSQL.execute_query(sql)
        for r in res:
            company_name = r[0]
            province = r[1]
            self.failed_pool.append((company_name, province))
            delete_from_company_pool(company_name, province)

    def init_kafka(self):
        """
        初始化kafka客户端
        :return:
        """
        self.kafka = KafkaAPI('NewRegisteredCompany')
        self.kafka.init_producer()
        self.kafka.init_consumer('Crawler')

    def get_company_province(self):
        """
        从队列中获取未消费的公司名
        :return: 队列中未消费的公司名
        :rtype: unicode
        """
        if len(self.failed_pool) > 0:
            ele = self.failed_pool.pop()
            return ele
        else:
            message = self.kafka.fetch_one()
            if message:
                json_text = message.value.decode('utf-8', 'ignore')
                partition = message.partition.id
                offset = message.offset
                json_obj = json.loads(json_text)
                company = json_obj['companyName']
                province = json_obj['province']
                print partition, offset, company
                return company, province
            else:
                return None, None

    def run(self):
        """
        执行更新任务
        :return:
        """
        company_name, province = self.get_company_province()
        while company_name:
            save_into_company_pool(company_name, province)
            print u'更新 %s %s' % (company_name, province)
            try:
                self.crawler.crawl(keyword=company_name, province=province)
                self.failed_times = 0
            except Exception, e:
                traceback.print_exc(e)
                print u'更新出错，放回更新队列'
                keyword = company_name.replace('(', u'`（').replace(')', u'）')
                delete_tag_a_from_db(keyword)
                self.kafka.send(json.dumps({'companyName': company_name, 'province': province}))

                self.failed_times += 1
                if self.failed_times == 50:
                    print u'连续失败50次,退出程序'
                    break
            delete_from_company_pool(company_name, province)
            company_name, province = self.get_company_province()
        print u'更新完毕'


def save_into_company_pool(company_name, province):
    sql_1 = "select * from GsSrc.dbo.company_pool where company_name='%s' and province='%s'" % (company_name, province)
    res_1 = MSSQL.execute_query(sql_1)
    if len(res_1) == 0:
        sql_2 = "insert into GsSrc.dbo.company_pool values('%s','%s', getDate())" % (company_name, province)
        MSSQL.execute_update(sql_2)


def delete_from_company_pool(company_name, province):
    sql = "delete from GsSrc.dbo.company_pool where company_name='%s' and province='%s'" % (company_name, province)
    MSSQL.execute_update(sql)

if __name__ == '__main__':
    job = UpdateNew()
    job.run()
