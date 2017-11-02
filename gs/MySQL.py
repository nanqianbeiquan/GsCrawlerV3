# coding=utf-8

import mysql.connector
import time


config = {'host': '172.16.0.76',
          'user': 'likai',
          'password': '1qaz@WSX3edc',
          'port': 3306,
          'database': 'enterprise_credit_info',
          'charset': 'utf8'
          }

# config = {'host': '192.168.1.28',
#           'user': 'bigdata1',
#           'password': 'aaBigDataZZ123$',
#           'port': 3306,
#           'database': 'dataterminaldb',
#           'charset': 'utf8'
#           }

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


def execute_many_update(sql, args):
    global connection, cursor
    cursor.executemany(sql, args)
    commit()


def commit():
    global connection
    connection.commit()


def set_auto_commit_to(auto_commit):
    connection.autocommit = auto_commit


if __name__ == '__main__':
    while True:
        test_sql = 'select date(now())'
        res = execute_query(test_sql)
        import datetime
        print res[0][0] == datetime.date.today()
        break
