# coding=utf-8
from PIL import Image
import os
import numpy
import requests
from io import BytesIO

RECOVERY_ARR = (
    (-157, -58),
    (-145, -58),
    (-265, -58),
    (-277, -58),
    (-181, -58),
    (-169, -58),
    (-241, -58),
    (-253, -58),
    (-109, -58),
    (-97, -58),
    (-289, -58),
    (-301, -58),
    (-85, -58),
    (-73, -58),
    (-25, -58),
    (-37, -58),
    (-13, -58),
    (-1, -58),
    (-121, -58),
    (-133, -58),
    (-61, -58),
    (-49, -58),
    (-217, -58),
    (-229, -58),
    (-205, -58),
    (-193, -58),
    (-145, 0),
    (-157, 0),
    (-277, 0),
    (-265, 0),
    (-169, 0),
    (-181, 0),
    (-253, 0),
    (-241, 0),
    (-97, 0),
    (-109, 0),
    (-301, 0),
    (-289, 0),
    (-73, 0),
    (-85, 0),
    (-37, 0),
    (-25, 0),
    (-1, 0),
    (-13, 0),
    (-133, 0),
    (-121, 0),
    (-49, 0),
    (-61, 0),
    (-229, 0),
    (-217, 0),
    (-193, 0),
    (-205, 0)
)


def recovery_img(ori_img):
    im_list_upper = []
    im_list_down = []

    for location in RECOVERY_ARR:

        if location[1] == -58:
            pass
            im_list_upper.append(ori_img.crop((abs(location[0]), 58, abs(location[0]) + 10, 166)))
        if location[1] == 0:
            pass
            im_list_down.append(ori_img.crop((abs(location[0]), 0, abs(location[0]) + 10, 58)))
    rec_img = Image.new('RGB', (260, 116))
    x_offset = 0
    for im in im_list_upper:
        rec_img.paste(im, (x_offset, 0))
        x_offset += im.size[0]
    x_offset = 0
    for im in im_list_down:
        rec_img.paste(im, (x_offset, 58))
        x_offset += im.size[0]
    return rec_img


def download_img(img_url):
    r = requests.get(img_url)
    return Image.open(BytesIO(r.content))


def contains_negative_block(m):
    for x in range(m.shape[0]-3):
        for y in range(m.shape[1]-3):
            flag = True
            for i in range(3):
                for j in range(3):
                    if m[x+i,y+j] != -1:
                        flag = False
            if flag:
                return True
    return False


def remove_positive_block(m):
    tmp_s0 = set()
    for x in range(m.shape[0]):
        # print 'x', x
        for y in range(m.shape[1]):
            tmp_s1 = set()
            tmp_s2 = set()
            if m[x, y] == 1 and (x, y) not in tmp_s0:
                tmp_s0.add((x, y))
                tmp_s1.add((x, y))
                tmp_s2.add((x, y))
            remove_flag = True

            while len(tmp_s1) > 0:
                _x, _y = tmp_s1.pop()
                _lx = range(max(-_x, -1), min(m.shape[0] - _x - 1, 1) + 1)
                _ly = range(max(-_y, -1), min(m.shape[1] - _y - 1, 1) + 1)
                for i in _lx:
                    for j in _ly:
                        if (i != 0 or j != 0) and (_x+i, _y+j) not in tmp_s2:
                            if m[_x+i, _y+j] == 1:
                                tmp_s0.add((_x+i, _y+j))
                                tmp_s1.add((_x+i, _y+j))
                                tmp_s2.add((_x+i, _y+j))
                            elif m[_x+i, _y+j] == -1:
                                remove_flag = False
                # if len(tmp_s1) == 0:
                #     geetest
            if not remove_flag:
                for t in tmp_s2:
                    m[t[0], t[1]] = 2
    for x in range(m.shape[0]):
        for y in range(m.shape[1]):
            if m[x, y] == 1:
                m[x, y] = 0
            elif m[x, y] == 2:
                m[x, y] = 1


def get_slice_offset(slice_img):
    grey_img = slice_img.convert('L')
    pixels = grey_img.load()
    bg_value = pixels[0, 0]
    slice_left = -1
    threshold = 20
    for x in range(grey_img.width):
        cnt1 = 0
        for y in range(grey_img.height):
            if abs(pixels[x, y]-bg_value) > 50:
                cnt1 += 1
        if cnt1 >= threshold and slice_left == -1:
            slice_left = x
            break
    return slice_left


def get_offset(bg_img_recovery, fullbg_img_recovery, slice_img):

    bg_left = -1
    bg_bottom = -1
    bg_top = -1

    slice_left = get_slice_offset(slice_img)
    bg_grey_img = bg_img_recovery.convert('L')
    fullbg_grey_img = fullbg_img_recovery.convert('L')

    bg_pixels = bg_grey_img.load()
    fullbg_pixels = fullbg_grey_img.load()

    sum_dif1 = 0
    _cnt1 = 0
    sum_dif2 = 0
    _cnt2 = 0
    for y in range(bg_img_recovery.height):
        for x in range(bg_img_recovery.width):
            # z = abs(fullbg_pixels[x, y] - bg_pixels[x, y])
            z = fullbg_pixels[x, y] - bg_pixels[x, y]
            if z >= 10:
                _cnt1 += 1
                sum_dif1 += z
            if z <= -10:
                sum_dif2 += z
                _cnt2 += 1

    threshold1 = sum_dif1 / (_cnt1 * 1.0)
    threshold2 = sum_dif2 / (_cnt2 * 2.0)
    # print 'threshold', threshold1, sum_dif1, _cnt1

    new_img = numpy.zeros((bg_img_recovery.width, bg_img_recovery.height), dtype=int)

    for y in range(bg_img_recovery.height):
        for x in range(bg_img_recovery.width):
            z = fullbg_pixels[x, y] - bg_pixels[x, y]
            if z > threshold1:
                new_img[x, y] = 1
                # print '1',
            elif z < threshold2:
                new_img[x, y] = -1
                # print '0',
                #     else:
                #         print '-',
                # print
    # print '\n'+'='*600+'\n'
    if contains_negative_block(new_img):
        remove_positive_block(new_img)
    for y in range(new_img.shape[1]):
        cnt = 0
        for x in range(new_img.shape[0]):
            if new_img[x, y] != 0:
                cnt += 1
        if cnt >= 25:
            bg_top = y
            break

    for y1 in range(new_img.shape[1]):
        y = new_img.shape[1] - (y1 + 1)
        cnt = 0
        for x in range(new_img.shape[0]):
            if new_img[x, y] != 0:
                cnt += 1
        if cnt >= 25:
            bg_bottom = y
            break
    # print self.bg_top, self.bg_bottom
    for x in range(new_img.shape[0]):
        cnt = 0
        for y in [bg_top, bg_top + 1, bg_top + 2, bg_top + 3, bg_top + 4,
                  bg_bottom, bg_bottom - 1, bg_bottom - 2, bg_bottom - 3, bg_bottom - 4]:
            if new_img[x, y] != 0:
                cnt += 1
        # print x, cnt
        if cnt >= 4:
            bg_left = x
            break
    # print self.bg_left
    offset = bg_left - slice_left
    return offset


def get_distance(bg_img, full_bg_img, slice_img):
    full_bg_img_recovery = recovery_img(full_bg_img)
    bg_img_recovery = recovery_img(bg_img)
    # slice_img.save('slice.jpg')
    # full_bg_img_recovery.save('full_bg_img_recovery.jpg')
    # bg_img_recovery.save('bg_img_recovery.jpg')
    return get_offset(bg_img_recovery=bg_img_recovery, fullbg_img_recovery=full_bg_img_recovery, slice_img=slice_img)


if __name__ == '__main__':
    print get_distance(
                       download_img('http://static.geetest.com/pictures/gt/26ebd36a0/bg/e53fd5ca0.jpg'),
                       download_img('http://static.geetest.com/pictures/gt/26ebd36a0/26ebd36a0.jpg'),
                       download_img('http://static.geetest.com/pictures/gt/26ebd36a0/slice/e53fd5ca0.png')
    )
