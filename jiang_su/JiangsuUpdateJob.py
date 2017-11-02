# coding=gbk
import PackageTool
import sys
from gs.GsSrcCousumer import GsSrcCousumer
from JiangSuSearcher import JiangSuSearcher


class JiangsuUpdateJob(GsSrcCousumer):

    def __init__(self):
        super(JiangsuUpdateJob, self).__init__()
    
    def set_config(self):
        self.searcher = JiangSuSearcher()

if __name__ == "__main__":
    job = JiangsuUpdateJob()
    job.run()


