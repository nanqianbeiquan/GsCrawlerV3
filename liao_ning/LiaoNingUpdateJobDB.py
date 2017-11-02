# coding=utf-8
import PackageTool
from gs.UpdateFromTable import UpdateFromTable
from LiaoNingSearcher import LiaoNingSearcher


class LiaoNingUpdateJobDB(UpdateFromTable):

    def __init__(self):
        super(LiaoNingUpdateJobDB, self).__init__()

    def set_config(self):
        self.searcher = LiaoNingSearcher()

if __name__ == '__main__':
    job = LiaoNingUpdateJobDB()
    job.run()
