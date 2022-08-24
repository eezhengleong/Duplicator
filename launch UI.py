from cProfile import run
import sys, os
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QMessageBox
from PyQt5.uic import loadUi
from PyQt5.QtGui import QIntValidator
from PyQt5.QtCore import QObject, QThread, pyqtSignal
import FindFileSize, ModifyFile, ModiifyFile2
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
        self.disk_space = {}                                            #available disk space, inside this will have {"Total","Used","Free"}
        self.copies = 0
        self.server.currentIndexChanged.connect(self.set_default_path)
        self.dnd.textChanged.connect(self.set_pname)
        self.browse_folder.clicked.connect(self.browsefolder)
        self.browse_path.clicked.connect(self.browsepath)
        self.path.textChanged.connect(self.find_disk_size)
        self.start.clicked.connect(self.start_clicked)

    def reportProgress(self,n):
        self.label_progress_num.setText(str(n) + "/" + str(self.copies))
        #print("changing label ", type(n), " ", n)


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
        self.fsize = FindFileSize.get_dir_size(self.pname)
        self.folder_name.setText(self.fname+" ("+"{:.2f}".format(self.fsize/1024/1024)+"MB)")

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
                self.DuplicateFiles()
            else:
                self.prompt_dialog("Error", "Not enough space!")

    def check_available_space(self):
        num = int(self.number.text())
        space_needed = num * self.fsize
        if space_needed < self.disk_space["Free"]:
            print(space_needed)
            print(self.disk_space["Free"])
            print("True returned")
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
        elif title == "Finished":
            dialog.setIcon(QMessageBox.Information)
        dialog.exec_()

    def DuplicateFiles(self):
        self.proMsg("In Progress")
        start_time = time.time()
        self.copies = int(self.number.text())
        self.worker = MainBackgroundThread(self.pname, self.copies, self.oname)
        self.worker.started.connect(lambda: self.start.setEnabled(False))
        self.worker.finished.connect(lambda: self.prompt_dialog("Finished","Duplication finished.\nTime elapsed: "+"{:.2f}".format(time.time()-start_time)+" seconds"))
        self.worker.finished.connect(lambda: self.proMsg("Done"))
        self.worker.finished.connect(lambda: self.start.setEnabled(True))
        self.worker.progress.connect(self.reportProgress)
        self.worker.start()

    def proMsg(self, txt):
        self.label_progress.setText(txt)

class MainBackgroundThread(QThread):
    started = pyqtSignal()
    finished = pyqtSignal()
    progress = pyqtSignal(int)
    def __init__(self, pathname, copies, outname):
        QThread.__init__(self)
        self.pathname, self.copies, self.outname = pathname, copies, outname
    
    def run(self):
        self.started.emit()
        lineList, formating = ModiifyFile2.find_param(self.pathname)
        for i in range(self.copies):
            ModiifyFile2.main(self.pathname, self.outname, lineList, formating)
            self.progress.emit(i+1)
        self.finished.emit()

app=QApplication(sys.argv)
mainwindow=Duplicator()
widget=QtWidgets.QStackedWidget()
widget.addWidget(mainwindow)
widget.setWindowTitle("Duplicator")
widget.setFixedWidth(800)
widget.setFixedHeight(600)
widget.show()
sys.exit(app.exec_())