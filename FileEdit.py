from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtCore import Qt
import os

class FileEdit(QLineEdit):
    def __init__(self, parent):
        super(FileEdit, self).__init__(parent)
        self.setReadOnly(True)
        self.setDragEnabled(True)
        self.filepath=""

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
            data = event.mimeData()
            urls = data.urls()
            self.filepath = str(urls[0].path())[1:]
            last_seperator = self.filepath.rindex("/")
            folder_name = self.filepath[last_seperator + 1:]
            self.setText(folder_name)

    def getFilePath(self):
        return self.filepath
