# coding=utf-8

import mysql.connector
import time


# config = {'host': 'localhost',
#           'user': 'likai',
#           'password': '1qaz@WSX3edc',
#           'port': 3306,
#           'database': 'tyc',
#           'charset': 'utf8'
#           }

config = {'host': '172.16.0.24',
          'user': 'bigdata1',
          'password': 'aaBigDataZZ123$',
          'port': 3306,
          'database': 'dataterminaldb2',
          'charset': 'utf8'
          }

connection = mysql.connector.connect(**config)
cursor = connection.cursor()


def execute_query(sql):
    global connection, cursor
    cursor.execute(sql)
    return cursor.fetchall()


def execute_update(sql):
    global connection, cursor
    cursor.execute(sql)
    commit()


def commit():
    global connection
    connection.commit()


def set_auto_commit_to(auto_commit):
    connection.autocommit = auto_commit


# if __name__ == '__main__':
#     while True:
#         test_sql = 'select * from  tyc.job_info'
#         res = execute_query(test_sql)
#         print res
#         # test_sql = "SHOW STATUS LIKE 'Qcache%'"
#         # res = execute_query(test_sql)
#         # print res[2]
#         time.sleep(2)
