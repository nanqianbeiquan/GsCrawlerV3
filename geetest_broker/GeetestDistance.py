# coding=utf-8
from PIL import Image
import os
import numpy


class GeetestDistance(object):

    recovery_arr = (
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

    slice_left = -1
    slice_right = -1
    slice_bottom = -1
    slice_top = -1

    slice_width = -1
    slice_height = -1

    bg_left = -1
    bg_right = -1
    bg_bottom = -1
    bg_top = -1

    def __init__(self, bg_path, fullbg_path, slice_path):
        self.bg_recovery_path = bg_path.replace('.jpg', '_recovery.jpg')
        self.fullbg_recovery_path = fullbg_path.replace('.jpg', '_recovery.jpg')
        self.slice_path = slice_path
        self.recovery_image(bg_path, self.bg_recovery_path)
        self.recovery_image(fullbg_path, self.fullbg_recovery_path)

    def recovery_image(self, image_path, image_recovery_path):
        im = Image.open(image_path)

        im_list_upper = []
        im_list_down = []

        for location in self.recovery_arr:

            if location[1] == -58:
                pass
                im_list_upper.append(im.crop((abs(location[0]), 58, abs(location[0])+10, 166)))
            if location[1] == 0:
                pass
                im_list_down.append(im.crop((abs(location[0]), 0, abs(location[0])+10, 58)))
        new_im = Image.new('RGB', (260, 116))
        x_offset = 0
        for im in im_list_upper:
            new_im.paste(im, (x_offset, 0))
            x_offset += im.size[0]

        x_offset = 0
        for im in im_list_down:
            new_im.paste(im, (x_offset, 58))
            x_offset += im.size[0]
        # Image
        new_im.save(image_recovery_path)
        pass

    def get_slice_offset(self):
        slice_img = Image.open(self.slice_path)
        # slice_rgb_pixels = slice_img.convert('RGB').load()
        grey_img = slice_img.convert('L')
        pixels = grey_img.load()
        bg_value = pixels[0, 0]
        self.slice_top = -1
        self.slice_bottom = -1
        self.slice_left = -1
        self.slice_right = -1
        threshold = 20
        for x in range(grey_img.width):
            cnt1 = 0
            for y in range(grey_img.height):
                if abs(pixels[x, y]-bg_value) > 50:
                    cnt1 += 1
            if cnt1 >= threshold and self.slice_left == -1:
                self.slice_left = x
                break
        for x1 in range(grey_img.width):
            cnt = 0
            x = grey_img.width - (x1+1)
            for y in range(grey_img.height):
                if abs(pixels[x, y]-bg_value) > 50:
                    cnt += 1
            if cnt >= threshold and self.slice_right == -1:
                self.slice_right = x
                break
        for y in range(grey_img.height):
            cnt1 = 0
            for x in range(grey_img.width):
                if abs(pixels[x, y]-bg_value) > 50:
                    cnt1 += 1
            if cnt1 >= threshold and self.slice_top == -1:
                self.slice_top = y
                break
        for y1 in range(grey_img.height):
            y = grey_img.height - (y1+1)
            cnt = 0
            for x in range(grey_img.width):
                if abs(pixels[x, y]-bg_value) > 50:
                    cnt += 1
            if cnt >= threshold and self.slice_bottom == -1:
                self.slice_bottom = y
                break
        # print (self.slice_left, self.slice_right), (self.slice_top, self.slice_bottom)
        self.slice_width = self.slice_right - self.slice_left + 1
        self.slice_height = self.slice_bottom - self.slice_top + 1

    def get_offset(self):
        self.get_slice_offset()
        bg_img = Image.open(self.bg_recovery_path)
        fullbg_img = Image.open(self.fullbg_recovery_path)
        bg_grey_img = bg_img.convert('L')
        fullbg_grey_img = fullbg_img.convert('L')

        bg_pixels = bg_grey_img.load()
        fullbg_pixels = fullbg_grey_img.load()

        sum_dif1 = 0
        _cnt1 = 0
        sum_dif2 = 0
        _cnt2 = 0
        for y in range(bg_img.height):
            for x in range(bg_img.width):

                # z = abs(fullbg_pixels[x, y] - bg_pixels[x, y])
                z = fullbg_pixels[x, y] - bg_pixels[x, y]
                if z >= 10:
                    _cnt1 += 1
                    sum_dif1 += z
                if z <= -10:
                    sum_dif2 += z
                    _cnt2 += 1

        threshold1 = sum_dif1/(_cnt1*1.0)
        '''
         threshold2 = sum_dif2 / (_cnt2 * 2.0)
            ZeroDivisionError: float division by zero
        '''
        threshold2 = sum_dif2 / (_cnt2 * 2.0)
        # print 'threshold', threshold1, sum_dif1, _cnt1

        new_img = numpy.zeros((bg_img.width, bg_img.height), dtype=int)

        for y in range(bg_img.height):
            for x in range(bg_img.width):
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
                self.bg_top = y
                break

        for y1 in range(new_img.shape[1]):
            y = new_img.shape[1] - (y1+1)
            cnt = 0
            for x in range(new_img.shape[0]):
                if new_img[x, y] != 0:
                    cnt += 1
            if cnt >= 25:
                self.bg_bottom = y
                break
        # print self.bg_top, self.bg_bottom
        for x in range(new_img.shape[0]):
            cnt = 0
            for y in [self.bg_top, self.bg_top+1, self.bg_top+2, self.bg_top+3, self.bg_top+4,
                      self.bg_bottom, self.bg_bottom-1, self.bg_bottom-2, self.bg_bottom-3, self.bg_bottom-4]:
                if new_img[x, y] != 0:
                    cnt += 1
            # print x, cnt
            if cnt >= 4:
                self.bg_left = x
                break
        # print self.bg_left
        offset = self.bg_left - self.slice_left
        # for y in range(self.bg_top, self.bg_bottom+1):
        #     for x in range(new_img.shape[0]):
        #         if new_img[x, y] == 1:
        #         if new_img[x, y] == 1:
        #             print '1',
        #         elif new_img[x, y] == -1:
        #             print '0',
        #         else:
        #             print '-',
        #     print
        # print '\n' + str((self.bg_left, self.slice_left, offset))+'\n'+'=' * 600 + '\n'
        os.remove(self.bg_recovery_path)
        os.remove(self.fullbg_recovery_path)
        return offset


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
                # if x == 208:
                #     print x, y, len(tmp_s1)
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
                #     break
            if not remove_flag:
                for t in tmp_s2:
                    m[t[0], t[1]] = 2
    for x in range(m.shape[0]):
        for y in range(m.shape[1]):
            if m[x, y] == 1:
                m[x, y] = 0
            elif m[x, y] == 2:
                m[x, y] = 1


if __name__ == '__main__':
    bg_path = os.path.join(os.path.dirname(__file__), '../temp/bg.jpg')
    slice_path = os.path.join(os.path.dirname(__file__), '../temp/slice.jpg')
    fullbg_path = os.path.join(os.path.dirname(__file__), '../temp/fullbg.jpg')
    gip = GeetestDistance(bg_path=bg_path, fullbg_path=fullbg_path, slice_path=slice_path)
    # gip.get_slice_offset()
    # gip.get_bg_endpoint()
    print gip.get_offset()
