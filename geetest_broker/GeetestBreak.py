# coding = utf-8

import random
from GeetestDistance import GeetestDistance
import BreakTrail
import GeetestJS
import TimeUtils


class GeetestBreak(object):

    bg_path = None
    full_bg_path = None
    slice_path = None
    gt = None
    challenge = None
    trail_arr_text_list = []

    def __init__(self, bg_path, full_bg_path, slice_path, gt, challenge):
        super(GeetestBreak, self).__init__()
        self.bg_path = bg_path
        self.full_bg_path = full_bg_path
        self.slice_path = slice_path
        self.challenge = challenge
        self.gt = gt

    def get_break_params(self):
        gtd = GeetestDistance(bg_path=self.bg_path, fullbg_path=self.full_bg_path, slice_path=self.slice_path)
        distance = gtd.get_offset()
        trail_arr = BreakTrail.get_trali_arr(distance)
        # print 'distance:', distance
        pass_time = trail_arr[-1][-1]
        # print trail_arr
        params = {
            'challenge': str(self.challenge),
            'gt': str(self.gt),
            'userresponse': GeetestJS.get_userresponse(distance, self.challenge),
            'passtime': pass_time,
            'imgload': random.randint(70, 150),
            'aa': GeetestJS.get_a(trail_arr),
            'callback': 'geetest_%s' % TimeUtils.get_cur_ts_mil(),
        }
        return params, trail_arr[-1][2]


if __name__ == '__main__':
    pass
