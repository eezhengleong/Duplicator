from cProfile import run
import os
from PyQt5.QtCore import QObject, pyqtSignal
import FindFileSize

class FindFolderSize(QObject):
    finished = pyqtSignal()
    def __init__(self):
        super(FindFolderSize, self).__init__()

    def set_param(self, path):  #path is a list
        self.path = path
        self.total = 0

    def run(self):
        for i in self.path:
            self.total += FindFileSize.get_dir_size(i)
        print("emit")
        self.finished.emit()

    def getTotal(self):
        return self.total
        