# coding=utf-8

import mysql.connector
import time
import TimeUtils


# config = {'host': '192.168.0.110',
#           'user': 'likai',
#           'password': '1qaz@WSX3edc',
#           'port': 3306,
#           'database': 'tyc',
#           'charset': 'utf8'
#           }

config = {'host': '172.16.0.76',
          'user': 'likai',
          'password': '1qaz@WSX3edc',
          'port': 3306,
          'database': 'law',
          'charset': 'utf8mb4'
          }

connection = mysql.connector.connect(**config)
cursor = connection.cursor()


def execute_query(sql):
    global connection, cursor
    try:
        cursor.execute(sql)
        return cursor.fetchall()
    except mysql.connector.errors.OperationalError:
        print u'mysql连接断开,重新连接...'
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        return execute_query(sql)


def execute_update(sql, params=()):
    global connection, cursor
    try:
        cursor.execute(sql, params)
        commit()
    except mysql.connector.errors.OperationalError:
        print u'mysql连接断开,重新连接...'
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        execute_update(sql, params)


def execute_many_update(sql, args):
    cursor.executemany(sql, args)
    commit()


def execute_update_without_commit(sql):
    global connection, cursor
    cursor.execute(sql)


def commit():
    global connection
    connection.commit()


def set_auto_commit_to(auto_commit):
    connection.autocommit = auto_commit


if __name__ == '__main__':
    res = execute_query("select date(now())")
    print str(res[0][0]) == TimeUtils.get_today()


