import sys, os
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QMessageBox
from PyQt5.uic import loadUi
from PyQt5.QtGui import QIntValidator
import DuplicateFolder, FindFileSize, ModifyFile
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
        self.pname = ""         #path name of selected folder
        self.fname = ""         #folder name of selected folder
        self.oname = ""         #output path name 
        self.fsize = 0          #file size
        self.disk_space = {}    #available disk space, inside this will have {"Total","Used","Free"}
        self.dnd.textChanged.connect(self.set_pname)
        self.browse_folder.clicked.connect(self.browsefolder)
        self.browse_path.clicked.connect(self.browsepath)
        self.start.clicked.connect(self.start_clicked)

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
            self.find_disk_size()

    def find_disk_size(self):
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
                start_time = time.time()
                ModifyFile.main(self.pname, int(self.number.text()))
                end_time = time.time()
                self.prompt_dialog("Finished","Duplication finished. \nTime elapsed: "+"{:.2f}".format(end_time-start_time)+" seconds")
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
        dialog.setIcon(QMessageBox.Warning)
        dialog.exec_()


app=QApplication(sys.argv)
mainwindow=Duplicator()
widget=QtWidgets.QStackedWidget()
widget.addWidget(mainwindow)
widget.setWindowTitle("Duplicator")
widget.setFixedWidth(800)
widget.setFixedHeight(600)
widget.show()
sys.exit(app.exec_())