# coding=utf-8
import gs.PackageTool
from geetest_broker import MySQL
from ZongJuSearcher import ZongJuSearcher
import traceback


if __name__ == '__main__':
    searcher = ZongJuSearcher()
    mc_list = [
        u'惠而浦（中国）股份有限公司'
    ]
    for mc in mc_list:
        print mc
        print searcher.load_nian_bao_msg(mc=mc, xydm="")
