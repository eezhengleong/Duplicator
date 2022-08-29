from cProfile import run
import os
from PyQt5.QtCore import QObject, pyqtSignal
import FindFileSize

class FindFolderSize(QObject):
    finished = pyqtSignal()
    total = 0
    def __init__(self):
        super(FindFolderSize, self).__init__()

    def run(self, path='.'):
        self.total = FindFileSize.get_dir_size(path)
        print("Total: ", self.total)
        self.finished.emit()

    # def get_dir_size(path='.'):
    #     self.total = 0
    #     with os.scandir(path) as it:
    #         for entry in it:
    #             if entry.is_file():
    #                 total += entry.stat().st_size
    #             elif entry.is_dir():
    #                 total += self.get_dir_size(entry.path)
    #     return self.total

    def getTotal(self):
        print("Returning total")
        return self.total
        