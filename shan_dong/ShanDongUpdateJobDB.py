# coding=utf-8
import PackageTool
from gs.UpdateFromTable import UpdateFromTable
from ShanDongSearcher_old import ShanDongSearcher


class ShanDongUpdateJobDB(UpdateFromTable):

    def __init__(self):
        super(ShanDongUpdateJobDB, self).__init__()

    def set_config(self):
        self.searcher = ShanDongSearcher()

if __name__ == '__main__':
    job = ShanDongUpdateJobDB()
    job.run()
