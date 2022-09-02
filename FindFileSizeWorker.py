from cProfile import run
import os
from PyQt5.QtCore import QObject, pyqtSignal
import FindFileSize

class FindFolderSize(QObject):
    finished = pyqtSignal()
    def __init__(self):
        super(FindFolderSize, self).__init__()

    def run(self, path='.'):
        self.total = FindFileSize.get_dir_size(path)
        self.finished.emit()

    def getTotal(self):
        return self.total
        