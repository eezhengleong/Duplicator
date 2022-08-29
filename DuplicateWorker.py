from PyQt5.QtCore import QObject, pyqtSignal
import ModifyFile2

class DuplicateObject(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)
    def __init__(self):
        super(DuplicateObject, self).__init__()
        
    def setParam(self, pathname, copies, outname):
        self.pathname, self.copies, self.outname = pathname, copies, outname
        self.copied = 0
        self.threadactive = True

    def run(self):
        lineList, formating = ModifyFile2.find_param(self.pathname)
        for i in range(self.copies):
            if self.threadactive:
                ModifyFile2.main(self.pathname, self.outname, lineList, formating)
                self.copied = i + 1
                self.progress.emit(self.copied)
            else:
                break
        self.finished.emit()

    def cancel(self):
        print("cancelling")
        self.threadactive = False