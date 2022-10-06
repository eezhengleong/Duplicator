# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Categories.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Categories(object):
    def setupUi(self, Categories):
        Categories.setObjectName("Categories")
        Categories.resize(400, 370)
        self.buttonBox = QtWidgets.QDialogButtonBox(Categories)
        self.buttonBox.setGeometry(QtCore.QRect(30, 330, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.IncludeTile = QtWidgets.QCheckBox(Categories)
        self.IncludeTile.setGeometry(QtCore.QRect(70, 170, 121, 17))
        self.IncludeTile.setObjectName("IncludeTile")
        self.SelectAll = QtWidgets.QCheckBox(Categories)
        self.SelectAll.setGeometry(QtCore.QRect(70, 200, 121, 17))
        self.SelectAll.setObjectName("SelectAll")
        self.Program = QtWidgets.QCheckBox(Categories)
        self.Program.setGeometry(QtCore.QRect(90, 230, 121, 17))
        self.Program.setObjectName("Program")
        self.Unpop = QtWidgets.QCheckBox(Categories)
        self.Unpop.setGeometry(QtCore.QRect(90, 290, 121, 17))
        self.Unpop.setObjectName("Unpop")
        self.ZHeight = QtWidgets.QCheckBox(Categories)
        self.ZHeight.setGeometry(QtCore.QRect(90, 260, 121, 17))
        self.ZHeight.setObjectName("ZHeight")
        self.CustomLocation = QtWidgets.QCheckBox(Categories)
        self.CustomLocation.setGeometry(QtCore.QRect(230, 230, 121, 17))
        self.CustomLocation.setObjectName("CustomLocation")
        self.SideCamera = QtWidgets.QCheckBox(Categories)
        self.SideCamera.setGeometry(QtCore.QRect(230, 260, 121, 17))
        self.SideCamera.setObjectName("SideCamera")
        self.CenterPin = QtWidgets.QCheckBox(Categories)
        self.CenterPin.setGeometry(QtCore.QRect(230, 290, 121, 17))
        self.CenterPin.setObjectName("CenterPin")
        self.label = QtWidgets.QLabel(Categories)
        self.label.setGeometry(QtCore.QRect(0, 10, 401, 21))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.line = QtWidgets.QFrame(Categories)
        self.line.setGeometry(QtCore.QRect(0, 110, 401, 16))
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.Part = QtWidgets.QCheckBox(Categories)
        self.Part.setGeometry(QtCore.QRect(60, 50, 201, 17))
        self.Part.setObjectName("Part")
        self.Part_OCV = QtWidgets.QCheckBox(Categories)
        self.Part_OCV.setGeometry(QtCore.QRect(60, 80, 201, 16))
        self.Part_OCV.setObjectName("Part_OCV")
        self.Pgm = QtWidgets.QCheckBox(Categories)
        self.Pgm.setGeometry(QtCore.QRect(60, 140, 201, 16))
        self.Pgm.setObjectName("Pgm")

        self.retranslateUi(Categories)
        self.buttonBox.accepted.connect(Categories.accept)
        self.buttonBox.rejected.connect(Categories.reject)
        QtCore.QMetaObject.connectSlotsByName(Categories)

    def retranslateUi(self, Categories):
        _translate = QtCore.QCoreApplication.translate
        Categories.setWindowTitle(_translate("Categories", "Dialog"))
        self.IncludeTile.setText(_translate("Categories", "Include Tiled Images"))
        self.SelectAll.setText(_translate("Categories", "Select All"))
        self.Program.setText(_translate("Categories", "Program"))
        self.Unpop.setText(_translate("Categories", "Unpop"))
        self.ZHeight.setText(_translate("Categories", "ZHeight"))
        self.CustomLocation.setText(_translate("Categories", "CustomLocation"))
        self.SideCamera.setText(_translate("Categories", "SideCamera"))
        self.CenterPin.setText(_translate("Categories", "CenterPin"))
        self.label.setText(_translate("Categories", "V-Lib Settings:"))
        self.Part.setText(_translate("Categories", "Part Library"))
        self.Part_OCV.setText(_translate("Categories", "Part Library and OCV Library"))
        self.Pgm.setText(_translate("Categories", "Program Library"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Categories = QtWidgets.QDialog()
    ui = Ui_Categories()
    ui.setupUi(Categories)
    Categories.show()
    sys.exit(app.exec_())
