# coding=utf-8

import MySQL
import random
import GeetestJS


# trail_arr_text_list = []
#
#
# def load_my_trails():
#     global trail_arr_text_list
#     sql = "select * from temp.geetest_training where result='success'"
#     res = MySQL.execute_query(sql)
#     for row in res:
#         trail_arr_text = row[1]
#         trail_arr_text_list.append(trail_arr_text)
#     return trail_arr_text_list
#
# load_my_trails()


def get_trali_arr(distance):
    # global trail_arr_text_list
    sql = '''
        select trail_arr FROM
        (
        select trail_arr from enterprise_credit_info.geetest_training
        where abs(distance-%d)=
        (
        select min(abs(distance-%d)) from enterprise_credit_info.geetest_training
        ) order by rand()
        ) a limit 1
        ''' % (distance, distance)
    # sql = '''
    #        select * FROM
    #        (
    #        select * from temp.geetest_training
    #        where distance=%d
    #        order by rand()
    #        ) a limit 1
    #        ''' % distance
    # print sql
    res = MySQL.execute_query(sql)
    if len(res) == 0:
        print sql
    origin_trail_arr_text = res[0][0]
    point_list = origin_trail_arr_text.split('|')
    new_point_list = []
    origin_distance = int(point_list[-1].split(',')[0])
    i = 0
    for point in point_list:
        x, y, t = point.split(',')
        if origin_distance != distance:
            _x = int(int(x) * (distance + .0) / origin_distance)
        else:
            _x = int(x)
        _y = int(y)
        _t = int(t)

        rand_1 = random.randint(1, 10)
        if 1 < i < len(point_list) - 4:
            rand_2 = random.randint(-1, 1)
            if rand_1 == 1 and int(x) + rand_2 > 0:
                _x = int(x) + rand_2
                _t = int(t) + rand_2
            elif rand_1 == 2:
                _y = int(y) + rand_2

        # rand_1 = random.randint(1, 3)
        # if 1 < i < len(point_list)-4:
        #     if rand_1 == 1:
        #         # rand_2 = random.randint(1, 4)
        #         rand_3 = random.randint(1, 10)
        #         if rand_3 == 3:
        #             _x = int(x) + random.randint(-1, 1)
        #             _t = int(t) + random.randint(-1, 1)
        #         elif rand_3 == 1:
        #             _y = int(y) + random.randint(-1, 1)
                # elif rand_3 == 2:
                #     _t = int(t) + random.randint(-1, 1)
        new_point_list.append([_x, _y, _t])
        i += 1
    new_point_list[-1][0] = distance
    # print new_point_list
    return new_point_list


if __name__ == "__main__":
    trail_arr = get_trali_arr(103)
    a = GeetestJS.get_a(trail_arr)
    print a
