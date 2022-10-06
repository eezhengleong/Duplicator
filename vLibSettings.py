from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt
from UIvLibSetings import Ui_Categories

class PgmLibSettings(QDialog, Ui_Categories):
    def __init__(self, checkedbox, PL, ocv_prev, pgm, *args, obj=None, **kwargs):
        super(PgmLibSettings,self).__init__(*args, **kwargs)
        self.setupUi(self)


# class PgmLibSettings(QDialog):
#     def __init__(self, checkedbox, ocv_prev, pgm):
#         super(PgmLibSettings, self).__init__()
#         loadUi('UI/Categories.ui', self)

        self.checkedbox = checkedbox
        self.pl = PL
        self.ocv = ocv_prev
        self.pgm = pgm
        self.initboxes()
        self.Program.toggled.connect(self.checkall)
        self.ZHeight.toggled.connect(self.checkall)
        self.Unpop.toggled.connect(self.checkall)
        self.CustomLocation.toggled.connect(self.checkall)
        self.SideCamera.toggled.connect(self.checkall)
        self.CenterPin.toggled.connect(self.checkall)
        self.SelectAll.toggled.connect(self.selectall)
        self.Part.stateChanged.connect(self.onlyone)
        self.Part_OCV.stateChanged.connect(self.onlyone)
        self.Pgm.stateChanged.connect(self.enablePgm)

    def enablePgm(self):
        if self.Pgm.isChecked():
            self.IncludeTile.setDisabled(False)
            self.Program.setDisabled(False)
            self.ZHeight.setDisabled(False)
            self.Unpop.setDisabled(False)
            self.CustomLocation.setDisabled(False)
            self.SideCamera.setDisabled(False)
            self.CenterPin.setDisabled(False)
            self.SelectAll.setDisabled(False)

        else:
            self.IncludeTile.setDisabled(True)
            self.Program.setDisabled(True)
            self.ZHeight.setDisabled(True)
            self.Unpop.setDisabled(True)
            self.CustomLocation.setDisabled(True)
            self.SideCamera.setDisabled(True)
            self.CenterPin.setDisabled(True)
            self.SelectAll.setDisabled(True)
        
    def onlyone(self, state):
        if state == Qt.Checked:
            if self.sender() == self.Part:
                self.Part_OCV.setChecked(False)

            elif self.sender() == self.Part_OCV:
                self.Part.setChecked(False)
    

    def initboxes(self):
        if self.pgm:
            self.Pgm.setChecked(True)

            if "tile" in self.checkedbox:
                self.IncludeTile.setChecked(True)

            if "program" in self.checkedbox:
                self.Program.setChecked(True)

            if "ZHeight" in self.checkedbox:
                self.ZHeight.setChecked(True)

            if "Unpop" in self.checkedbox:
                self.Unpop.setChecked(True)

            if "customLocation" in self.checkedbox:
                self.CustomLocation.setChecked(True)

            if "sideCam" in self.checkedbox:
                self.SideCamera.setChecked(True)

            if "centerPin" in self.checkedbox:
                self.CenterPin.setChecked(True)
            
            self.initcheckall()

        else:
            self.Pgm.setChecked(False)
            self.IncludeTile.setDisabled(True)
            self.Program.setDisabled(True)
            self.ZHeight.setDisabled(True)
            self.Unpop.setDisabled(True)
            self.CustomLocation.setDisabled(True)
            self.SideCamera.setDisabled(True)
            self.CenterPin.setDisabled(True)
            self.SelectAll.setDisabled(True)

        if self.ocv:
            self.Part_OCV.setChecked(True)
        elif self.pl:
            self.Part.setChecked(True)
        elif self.ocv == False and self.pl == False:
            self.Part.setChecked(False)
            self.Part_OCV.setChecked(False)

    def initcheckall(self):
        checklist = ["program", "ZHeight", "Unpop", "customLocation", "sideCam", "centerPin"]
        for i in checklist:
            if i not in self.checkedbox:
                self.SelectAll.setChecked(False)
                break
            else:
                self.SelectAll.setChecked(True)

    def checkall(self):
        if self.Program.isChecked() and self.ZHeight.isChecked() and self.Unpop.isChecked() and self.CustomLocation.isChecked() and self.SideCamera.isChecked() and self.CenterPin.isChecked():
            self.SelectAll.setChecked(True)
        else:
            self.SelectAll.setChecked(False)

    def selectall(self):
        
        if self.SelectAll.isChecked():
            self.Program.setChecked(True)
            self.ZHeight.setChecked(True)
            self.Unpop.setChecked(True)
            self.CustomLocation.setChecked(True)
            self.SideCamera.setChecked(True)
            self.CenterPin.setChecked(True)
        else:
            if self.Program.isChecked() and self.ZHeight.isChecked() and self.Unpop.isChecked() and self.CustomLocation.isChecked() and self.SideCamera.isChecked() and self.CenterPin.isChecked():
                self.Program.setChecked(False)
                self.ZHeight.setChecked(False)
                self.Unpop.setChecked(False)
                self.CustomLocation.setChecked(False)
                self.SideCamera.setChecked(False)
                self.CenterPin.setChecked(False)
