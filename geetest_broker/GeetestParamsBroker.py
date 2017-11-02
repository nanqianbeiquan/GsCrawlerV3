# coding=utf-8
"""
适用极验版本6.0.0~
"""
import platform
if platform.system() == 'Windows':
    import PyV8
else:
    from pyv8 import PyV8
import os

ctxt = PyV8.JSContext()
ctxt.enter()

with open(os.path.join(os.path.dirname(__file__), 'userresponse_imitator.6.0.0.js')) as f:
    userresponse_imitator_func = ctxt.eval(f.read())

with open(os.path.join(os.path.dirname(__file__), 'aa_imitator.6.0.0.js')) as f:
    aa_imitator_func = ctxt.eval(f.read())


def imitate_userrespose(distance, challenge):
    return userresponse_imitator_func(distance, challenge)


def imitate_aa(trail_arr, c, s):
    return aa_imitator_func(str(trail_arr), str(c), s)


if __name__ == '__main__':
    distance = 124
    challenge = '82d6ac78790b94c5ed516955f617ac97i2'
    print imitate_userrespose(distance, challenge)

    trail_arr = [[-11, -27, 0], [0, 0, 0], [1, 0, 244], [5, 0, 260], [9, 0, 276], [16, 0, 293], [24, 2, 310], [35, 3, 328],
                 [46, 5, 344], [57, 7, 361], [67, 9, 378], [74, 9, 397], [83, 11, 413], [90, 12, 430], [97, 12, 446],
                 [103, 13, 463], [108, 13, 480], [114, 13, 497], [118, 13, 517], [122, 13, 536], [126, 13, 551], [130, 13, 569],
                 [134, 13, 584], [138, 13, 601], [140, 13, 618], [142, 13, 636], [144, 14, 651], [145, 14, 668], [147, 14, 684],
                 [148, 14, 701], [149, 14, 718], [150, 14, 742], [151, 14, 759], [152, 14, 779], [155, 14, 792], [157, 14, 810],
                 [159, 14, 826], [162, 14, 842], [164, 14, 859], [166, 14, 876], [169, 14, 893], [171, 14, 910], [173, 14, 927],
                 [174, 14, 945], [175, 14, 962], [176, 14, 980], [178, 14, 997], [179, 14, 1014], [179, 14, 1032],
                 [180, 14, 1056], [180, 15, 1552], [180, 15, 1661], [180, 15, 1680]]
    c = [12, 58, 98, 36, 43, 95, 62, 15, 12]
    s = '36577848'
    print imitate_aa(trail_arr, c, s)
