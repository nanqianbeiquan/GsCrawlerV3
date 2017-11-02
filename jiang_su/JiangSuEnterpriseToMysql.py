# coding=utf-8

import sys
import os
import time

import xlrd
import MySQLdb


reload(sys)
sys.setdefaultencoding('utf8')
'''feng yuanhua'''


class EnterpriseExcelReader(object):

    def __init__(self):
        self.mysql_conn()
        self.set_config()

    def set_config(self):
        self.province = u'江苏省'
        self.last_update_time = time.strftime('%Y-%m-%d %H:%M:%S')
        self.update_status = '-1'

    def mysql_conn(self):
        self.conn = MySQLdb.connect(host='172.16.0.76', port=3306, user='fengyuanhua', passwd='!@#qweASD',
                                    db='enterprise_credit_info', charset='utf8')
        self.cursor = self.conn.cursor()

    def data_to_mysql(self, sql, num, k1, n):
        try:
            self.cursor.execute(sql)
            self.conn.commit()
            num += 1
            data_nums = [num, k1]
        except Exception as e:
            print n+1, sql, e
            k1 += 1
            data_nums = [num, k1]
        return data_nums

    def excel_read(self):
        file_directory = sys.path[0] + '\ocr\\'
        filenames = os.listdir(file_directory)
        excel_names = [filename for filename in filenames if '.xls' in filename]
        all_num = 0
        k2 = 0
        for n in range(len(excel_names)):
            excel_path = file_directory + excel_names[n]
            excel = xlrd.open_workbook(excel_path, 'utf8')
            table = excel.sheet_by_name(u'江苏')
            rows = table.nrows
            k1 = 0
            num = 0
            for i in range(1, rows):
                row_val = table.row_values(i)
                field_keys = 'province,update_status,last_update_time,mc'
                vals = "'" + self.province.encode('utf8') + "','" + self.update_status.encode('utf8') + \
                       "','" + self.last_update_time + "','" + row_val[1].encode('utf8') + "'"
                sql = "insert into dtjk_company_src_old (" + field_keys + ") values (" + vals + ")"
                data_nums = reader.data_to_mysql(sql, num, k1, n)
                num = data_nums[0]
                k1 = data_nums[1]
            print str(n+1) + u'表插入' + str(num) + u'条'
            print str(n+1) + u'表重复' + str(k1) + u'条'
            k2 += k1
            all_num += num
        print self.province + u'一共插入' + str(all_num) + u'条'
        print self.province + u'一共失败' + str(k2) + u'条'


if __name__ == '__main__':
    reader = EnterpriseExcelReader()
    reader.excel_read()


