# coding=utf-8


class StatusCodeException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class NotFoundException(Exception):
    def __init__(self, value=u"详情不存在"):
        self.value = value

    def __str__(self):
        return repr(self.value)


class GeetestTrailException(Exception):
    def __init__(self, value=u"连续多次滑动轨迹有误"):
        self.value = value

    def __str__(self):
        return repr(self.value)


class UnknownColumnException(Exception):
    def __init__(self, mc, col):
        self.mc = mc
        self.col = col

    def __str__(self):
        return u'%s存在未知列名：%s' % (self.mc, self.value)
