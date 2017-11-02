# coding=utf-8
import PackageTool
from gs.GsSrcCousumer import GsSrcCousumer
from LiaoNingSearcher import LiaoNingSearcher


class LiaoNingUpdateJob(GsSrcCousumer):

    def __init__(self):
        super(LiaoNingUpdateJob, self).__init__()

    def set_config(self):
        self.searcher = LiaoNingSearcher()

if __name__ == '__main__':
    job = LiaoNingUpdateJob()
    job.run()
