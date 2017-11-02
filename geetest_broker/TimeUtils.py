# coding=utf-8
import datetime
import time


def get_today():
    """
    获取当前日期
    :return: 格式化的日期
    :rtype: str
    """
    return str(datetime.date.today())


def get_cur_ts_sec():
    """
    获取当前时间戳,单位:秒
    :return: 秒为单位的当前时间戳
    :rtype: str
    """
    return str(int(time.time()))


def get_cur_ts_mil():
    """
    获取当前时间戳,单位:毫秒
    :return: 毫秒为单位的当前时间戳
    :rtype: str
    """
    return str(long(time.time()*1000))


def get_cur_time():
    """
    获取当前格式化时间
    :return: 格式化的时间
    :rtype: str
    """
    return time.strftime('%Y-%m-%d %X', time.localtime())


def get_time(ts):
    return time.strftime('%Y-%m-%d %X', time.localtime(ts/1000))


def get_date(ts):
    return time.strftime('%Y-%m-%d', time.localtime(ts / 1000))


# Sun Aug 28 2016 14:33:53 GMT+0800 (CST)
def get_cur_time_jiangsu():
    return time.strftime('%a %b %d %Y %X GMT+0800 (CST)',
                         time.localtime())


def format_nei_meng_gu(time_original):
    dt = datetime.datetime.strptime(time_original, '%b %d, %Y %I:%M:%S %p')
    return str(dt)

if __name__ == '__main__':
    print get_today()
    print get_cur_ts_sec()
    print get_cur_ts_mil()
    print get_cur_time()
    print get_cur_time_jiangsu()
    print format_nei_meng_gu('Apr 15, 2010 12:00:00 AM')
    print format_nei_meng_gu("Apr 21, 2016 12:00:00 AM")
    print get_date(1454601600000)

