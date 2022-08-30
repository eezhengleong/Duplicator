#subclassing object and use moveToThread to let the thread handle this process

from PyQt5.QtCore import QObject, pyqtSignal
import vdspcDuplicate

class DuplicateObject(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)

    def __init__(self): #class constructor
        super(DuplicateObject, self).__init__()
        
    def setParam(self, pathname, copies, outname): #set parameter before run
        self.pathname, self.copies, self.outname = pathname, copies, outname
        self.copied = 0
        self.threadactive = True

    def run(self): #method that will be executed when thread.start() is called
        lineList, formating = vdspcDuplicate.find_param(self.pathname)
        for i in range(self.copies):
            if self.threadactive:
                vdspcDuplicate.main(self.pathname, self.outname, lineList, formating)
                self.copied = i + 1
                self.progress.emit(self.copied)
            else:
                break
        self.finished.emit()

    def cancel(self): #stopping the duplication process when cancel is selected
        print("cancelling")
        self.threadactive = False