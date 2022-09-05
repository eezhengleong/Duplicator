from cProfile import run
import os
from PyQt5.QtCore import QObject, pyqtSignal
import FindFileSize

class FindFolderSize(QObject):
    finished = pyqtSignal()
    def __init__(self):
        super(FindFolderSize, self).__init__()

    def set_param(self, path="."):
        self.path = path

    def run(self):
        self.total = FindFileSize.get_dir_size(self.path)
        self.finished.emit()

    def getTotal(self):
        return self.total
        