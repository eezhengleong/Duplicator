#subclassing object and use moveToThread to let the thread handle this process

from PyQt5.QtCore import QObject, pyqtSignal
import pgmDuplicate

class DuplicateObject(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)

    def __init__(self): #class constructor
        super(DuplicateObject, self).__init__()
        
    def setParam(self, source, copies, outname, selectedfiles): #set parameter before run
        self.source, self.copies, self.outname, self.selectedfiles = source, copies, outname, selectedfiles
        self.copied = 0
        self.threadactive = True

    def run(self): #method that will be executed when thread.start() is called
        for i in range(self.copies):
            if self.threadactive:
                program = pgmDuplicate.main(self.source, self.selectedfiles, self.outname)
                self.copied = i + 1
                self.progress.emit(self.copied)
            else:
                break
        self.finished.emit()

    def cancel(self): #stopping the duplication process when cancel is selected
        print("cancelling")
        self.threadactive = False