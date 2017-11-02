# coding=utf-8
import datetime
import time


def date_add(original, delta):
    """
    获取时间差
    :param original: 原始时间
    :param delta: 添加时间差后的时间
    :return:
    """
    # print type(time.strptime(original, '%Y-%m-%d'))
    return str(datetime.datetime.fromtimestamp(time.mktime(time.strptime(original, '%Y-%m-%d'))) + datetime.timedelta(days=delta))[:10]


def get_today():
    """
    获取当前日期
    :return: 格式化的日期
    :rtype: str
    """
    return str(datetime.date.today())


def get_yesterday():
    """
    获取昨天
    :return: 格式化的日期
    :rtype: str
    """
    return date_add(get_today(), -1)


def get_the_day_before_yesterday():
    """
    获取前天
    :return: 格式化的日期
    :rtype: str
    """
    return date_add(get_today(), -2)


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
    try:
        return time.strftime('%Y-%m-%d %X', time.localtime(ts/1000))
    except ValueError:
        return None

def get_date(ts):
    try:
        return time.strftime('%Y-%m-%d', time.localtime(ts / 1000))
    except ValueError:
        return None


# Sun Aug 28 2016 14:33:53 GMT+0800 (CST)
def get_cur_time_jiangsu():
    return time.strftime('%a %b %d %Y %X GMT+0800 (CST)',
                         time.localtime())


def format_nei_meng_gu(time_original):
    dt = datetime.datetime.strptime(time_original, '%b %d, %Y %I:%M:%S %p')
    return str(dt)


def get_ts(time_original):
    return time.mktime(time.strptime(time_original,'%Y-%m-%d'))

if __name__ == '__main__':
    print get_today()
    print get_yesterday()
    print get_the_day_before_yesterday()
    # print get_cur_ts_sec()
    # print get_cur_ts_mil()
    # print get_cur_time()
    # print get_cur_time_jiangsu()
    # print format_nei_meng_gu('Apr 15, 2010 12:00:00 AM')
    # print format_nei_meng_gu("Apr 21, 2016 12:00:00 AM")
    # print get_date(-2209190400000)


