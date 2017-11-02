# coding=utf-8
import PackageTool
from gs.UpdateFromTable import UpdateFromTable
from ShangHaiSearcher_all import ShangHaiSearcher


class ShangHaiUpdateJobDB(UpdateFromTable):

    def __init__(self):
        super(ShangHaiUpdateJobDB, self).__init__()

    def set_config(self):
        self.searcher = ShangHaiSearcher()

if __name__ == '__main__':
    job = ShangHaiUpdateJobDB()
    job.run()
