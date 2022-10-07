from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QDialog, QFileDialog
from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt
from UIvLibPath import Ui_Dialog

class VLibSettings(QDialog, Ui_Dialog):
    # def __init__(self, pl, ocv, pgm):
    #     super(VLibSettings, self).__init__()
    #     loadUi('UI/Vlib_path.ui', self)

    def __init__(self, pl, ocv, pgm, duplicating, *args, obj=None, **kwargs):
        super(VLibSettings,self).__init__(*args, **kwargs)
        self.setupUi(self)

        self.pl, self.ocv, self.pgm, self.duplicating = pl, ocv, pgm, duplicating
        self.partpath.setReadOnly(True)
        self.ocvpath.setReadOnly(True)
        self.pgmpath.setReadOnly(True)
        self.partpath.setText(pl)
        self.ocvpath.setText(ocv)
        self.pgmpath.setText(pgm)
        self.setBtns()
        self.browsepart.clicked.connect(self.partbrowsing)
        self.browseocv.clicked.connect(self.ocvbrowsing)
        self.browsepgm.clicked.connect(self.pgmbrowsing)

    def setBtns(self):
        disabledSS = "background-color: gray; color: rgb(0, 0, 0);"
        enabledSS = """QPushButton{background-color: rgb(0, 157, 235);}
                       QPushButton:hover{background-color: rgb(85, 170, 255);}"""
        if self.duplicating:
            self.browsepart.setDisabled(True)
            self.browsepart.setStyleSheet(disabledSS)
            self.browseocv.setDisabled(True)
            self.browseocv.setStyleSheet(disabledSS)
            self.browsepgm.setDisabled(True)
            self.browsepgm.setStyleSheet(disabledSS)
        else:
            self.browsepart.setDisabled(False)
            self.browsepart.setStyleSheet(enabledSS)
            self.browseocv.setDisabled(False)
            self.browseocv.setStyleSheet(enabledSS)
            self.browsepgm.setDisabled(False)
            self.browsepgm.setStyleSheet(enabledSS)

    def partbrowsing(self):
        output = QFileDialog.getExistingDirectory(self, 'Select a folder', 'C:/')
        self.partpath.setText(output)

    def ocvbrowsing(self):
        output = QFileDialog.getExistingDirectory(self, 'Select a folder', 'C:/')
        self.ocvpath.setText(output)

    def pgmbrowsing(self):
        output = QFileDialog.getExistingDirectory(self, 'Select a folder', 'C:/')
        self.pgmpath.setText(output)