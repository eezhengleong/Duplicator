import sys, time, configparser, os
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QMessageBox, QInputDialog
from PyQt5.QtGui import QIntValidator
from PyQt5.QtCore import QThread
from PyQt5.uic import loadUi
from Duplicator import Ui_MainWindow
import FindFileSize, vdspcDuplicateWorker, FindFileSizeWorker, vlibDuplicateWorker, FileEdit, logging

class DuplicatorClass(QMainWindow, Ui_MainWindow):
    def __init__(self, *args, obj=None, **kwargs):
        super(DuplicatorClass,self).__init__(*args, **kwargs)
        self.setupUi(self)

# class DuplicatorClass(QMainWindow):
#     def __init__(self):
#         super(DuplicatorClass,self).__init__()
#         loadUi("UI\Duplicator.ui",self)
        
        self.config_obj = configparser.ConfigParser(interpolation = None)
        self.config_obj.read("DuplicatorConfig.cfg")
        self.defaultpath = self.config_obj["default_path"]
        self.files_needed = self.config_obj["files_to_look_for"]
        self.postgres = self.config_obj["postgresql"]
        self.queries = self.config_obj["query"]
        self.db = {}
        if self.config_obj.has_section("postgresql"):
            params = self.config_obj.items("postgresql")
            for param in params:
                self.db[param[0]] = param[1]
        else:
            raise Exception('Section {0} not found in the {1} file'.format(section, filename))

        #initialize parameters and variables that will be used
        self.folder_name.setReadOnly(True)
        self.path.setReadOnly(True)
        self.onlyInt = QIntValidator()
        self.onlyInt.setRange(0,1000000)
        self.number.setValidator(self.onlyInt)
        self.pname = ""                                                 #path name of selected folder
        self.fname = ""                                                 #folder name of selected folder
        self.oname = ""                                                 #output path name 
        self.fsize = 0                                                  #file size
        self.disk_space = {}                                            #available disk space, inside this will have {"Total","Used","Free"}, but we will only use free
        self.able_copy = 0                                              #maximum number of copies able to accomodate the disk size
        self.space_needed = 0
        self.copies = 0                                                 #holds the number of files to be copied
        self.copied = 0                                                 #holds the number of coiped files
        self.duplicating = False                                        #indicator for duplication process
        self.OCV = False
        self.serverType = ""                                            #holds the server type
        self.bytesFormat = ["B","KB","MB","GB","TB"]
        self.setBtn()                                                   #enable or disable start and cancel button
        self.changebg()                                                 #change bg colour based on status
        #set actions on the UI
        self.server.currentIndexChanged.connect(self.set_default_path)  #default path will be set whenever a new server is chosen
        self.dnd.textChanged.connect(self.set_pname)                    #drag and drop(dnd) feature
        self.browse_folder.clicked.connect(self.browsefolder)           #open file explorer to select a source folder
        self.browse_path.clicked.connect(self.browsepath)               #open file explorer to select an output path
        self.path.textChanged.connect(self.find_disk_size)              #find available disk size when output path is selected
        self.path.textChanged.connect(self.calculate_copies)
        self.folder_name.textChanged.connect(self.calculate_copies)
        self.number.textChanged.connect(self.calculate_copies)          #show the maximum number of copies able to duplicate depending on the disk space and source size
        self.start.clicked.connect(self.start_clicked)                  #perfrom duplication when start button is clicked
        self.cancel.clicked.connect(self.cancelOpt)                     #cancel duplication when cancel button is clicked
        self.progressBar.setValue(0)                                    #set progress bar value to 0 at the start
        self.reset1.clicked.connect(self.resetSource)
        self.reset2.clicked.connect(self.resetOutput)

    def calculate_copies(self):
        if self.fsize != 0 and len(self.disk_space) != 0:
            self.able_copy = int(self.disk_space["Free"]/self.fsize)
            self.max_copies.setText("Maximum number of copies: " + str(self.able_copy))
        else:
            self.able_copy = 0
            self.max_copies.setText("Maximum number of copies: -")

        if self.number.text() != "0" and self.number.text() != "" and self.fsize != 0:
            num = int(self.number.text())
            self.space_needed = num * self.fsize
            spaceneeded = self.space_needed
            for i in self.bytesFormat:
                if spaceneeded > 1024:
                    spaceneeded = spaceneeded / 1024
                else:
                    self.needed_space.setText("Space needed: " + "{:.2f}".format(spaceneeded)+i)
                    break
        else:
            self.needed_space.setText("Space needed: -")

    def set_default_path(self): #default output path based on server type
        if self.server.currentIndex() == 0:
            self.oname = ""
            self.path.setText("")
            self.serverType = ""
        
        elif self.server.currentIndex() == 1:
            self.oname = self.defaultpath["VDSPC"]
            self.path.setText(self.oname)
            self.serverType = "VDSPC"

        elif self.server.currentIndex() == 2:
            self.oname = self.defaultpath["VLib_PL"]
            self.path.setText(self.oname)
            self.serverType = "V-Lib"


    def browsefolder(self): #setting source path name (pname) from file browsing
        if self.serverType == "VDSPC":
            self.pname=QFileDialog.getExistingDirectory(self, 'Select a folder', 'C:/vdspc_image_vone')

        elif self.serverType == "V-Lib":
            self.pname=QFileDialog.getOpenFileName(self, 'Select a .datj file', 'C:/CPI/cad', "datj(*.datj)")[0]

        else:
            self.prompt_dialog("Warning","Please first choose a server")

        if self.pname != "" and self.serverType != "":
            self.set_fname()

    def set_pname(self): #setting source path name (pname) from drag and drop
        if self.dnd.text() != "Drag and Drop" and self.serverType != "":
            self.pname = self.dnd.getFilePath()
            self.dnd.setText("Drag and Drop")
            self.set_fname()
        elif self.dnd.text() != "Drag and Drop":
            self.dnd.setText("Drag and Drop")
            self.prompt_dialog("Warning", "Please first choose a server!")

    def set_fname(self): #finding the source file/folder name and display in UI
        last_seperator = self.pname.rindex("/")
        self.fname = self.pname[last_seperator + 1:]
        self.folder_name.setText(self.fname)
        self.FindFolderSize()

    def FindFolderSize(self): #find the size of source file/folder using thread to prevent UI freezing
        self.thread = QThread()
        self.worker = FindFileSizeWorker.FindFolderSize()
        self.worker.moveToThread(self.thread)
        self.worker.set_param(self.pname)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(lambda: self.getFolderSize(self.worker))
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.finished.connect(self.thread.deleteLater)
        self.thread.start()

    def getFolderSize(self, worker): #method used to retrieve source file/folder size from thread
        self.fsize = worker.getTotal()
        self.calculate_copies()
        self.fsizedivided = self.fsize
        for i in self.bytesFormat:
            if self.fsizedivided > 1024:
                self.fsizedivided = self.fsizedivided / 1024
            else:
                self.foldersize.setText("Folder/File size: " + "{:.2f}".format(self.fsizedivided)+i)
                break

    def browsepath(self): #setting output path (oname) from browsing
        self.oname=QFileDialog.getExistingDirectory(self, 'Select a folder', 'D:/')
        if self.oname != "":
            self.path.setText(self.oname)

    def resetSource(self):
        self.folder_name.setText("")
        self.foldersize.setText("Folder/File size: -")
        self.pname = ""
        self.fname = ""
        self.fsize = 0
        self.calculate_copies()

    def resetOutput(self):
        self.path.setText("")
        self.diskspace.setText("Free space: -")
        self.oname = ""
        self.disk_space = {}
        self.calculate_copies()

    def find_disk_size(self): #method used to find disk size of selected output path
        if self.oname == "":
            self.diskspace.setText("Free space: ")
        else:
            self.disk_space = FindFileSize.get_disk_size(self.oname)
            self.diskspace.setText("Free space: "+ "{:.2f}".format(self.disk_space["Free"]/1024/1024/1024)+"GB")
            
    def start_clicked(self): #conditions when start button is clicked
        if self.server.currentText() == "--Choose Server--":
            self.prompt_dialog("Error","Please choose a server!")
        
        elif self.pname == "":
            self.prompt_dialog("Error","Please choose a folder!")
        
        elif self.oname == "":
            self.prompt_dialog("Error","Please choose an output path!")

        elif self.number.text() == "0" or self.number.text() == "":
            self.prompt_dialog("Error","Please input number of copies!")

        else:
            if self.find_files_needed():
                if self.check_available_space():
                    self.duplicating = True
                    
                    if self.serverType == "VDSPC":
                        self.setBtn()
                        self.changebg()
                        self.DuplicateVDSPC()
                    elif self.serverType == "V-Lib":
                        if self.PL_OCV():
                            self.setBtn()
                            self.changebg()
                            self.DuplicateVLib()
                        else:
                            print("nothing happened")
                else:
                    self.prompt_dialog("Error", "Not enough space!")

    def PL_OCV(self):
        items = ("Part Library only", "Part and OCV Library")
        item, okPressed = QInputDialog.getItem(self, "Please Choose", "Options: ", items, 0, False)
        if okPressed and item:
            print(item)
            if item == items[0]:
                self.OCV = False
            elif item == items[1]:
                self.OCV = True
            return True
        else:
            print("Cancelled")
            return False

    def find_files_needed(self):
        if self.serverType == "VDSPC":
            if os.path.isfile(self.pname+"/"+self.files_needed[self.serverType]):
                return True
            else:
                self.prompt_dialog("Error", self.files_needed[self.serverType]+" is not inside the source!")
                return False
        elif self.serverType == "V-Lib":
            name, ext = os.path.splitext(self.pname)
            vlib_files = self.files_needed[self.serverType].split(",")
            if ext != vlib_files[0]:
                self.prompt_dialog("Error", vlib_files[0] +" is not selected!")
                return False
            elif os.path.isfile(name+vlib_files[1]) == False:
                self.prompt_dialog("Error", vlib_files[1] +" is not inside the source!")
                return False
            else:
                return True

    def changebg(self): #method for changing bg colour when process starts and ends
        if self.duplicating:
            self.setStyleSheet("""QMainWindow{background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 rgba(170, 255, 127, 255), stop:0.875 rgba(255, 255, 255, 255));}""")
        else:
            self.setStyleSheet("""QMainWindow{background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 rgba(255, 255, 127, 255), stop:0.875 rgba(255, 255, 255, 255));}""")

    def check_available_space(self): #compare space needed with space available on disk
        if self.space_needed < self.disk_space["Free"]:
            return True
        else:
            return False

    def prompt_dialog(self, title, text): #method to prompt notification dialog
        dialog = QMessageBox()
        dialog.setWindowTitle(title)
        dialog.setText(text)
        if title == "Error" or title == "Warning":
            dialog.setIcon(QMessageBox.Warning)
        elif title == "Finished" or title == "Cancelled":
            dialog.setIcon(QMessageBox.Information)
        dialog.exec_()

    def DuplicateVDSPC(self): #VDSPC duplication process using thread
        self.proMsg("In Progress")
        start_time = time.time()
        self.copies = int(self.number.text())
        self.label_progress_num.setText("0/"+str(self.copies))
        self.progressBar.setValue(0)
        self.thread = QThread()
        self.worker = vdspcDuplicateWorker.DuplicateObject()
        self.worker.moveToThread(self.thread)
        self.worker.setParam(self.pname, self.copies, self.oname)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(lambda: self.resetParam(start_time))
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(self.reportProgress)
        self.thread.start()

    def DuplicateVLib(self): #V-Lib duplication processing thread
        self.proMsg("In Progress")
        vlib_files = self.files_needed[self.serverType].split(",")
        start_time = time.time()
        self.copies = int(self.number.text())
        self.label_progress_num.setText("0/"+str(self.copies))
        self.progressBar.setValue(0)
        self.thread = QThread()
        self.worker = vlibDuplicateWorker.DuplicateObject()
        self.worker.moveToThread(self.thread)
        self.worker.setParam(self.pname, self.copies, self.oname, self.db, vlib_files, self.queries, self.OCV, self.defaultpath["VLib_OCV"])
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(lambda: self.resetParam(start_time))
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(self.reportProgress)
        self.thread.start() 

    def reportProgress(self,n): #update progress number and progress bar by retrieving data from thread
        self.label_progress_num.setText(str(n) + "/" + str(self.copies))
        self.copied = n
        self.progressBar.setValue(int((self.copied/self.copies)*100))

    def proMsg(self, txt): #setting text on top of progress number
        self.label_progress.setText(txt)

    def cancelOpt(self): #conditions when cancel button is clicked
        dialog = QMessageBox()
        dialog.setWindowTitle("Cancel")
        dialog.setText("Are you sure to cancel?")
        dialog.setIcon(QMessageBox.Question)
        dialog.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        returnValue = dialog.exec()
        if returnValue == QMessageBox.Ok:
            self.worker.cancel()
        
    def resetParam(self, start_time): #reset parameters and variables when process is finished or cancelled
        if self.worker.copied == self.copies:
            self.proMsg("Done")
            self.prompt_dialog("Finished","Duplication finished.\nTime elapsed: "+"{:.2f}".format(time.time()-start_time)+" seconds")
        else:
            self.proMsg("Cancelled")
            self.prompt_dialog("Cancelled","Duplication Cancelled.\nTime elapsed: "+"{:.2f}".format(time.time()-start_time)+" seconds")
        self.duplicating = False
        self.setBtn()
        self.changebg()
        self.progressBar.setValue(0)
        self.OCV = False

    def setBtn(self): #enable or disable start and cancel button based on duplication status
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

#opening a window with widgets
if __name__ == '__main__':
    app=QApplication(sys.argv)
    mainwindow=DuplicatorClass()
    widget=QtWidgets.QStackedWidget()
    widget.addWidget(mainwindow)
    widget.setWindowTitle("Duplicator")
    widget.setFixedWidth(800)
    widget.setFixedHeight(600)
    widget.show()
    # sys.exit(app.exec_())
    app.exec()
    
