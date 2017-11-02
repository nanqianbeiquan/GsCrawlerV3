# coding=utf-8
import PackageTool
from gs.GsSrcCousumer import GsSrcCousumer
from ShangHaiSearcher_all import ShangHaiSearcher


class ShangHaiUpdateJob(GsSrcCousumer):

    def __init__(self):
        super(ShangHaiUpdateJob, self).__init__()

    def set_config(self):
        self.searcher = ShangHaiSearcher()

if __name__ == '__main__':
    job = ShangHaiUpdateJob()
    job.run()
