# coding=utf-8

status_dict = {
    u'存续': 1, u'存续（在营、开业、在册）': 1, u'在业': 1, u'开业': 1,u'已开业': 1, u'在营':1, u'在营（开业）': 1,\
    u'在营（开业）企业': 1, u'吊销，未注销':2, u'吊销未注销': 2,u'吊销,未注销':2,u'吊销':3, u'吊销企业': 3,u'已吊销': 3,\
     u'拟注销': 4, u'注销': 5, u'已注销':5, u'注销企业': 5, u'吊销,已注销': 6,u'吊销，已注销': 6,u'注吊销': 6,\
    u'吊销后注销': 6,u'清算中': 7,u'其他': 8, u'个体转企业': 9, u'迁出': 10,u'迁移异地': 10, u'市外迁出': 10,u'已迁出企业': 10,\
    u'停业': 11,u'停业（个体工商户使用': 11,u'撤销登记': 12, u'撤消登记': 12, u'撤销': 12, u'待迁入': 13, \
    u'经营期限届满': 14,u'不明': 15,u'登记成立': 16,u'正常': 17,u'非正常户': 18,'2': 19,}


def compare_status(status_1, status_2):
    global status_dict
    val_1 = status_dict.get(status_1, 100)
    val_2 = status_dict.get(status_2, 100)
    if val_1 > val_2:
        return -1
    elif val_1 < val_2:
        return 1
    else:
        return 0


if __name__ == '__main__':
    print compare_status(u'存续（在营、开业、在册）', None)
