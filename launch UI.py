import sys, os
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QLineEdit, QMessageBox
from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt, QUrl, QEvent
import DuplicateFolder

class Duplicator(QMainWindow):
    def __init__(self):
        super(Duplicator,self).__init__()
        loadUi("UI\Duplicator.ui",self)
        self.dnd.setDragEnabled(True)
        self.dnd.setAcceptDrops(True)
        self.browse_folder.clicked.connect(self.browsefiles)

    def browsefiles(self):
        fname=QFileDialog.getOpenFileName(self, 'Open file', 'D:\codefirst.io\PyQt5 tutorials\Browse Files', 'Images (*.png, *.xmp *.jpg)')
        # fname=QFileDialog.getOpenFileName(self, 'Open file', 'D:\codefirst.io\PyQt5 tutorials\Browse Files', 'All files')
        self.dnd.setText(fname[0])
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()



app=QApplication(sys.argv)
mainwindow=Duplicator()
widget=QtWidgets.QStackedWidget()
widget.addWidget(mainwindow)
widget.setWindowTitle("Duplicator")
widget.setFixedWidth(800)
widget.setFixedHeight(600)
widget.show()
sys.exit(app.exec_())