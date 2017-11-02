# coding=utf-8

weight_arr = [1, 3, 9, 27, 19, 26, 16, 17, 20, 29, 25, 13, 8, 24, 10, 30, 28]
char_to_num = {
    '0': 0,
    '1': 1,
    '2': 2,
    '3': 3,
    '4': 4,
    '5': 5,
    '6': 6,
    '7': 7,
    '8': 8,
    '9': 9,
    'A': 10,
    'B': 11,
    'C': 12,
    'D': 13,
    'E': 14,
    'F': 15,
    'G': 16,
    'H': 17,
    'J': 18,
    'K': 19,
    'L': 20,
    'M': 21,
    'N': 22,
    'P': 23,
    'Q': 24,
    'R': 25,
    'T': 26,
    'U': 27,
    'W': 28,
    'X': 29,
    'Y': 30,
}
check_code_arr = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F',
                  'G', 'H', 'J', 'K', 'L', 'M', 'N', 'P', 'Q', 'R', 'T', 'U', 'W', 'X', 'Y', '0']


def check(code):
    """
    判断字符串是否为统一社会信用代码
    :param code:
    :return:
    """
    if not code or len(code) != 18:
        return False
    else:
        s = 0
        for i in range(17):
            c = code[i]
            num = char_to_num.get(c, None)
            if num is None:
                return False
            else:
                s += weight_arr[i] * num
        check_code = check_code_arr[31 - s % 31]
        return check_code == code[17]


if __name__ == '__main__':
    print check(u'913713015640982422')
