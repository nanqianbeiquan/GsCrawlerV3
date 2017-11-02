# coding=gbk
import PackageTool
import sys
from gs.UpdateFromTable import UpdateFromTable
from JiangSuSearcher import JiangSuSearcher


class JiangsuUpdateJobDB(UpdateFromTable):

    def __init__(self):
        super(JiangsuUpdateJobDB, self).__init__()
    
    def set_config(self):
        self.searcher = JiangSuSearcher()

if __name__ == "__main__":
    job = JiangsuUpdateJobDB()
    job.run()


