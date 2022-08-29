import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QMessageBox
from PyQt5.uic import loadUi
from PyQt5.QtGui import QIntValidator
from PyQt5.QtCore import QThread
import FindFileSize, DuplicateWorker, FolderSizeWorker
import time

class Duplicator(QMainWindow):
    def __init__(self):
        super(Duplicator,self).__init__()
        loadUi("UI\Duplicator.ui",self)

        #initialize parameters and variables that will be used
        self.folder_name.setReadOnly(True)
        self.path.setReadOnly(True)
        self.onlyInt = QIntValidator()
        self.onlyInt.setRange(0,86400)
        self.number.setValidator(self.onlyInt)
        self.pname = ""                                                 #path name of selected folder
        self.fname = ""                                                 #folder name of selected folder
        self.oname = ""                                                 #output path name 
        self.fsize = 0                                                  #file size
        self.disk_space = {}                                            #available disk space, inside this will have {"Total","Used","Free"}, but we will only use free
        self.copies = 0                                                 #holds the number of files to be copied
        self.copied = 0                                                 #holds the number of coiped files
        self.duplicating = False                                        #indicator for duplication process
        self.setBtn()                                                   #enable or disable start and cancel button
        self.changebg()
        #set actions on the UI
        self.server.currentIndexChanged.connect(self.set_default_path)  #default path will be set whenever a new server is chosen
        self.dnd.textChanged.connect(self.set_pname)                    #drag and drop(dnd) feature
        self.browse_folder.clicked.connect(self.browsefolder)           #open file explorer to select a source folder
        self.browse_path.clicked.connect(self.browsepath)               #open file explorer to select an output path
        self.path.textChanged.connect(self.find_disk_size)              #find available disk size when output ppath is selected
        self.start.clicked.connect(self.start_clicked)                  #perfrom duplication when start button is clicked
        self.cancel.clicked.connect(self.cancelOpt)                     #cancel duplication when cancel button is clicked
        #self.preset.clicked.connect(self.setPreset)                     #ignore this
        self.progressBar.setValue(0)

    def setPreset(self):
        self.server.setCurrentIndex(1)
        self.pname = "D:/vdspc_image_vone/AXI-EZLEONG-NB[@$@]2022-08-11-08-31-30"
        self.set_fname()
        self.number.setText("5")

    def set_default_path(self):
        if self.server.currentIndex() == 0:
            self.oname = ""
            self.path.setText("")
        
        elif self.server.currentIndex() == 1:
            self.oname = "D:/vdspc_image_vone"
            self.path.setText(self.oname)

        elif self.server.currentIndex() == 2:
            self.oname = "C:/vdspc_image_vone"
            self.path.setText(self.oname)

        elif self.server.currentIndex() == 3:
            self.oname = "C:/vdspc_image_vone"
            self.path.setText(self.oname)

    def browsefolder(self):
        self.pname=QFileDialog.getExistingDirectory(self, 'Select a folder', 'D:/')
        if self.pname != "":
            self.set_fname()

    def set_pname(self):
        self.pname = self.dnd.getFilePath()
        self.dnd.setText("Drag and Drop")
        self.set_fname()

    def set_fname(self):
        last_seperator = self.pname.rindex("/")
        self.fname = self.pname[last_seperator + 1:]
        self.folder_name.setText(self.fname)
        self.FindFolderSize()
        # self.fsize = FindFileSize.get_dir_size(self.pname)
        # bytesFormat = ["B","KB","MB","GB","TB"]
        # self.fsizedivided = self.fsize
        # for i in bytesFormat:
        #     if self.fsizedivided > 1024:
        #         self.fsizedivided = self.fsizedivided / 1024
        #     else:
        #         self.foldersize.setText("Folder size: " + "{:.2f}".format(self.fsizedivided)+i)
        #         break

    def FindFolderSize(self):
        self.thread = QThread()
        self.worker = FolderSizeWorker.FindFolderSize()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(lambda: self.worker.run(self.pname))
        self.worker.finished.connect(lambda: self.getFolderSize(self.worker))
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.finished.connect(self.thread.deleteLater)
        self.thread.start()

    def getFolderSize(self, worker):
        self.fsize = worker.getTotal()
        bytesFormat = ["B","KB","MB","GB","TB"]
        self.fsizedivided = self.fsize
        for i in bytesFormat:
            if self.fsizedivided > 1024:
                self.fsizedivided = self.fsizedivided / 1024
            else:
                self.foldersize.setText("Folder size: " + "{:.2f}".format(self.fsizedivided)+i)
                break

    def browsepath(self):
        self.oname=QFileDialog.getExistingDirectory(self, 'Select a folder', 'D:/')
        if self.oname != "":
            self.path.setText(self.oname)

    def find_disk_size(self):
        if self.oname == "":
            self.diskspace.setText("Free space: ")
        else:
            self.disk_space = FindFileSize.get_disk_size(self.oname)
            self.diskspace.setText("Free space: "+ "{:.2f}".format(self.disk_space["Free"]/1024/1024/1024)+"GB")
            
    def start_clicked(self):
        if self.server.currentText() == "--Choose Server--":
            self.prompt_dialog("Error","Please choose a server!")
        
        elif self.pname == "":
            self.prompt_dialog("Error","Please choose a folder!")
        
        elif self.path.text() == "":
            self.prompt_dialog("Error","Please choose an output path!")

        elif self.number.text() == "0" or self.number.text() == "":
            self.prompt_dialog("Error","Please input number of copies!")

        else:
            if self.check_available_space():
                print("Success")
                self.duplicating = True
                self.setBtn()
                self.changebg()
                self.DuplicateFilesObj()
            else:
                self.prompt_dialog("Error", "Not enough space!")

    def changebg(self):
        if self.duplicating:
            self.setStyleSheet("""QMainWindow{background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 rgba(170, 255, 127, 255), stop:0.875 rgba(255, 255, 255, 255));}""")
        else:
            self.setStyleSheet("""QMainWindow{background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 rgba(255, 255, 127, 255), stop:0.875 rgba(255, 255, 255, 255));}""")

    def check_available_space(self):
        num = int(self.number.text())
        space_needed = num * self.fsize
        if space_needed < self.disk_space["Free"]:
            print(space_needed)
            print(self.disk_space["Free"])
            print("Enough space")
            return True
        else:
            print(space_needed)
            print(self.disk_space["Free"])
            print("not enough space, False returned")
            return False

    def prompt_dialog(self, title, text):
        dialog = QMessageBox()
        dialog.setWindowTitle(title)
        dialog.setText(text)
        if title == "Error":
            dialog.setIcon(QMessageBox.Warning)
        elif title == "Finished" or title == "Cancelled":
            dialog.setIcon(QMessageBox.Information)
        dialog.exec_()

    def DuplicateFilesObj(self):
        self.proMsg("In Progress")
        start_time = time.time()
        self.copies = int(self.number.text())
        self.label_progress_num.setText("0/"+str(self.copies))
        self.progressBar.setValue(0)
        self.thread = QThread()
        print("thread created")
        print("is thread alive: ", self.thread.isRunning())
        self.worker = DuplicateWorker.DuplicateObject()
        print("worker created")
        self.worker.moveToThread(self.thread)
        print("worker moved to thread")
        self.worker.setParam(self.pname, self.copies, self.oname)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(lambda: self.resetParam(start_time))
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(self.reportProgress)
        self.thread.start()
        print("is thread running: ", self.thread.isRunning())

    def reportProgress(self,n):
        self.label_progress_num.setText(str(n) + "/" + str(self.copies))
        self.copied = n
        self.progressBar.setValue(int((self.copied/self.copies)*100))

    def proMsg(self, txt):
        self.label_progress.setText(txt)

    def cancelOpt(self):
        dialog = QMessageBox()
        dialog.setWindowTitle("Cancel")
        dialog.setText("Are you sure to cancel?")
        dialog.setIcon(QMessageBox.Question)
        dialog.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        returnValue = dialog.exec()
        if returnValue == QMessageBox.Ok:
            self.worker.cancel()
        
    def resetParam(self, start_time):
        if self.worker.copied == self.copies:
            self.proMsg("Done")
            self.prompt_dialog("Finished","Duplication finished.\nTime elapsed: "+"{:.2f}".format(time.time()-start_time)+" seconds")
        else:
            self.proMsg("Cancelled")
            self.prompt_dialog("Cancelled","Duplication Cancelled.\nTime elapsed: "+"{:.2f}".format(time.time()-start_time)+" seconds")
        self.duplicating = False
        self.setBtn()
        self.changebg()

    def setBtn(self):
        if self.duplicating:
            self.start.setEnabled(False)
            self.start.setStyleSheet("background-color: gray; color: rgb(0, 0, 0);")
            self.cancel.setEnabled(True)
            self.cancel.setStyleSheet("""QPushButton{background-color: rgb(255, 0, 0);
                                         color: rgb(0, 0, 0);}
                                         QPushButton:hover{background-color: rgb(255, 85, 127);}""")
        else:
            self.start.setEnabled(True)
            self.start.setStyleSheet("""QPushButton{background-color: rgb(0, 255, 127);
                                        color: rgb(0, 0, 0);}
                                        QPushButton:hover{background-color: rgb(170, 255, 127);}""")
            self.cancel.setEnabled(False)
            self.cancel.setStyleSheet("background-color: gray; color: rgb(0, 0, 0);")


app=QApplication(sys.argv)
mainwindow=Duplicator()
widget=QtWidgets.QStackedWidget()
widget.addWidget(mainwindow)
widget.setWindowTitle("Duplicator")
widget.setFixedWidth(800)
widget.setFixedHeight(600)
widget.show()
sys.exit(app.exec_())