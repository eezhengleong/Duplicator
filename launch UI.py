import sys, os
from tkinter import dnd
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QMessageBox
from PyQt5.uic import loadUi
from PyQt5.QtGui import QIntValidator
import DuplicateFolder
import time

class Duplicator(QMainWindow):
    def __init__(self):
        super(Duplicator,self).__init__()
        loadUi("UI\Duplicator.ui",self)
        self.onlyInt = QIntValidator()
        self.onlyInt.setRange(0,86400)
        self.number.setValidator(self.onlyInt)
        self.pname = ""
        self.fname = ""
        self.oname = ""
        self.dnd.textChanged.connect(self.change_pname)
        self.browse_folder.clicked.connect(self.browsefolder)
        self.browse_path.clicked.connect(self.browsepath)
        self.start.clicked.connect(self.start_clicked)

    def change_pname(self):
        self.pname = self.dnd.getFilePath()
        self.dnd.setText("Drag and Drop")
        self.set_fname()

    def set_fname(self):
        last_seperator = self.pname.rindex("/")
        self.fname = self.pname[last_seperator + 1:]
        self.folder_name.setText(self.fname)

    def browsefolder(self):
        self.pname=QFileDialog.getExistingDirectory(self, 'Select a folder', 'D:/')
        self.set_fname()

    def browsepath(self):
        self.oname=QFileDialog.getExistingDirectory(self, 'Select a folder', 'D:/')
        self.path.setText(self.oname)

    def start_clicked(self):
        print(self.pname)
        if self.server.currentText() == "--Choose Server--":
            dialog = QMessageBox()
            dialog.setWindowTitle("Error")
            dialog.setText("Please choose a server!")
            dialog.setIcon(QMessageBox.Warning)
            dialog.exec_()
        
        elif self.pname == "":
            dialog = QMessageBox()
            dialog.setWindowTitle("Error")
            dialog.setText("Please choose a folder!")
            dialog.setIcon(QMessageBox.Warning)
            dialog.exec_()

        elif self.number.text() == "0":
            dialog = QMessageBox()
            dialog.setWindowTitle("Error")
            dialog.setText("Please input number of copies!")
            dialog.setIcon(QMessageBox.Warning)
            dialog.exec_()

        else:
            print("Success")
            print(self.server.currentText())
            print(self.pname)
            print(self.number.text())
            start_time = time.time()
            DuplicateFolder.FolderDuplicate(self.pname, self.number.text())
            end_time = time.time()
            print(end_time-start_time)

app=QApplication(sys.argv)
mainwindow=Duplicator()
widget=QtWidgets.QStackedWidget()
widget.addWidget(mainwindow)
widget.setWindowTitle("Duplicator")
widget.setFixedWidth(800)
widget.setFixedHeight(600)
widget.show()
sys.exit(app.exec_())