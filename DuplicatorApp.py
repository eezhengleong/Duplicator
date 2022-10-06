import sys, time, configparser, os
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QMessageBox, QInputDialog
from PyQt5.QtGui import QIntValidator, QIcon
from PyQt5.QtCore import QThread
from PyQt5.uic import loadUi
from UIDuplicator import Ui_MainWindow
import FindFileSize, vdspcDuplicateWorker, FindFileSizeWorker, pl_ocvDuplicateWorker, vlibDuplicateWorker, FileEdit, logging, vLibSettings, logging, pgmDuplicateWorker, vLibPath
from Socket_Singleton import Socket_Singleton

basedir = os.path.dirname(__file__)

# def my_excepthook(type, value, tback):
#     # log the exception here

#     # then call the default handler
#     sys.__excepthook__(type, value, tback)

class DuplicatorClass(QMainWindow, Ui_MainWindow): #open ui from another py file that is converted from ui
    def __init__(self, *args, obj=None, **kwargs):
        super(DuplicatorClass,self).__init__(*args, **kwargs)
        self.setupUi(self)

# class DuplicatorClass(QMainWindow): #open ui by loading from ui file
#     def __init__(self):
#         super(DuplicatorClass,self).__init__()
#         loadUi("UI\Duplicator.ui",self)
        
        self.config_extract()

        #initialize parameters and variables that will be used
        self.folder_name.setReadOnly(True)
        self.path.setReadOnly(True)
        self.number.setValidator(QIntValidator())
        self.serverType = ""                                            #holds the server type
        self.pname = ""                                                 #path name of selected folder
        self.fname = ""                                                 #folder name of selected folder
        self.fsize = 0                                                  #file size
        self.VDSCPpath = ""                                             #output path name
        self.disk_space = {}                                            #available disk space, inside this will have {"Total","Used","Free"}, but we will only use free
        self.copies = 0                                                 #holds the number of files to be copied
        self.copied = 0                                                 #holds the number of coiped files
        self.space_needed = 0                                           #space needed (number of copies * fsize)
        self.able_copy = 0                                              #maximum number of copies able to accomodate the disk size
        self.duplicating = False                                        #indicator for duplication process
        self.PL = True                                                  #indicator for Part Library selection
        self.OCV = False                                                #indicator for OCV Library selection
        self.Pgm = False                                                #indicator for Program Library selection
        self.checked = []                                               #a list to store the catgories selected for program library
        self.bytesFormat = ["B","KB","MB","GB","TB"]                    #will be displayed based on the space calculated (1KB = 1024B and so on)
        self.setBtn()                                                   #enable or disable start and cancel button
        self.setSettingsBtn(self.serverType)                            #enable or disable settings button for V-Lib
        self.changebg()                                                 #change bg colour based on status
        self.progressBar.setValue(0)                                    #set progress bar value to 0 at the start
        
        #set actions on the UI
        self.server.currentIndexChanged.connect(self.set_default_path)  #default path will be set whenever a new server is chosen
        self.dnd.textChanged.connect(self.set_pname)                    #drag and drop(dnd) feature
        self.browse_folder.clicked.connect(self.browsefolder)           #open file explorer to select a source folder
        self.browse_path.clicked.connect(self.browsepath)               #open file explorer to select an output path
        self.path.textChanged.connect(self.find_disk_size)              #find available disk size when output path is selected
        self.path.textChanged.connect(self.calculate_copies)            #calculate maximum number of copies when output path is changed, depending on the disk space and source size
        self.folder_name.textChanged.connect(self.calculate_copies)     #calculate maximum number of copies when source is changed, depending on the disk space and source size
        self.number.textChanged.connect(self.calculate_copies)          #calculate maximum number of copies when number is changed, depending on the disk space and source size
        self.start.clicked.connect(self.start_clicked)                  #perform duplication when start button is clicked
        self.cancel.clicked.connect(self.cancelOpt)                     #cancel duplication when cancel button is clicked
        self.reset1.clicked.connect(self.resetSource)                   #reset source when clicked
        self.reset2.clicked.connect(self.resetOutput)                   #reset output path when clicked
        self.settingsbtn.clicked.connect(self.opensettings)             #open V-Lib settings dialog when pressed

    def config_extract(self):  #to extract every information from config file
        self.config_obj = configparser.ConfigParser(interpolation = None)
        self.config_obj.read("DuplicatorConfig.cfg")
        self.defaultpath = self.config_obj["default_path"]
        self.files_needed = self.config_obj["files_to_look_for"]
        self.queries = self.config_obj["query"]
        self.db = {}

        if self.config_obj.has_section("postgresql"):
            params = self.config_obj.items("postgresql")
            for param in params:
                self.db[param[0]] = param[1]
        else:
            raise Exception('Section {0} not found in the {1} file'.format("postgresql", "DuplicatorConfig.cfg"))
        
        self.PLpath = self.defaultpath["VLib_PL"]
        self.OCVpath = self.defaultpath["VLib_OCV"]
        self.Pgmpath = self.defaultpath["VLib_Pgm"]

    def opensettings(self):  #method to open settings dialog
        if self.serverType == "VLib":
            self.settings = vLibSettings.PgmLibSettings(self.checked, self.PL, self.OCV, self.Pgm)
            self.settings.buttonBox.accepted.connect(self.getsettings)
            self.settings.exec_()

    def getsettings(self):  #get user selection from settings dialog when closed
        self.checked = []
        self.OCV = False
        self.Pgm = False
        self.PL = False

        if self.settings.Part_OCV.isChecked():
            self.OCV = True
        elif self.settings.Part.isChecked():
            self.PL = True
        
        if self.settings.Pgm.isChecked():
            self.Pgm = True

            if self.settings.Program.isChecked():
                self.checked.append("program")

            if self.settings.ZHeight.isChecked():
                self.checked.append("ZHeight")

            if self.settings.Unpop.isChecked():
                self.checked.append("Unpop")

            if self.settings.CustomLocation.isChecked():
                self.checked.append("customLocation")

            if self.settings.SideCamera.isChecked():
                self.checked.append("sideCam")

            if self.settings.CenterPin.isChecked():
                self.checked.append("centerPin")
            
            if self.settings.IncludeTile.isChecked():
                self.checked.append("tile")
        
        if self.PL == False and self.OCV == False and self.Pgm == False:
            self.prompt_dialog("Error", "Please choose one or more options!")
            self.opensettings()
        elif self.pname != "":
            name, ext = os.path.splitext(self.pname)
            if ext == ".datj" and (self.PL or self.OCV) and self.Pgm == False:
                self.pname_list = self.find_exist_files()
            elif ext == ".plx" and self.Pgm:
                self.pname_list = self.find_exist_files()
            else:
                self.resetSource()
            self.FindFolderSize()

    def calculate_copies(self):  #method to calculate maximum number of copies
        if self.fsize != 0 and len(self.disk_space) != 0:
            copy_prev = -1
            for i in self.disk_space:
                self.able_copy = int(self.disk_space[i]/self.fsize)
                if copy_prev == -1:
                    copy_prev = self.able_copy
                if self.able_copy > copy_prev:
                    self.able_copy = copy_prev

            self.max_copies.setText("Maximum number of copies: " + str(self.able_copy))
        else:
            self.able_copy = 0
            self.max_copies.setText("Maximum number of copies: -")

        if self.number.text() == "+" or self.number.text() == "-":
            self.number.setText("")

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
            self.VDSCPpath = ""
            self.path.setText("")
            self.serverType = ""
            self.resetSource()
        
        elif self.server.currentIndex() == 1:
            self.serverType = "VDSPC"
            self.VDSCPpath = self.defaultpath["VDSPC"]
            self.path.setText(self.VDSCPpath)
            self.path.setDisabled(False)
            self.resetSource()

        elif self.server.currentIndex() == 2:
            self.serverType = "VLib"
            self.path.setText("Please click browse on the right...")
            self.path.setDisabled(True)
            self.resetSource()
        
        self.setSettingsBtn(self.serverType)



    def browsefolder(self): #setting source path name (pname) from file browsing
        if self.serverType == "VDSPC":
            self.pname=QFileDialog.getExistingDirectory(self, 'Select a folder', 'C:/vdspc_image_vone')

        elif self.serverType == "VLib":
            if (self.PL or self.OCV) and self.Pgm == False:
                self.pname=QFileDialog.getOpenFileName(self, 'Select a .datj file', 'C:/CPI/cad', "datj(*.datj)")[0]
            elif self.Pgm == True:
                self.pname=QFileDialog.getOpenFileName(self, 'Select a .plx file', 'C:/CPI/cad', "plx(*.plx)")[0]

        else:
            self.prompt_dialog("Warning","Please first choose a server")

        if self.pname != "" and self.serverType != "":
            self.set_fname()
        else:
            self.resetSource()

    def set_pname(self): #setting source path name (pname) from drag and drop
        if self.dnd.text() != "Drag and Drop" and self.serverType != "":
            self.pname = self.dnd.getFilePath()
            self.dnd.setText("Drag and Drop")
            self.checkdnd()
        elif self.dnd.text() != "Drag and Drop":
            self.dnd.setText("Drag and Drop")
            self.prompt_dialog("Warning", "Please first choose a server!")

    def checkdnd(self):  #check whether source droped in dnd is valid or not
        if self.serverType == "VDSPC":
            if os.path.isdir(self.pname):
                self.set_fname()
            else:
                self.prompt_dialog("Error", "Please Drag and Drop a folder!")
        elif self.serverType == "VLib":
            if os.path.isfile(self.pname):
                name, ext = os.path.splitext(self.pname)
                if (self.PL or self.OCV) and self.Pgm == False:
                    if ext == ".datj":
                        self.set_fname()
                    else:
                        self.prompt_dialog("Error", "Please Drag and Drop a .datj file!")
                elif self.Pgm == True:
                    if ext == ".plx":
                        self.set_fname()
                    else:
                        self.prompt_dialog("Error", "Please Drag and Drop a .plx file!")
            else:
                self.prompt_dialog("Error", "Please Drag and Drop the correct file!")
                


    def set_fname(self): #finding the source file/folder name and display in UI
        last_seperator = self.pname.rindex("/")
        self.fname = self.pname[last_seperator + 1:]
        self.folder_name.setText(self.fname)
        self.pname_list = []
        if self.serverType == "VDSPC":
            self.pname_list.append(self.pname)    
        elif self.serverType == "VLib":
            self.pname_list = self.find_exist_files()
        self.FindFolderSize()

    def find_exist_files(self):  #prepare a list of file  that will be duplicated and calculate size
        path_list = []
        print("Finding files...")

        #Part Library only
        if self.PL and self.OCV == False and self.Pgm == False:
            path_list.append(self.pname)
            name, ext = os.path.splitext(self.pname)
            path_list.append(name+".alt")
            if os.path.exists(self.defaultpath["CPM"]+ "/" + name.split("/")[-1]):
                path_list.append(self.defaultpath["CPM"]+ "/" + name.split("/")[-1])
            if os.path.exists(self.defaultpath["OCI"]+ "/" + name.split("/")[-1]):
                path_list.append(self.defaultpath["OCI"]+ "/" + name.split("/")[-1])

        #Part and OCV Library
        elif self.PL == False and self.OCV and self.Pgm == False:
            path_list.append(self.pname)
            name, ext = os.path.splitext(self.pname)
            path_list.append(name+".alt")
            if os.path.exists(self.defaultpath["CPM"]+ "/" + name.split("/")[-1]):
                path_list.append(self.defaultpath["CPM"]+ "/" + name.split("/")[-1])
            if os.path.exists(self.defaultpath["OCI"]+ "/" + name.split("/")[-1]):
                path_list.append(self.defaultpath["OCI"]+ "/" + name.split("/")[-1])
            path_list.append(self.defaultpath["VLib_OCV"] + "/" + self.fname.split(".")[0])

        #Program Library only
        elif self.PL == False and self.OCV == False and self.Pgm:
            print("fidning pgm fiels...")
            path_list.append(self.pname)
            name, ext = os.path.splitext(self.pname)
            for i in self.checked:
                if i == "Unpop":
                    if os.path.exists("C:/CPI/data/Unpop/"+self.fname.split(".")[0]+".hm"):
                        path_list.append("C:/CPI/data/Unpop/"+self.fname.split(".")[0]+".hm")
                
                elif i == "tile":
                    tilepath = "C:/CPI/tiles/"+self.fname.split(".")[0]+"_1.tile"
                    print("Tile path to look: ",tilepath)
                    if os.path.exists("C:/CPI/tiles/"+self.fname.split(".")[0]+"_1.tile"):
                        tile_file = open("C:/CPI/tiles/"+self.fname.split(".")[0]+"_1.tile")
                        for line in tile_file.readlines():
                            if line.find(".jpg") >= 0:
                                path_list.append("C:/CPI/" + line.split()[1])
                    else:
                        print("No tile image")

                else:
                    for j in self.files_needed[i].split(","):
                        if j == ".plx":
                            pass
                        elif os.path.exists(name+j):
                            path_list.append(name+j)

        #Part Library or OCV Library, together with Program Library
        elif (self.PL or self.OCV) and self.Pgm:
            name = self.fname.split(".")[0]
            map_file = open("C:/cpi/data/database_map.txt")
            for line in map_file.readlines():
                line_list = line.split()
                if name in line_list:
                    db = line_list[2]
                    break
            path_list.append("C:/cpi/"+db+"j")
            path_list.append("C:/cpi/"+db.split(".")[0]+".alt")

            if os.path.exists(self.defaultpath["CPM"]+ "/" + (db.split(".")[0]).split("/")[-1]):
                path_list.append(self.defaultpath["CPM"]+ "/" + (db.split(".")[0]).split("/")[-1])

            if os.path.exists(self.defaultpath["OCI"]+ "/" + (db.split(".")[0]).split("/")[-1]):
                path_list.append(self.defaultpath["OCI"]+ "/" + (db.split(".")[0]).split("/")[-1])

            if self.OCV:
                path_list.append(self.defaultpath["VLib_OCV"] + "/" + (db.split(".")[0]).split("/")[-1])
            
            path_list.append(self.pname)
            name, ext = os.path.splitext(self.pname)
            for i in self.checked:
                if i == "Unpop":
                    if os.path.exists("C:/CPI/data/Unpop/"+self.fname.split(".")[0]+".hm"):
                        path_list.append("C:/CPI/data/Unpop/"+self.fname.split(".")[0]+".hm")
                
                elif i == "tile":
                    tilepath = "C:/CPI/tiles/"+self.fname.split(".")[0]+"_1.tile"
                    print("Tile path to look: ",tilepath)
                    if os.path.exists("C:/CPI/tiles/"+self.fname.split(".")[0]+"_1.tile"):
                        tile_file = open("C:/CPI/tiles/"+self.fname.split(".")[0]+"_1.tile")
                        for line in tile_file.readlines():
                            if line.find(".jpg") >= 0:
                                path_list.append("C:/CPI/" + line.split()[1])
                    else:
                        print("No tile image")

                else:
                    for j in self.files_needed[i].split(","):
                        if j == ".plx":
                            pass
                        elif os.path.exists(name+j):
                            path_list.append(name+j)
                        
        print(path_list)
        return path_list


    def FindFolderSize(self): #find the size of source file/folder using thread to prevent UI freezing
        self.thread = QThread()
        self.worker = FindFileSizeWorker.FindFolderSize()
        self.worker.moveToThread(self.thread)
        self.worker.set_param(self.pname_list)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(lambda: self.getFolderSize(self.worker))
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.thread.wait)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.finished.connect(self.thread.deleteLater)
        self.thread.start()

    def getFolderSize(self, worker): #method used to retrieve source file/folder size from thread
        self.fsize = worker.getTotal()
        if self.fsize == -1:
            self.fsize = 0
            self.pname = ""
            self.fname = ""
            self.foldersize.setText("Folder/File size: -")
            self.prompt_dialog("Error", "Please choose a folder!")
            self.fsize = 0
            self.foldersize.setText("Folder/File size: -")

        else:
            self.calculate_copies()
            self.fsizedivided = self.fsize
            for i in self.bytesFormat:
                if self.fsizedivided > 1024:
                    self.fsizedivided = self.fsizedivided / 1024
                else:
                    self.foldersize.setText("Folder/File size: " + "{:.2f}".format(self.fsizedivided)+i)
                    break

    def browsepath(self): #setting output path from browsing
        #VDSPC only needs one path, a normal browsing will do
        if self.serverType == "VDSPC":
            self.VDSCPpath=QFileDialog.getExistingDirectory(self, 'Select a folder', 'D:/')
            if self.VDSCPpath != "":
                self.path.setText(self.VDSCPpath)
            else:
                self.resetOutput()

        #VLib has 3 paths (Part, OCV, Program), so need to open another dialog for browsing
        elif self.serverType == "VLib":
            self.chooseVlibPath = vLibPath.VLibSettings(self.PLpath, self.OCVpath, self.Pgmpath, self.duplicating)
            self.chooseVlibPath.buttonBox.accepted.connect(self.getVlibPath)
            self.chooseVlibPath.exec_()

    def getVlibPath(self):  #get the path of every source (Part, OCV, Programs) set in the path dialog, and find available disk size 
        self.PLpath = self.chooseVlibPath.partpath.text()
        self.OCVpath = self.chooseVlibPath.ocvpath.text()
        self.Pgmpath = self.chooseVlibPath.pgmpath.text()
        print(self.PLpath)
        print(self.OCVpath)
        print(self.Pgmpath)
        self.find_disk_size()

    def resetSource(self):  #reset source when clicked
        self.folder_name.setText("")
        self.foldersize.setText("Folder/File size: -")
        self.pname = ""
        self.fname = ""
        self.fsize = 0
        self.calculate_copies()

    def resetOutput(self):  #reset output path when clicked
        self.path.setText("")
        self.diskspace.setText("Free space: -")
        self.VDSCPpath = ""
        self.disk_space = {}
        self.calculate_copies()

    def find_disk_size(self): #method used to find disk size of selected output path
        self.disk_space = {}

        if self.serverType == "VDSPC":
            if self.VDSCPpath == "":
                self.diskspace.setText("Free space: ")
            else:
                space = FindFileSize.get_disk_size(self.VDSCPpath)
                self.disk_space[self.VDSCPpath[0]] = space["Free"]

        else:
            space = FindFileSize.get_disk_size(self.PLpath)
            self.disk_space[self.PLpath[0]] = space["Free"]
            space = FindFileSize.get_disk_size(self.OCVpath)
            self.disk_space[self.OCVpath[0]] = space["Free"]
            space = FindFileSize.get_disk_size(self.Pgmpath)
            self.disk_space[self.Pgmpath[0]] = space["Free"]
        print(self.disk_space)
        #at the end will get something like this: {"C": 123456} or {"C": 123456, "D": 1234567}
        txt = "Free space: "
        for i in self.disk_space:
            if list(self.disk_space.keys()).index(i) != 0:
                txt += "\t"
            txt += i +": " + "{:.2f}".format(self.disk_space[i]/1024/1024/1024)+"GB"
        self.diskspace.setText(txt)
        self.calculate_copies()
            
    def start_clicked(self): #conditions when start button is clicked
        #Check whether server source is chosen
        if self.server.currentText() == "--Please Choose--":
            self.prompt_dialog("Error","Please choose a server!")
        
        #check whether source is available
        elif self.pname == "":
            self.prompt_dialog("Error","Please choose a folder!")
        
        #check whether output path is set for VDSPC
        elif self.VDSCPpath == "" and self.serverType == "VDSPC":
            self.prompt_dialog("Error","Please choose an output path!")

        #check whether output path for Part Library is set when enabled
        elif self.PLpath == "" and self.serverType == "VLib" and self.PL == True:
            self.prompt_dialog("Error", "Please choose an output path for Part Library")

        #check whether output path for OCV Library is set when enabled
        elif (self.PLpath == "" or self.OCVpath == "") and self.serverType == "VLib" and self.OCV == True:
            self.prompt_dialog("Error", "Please choose an output path for Part or OCV Library")

        #check whether output path for Program Library is set when enabled
        elif self.Pgmpath == "" and self.serverType == "VLib" and self.Pgm == True:
            self.prompt_dialog("Error", "Please choose an output path for Program Library")

        #check whether a number is input or not
        elif self.number.text() == "0" or self.number.text() == "":
            self.prompt_dialog("Error","Please input number of copies!")

        #everything passes, run here
        else:
            if self.find_files_needed():  #one more check on the source, whether the neccassary files are present
                if self.check_available_space():  #check for whether available space is enough for duplication
                    self.duplicating = True       #indicates that duplication process started
                    
                    #run different duplication algorithm based on server type chosen
                    if self.serverType == "VDSPC":
                        self.setBtn()
                        self.disableEverything()
                        self.changebg()
                        self.DuplicateVDSPC()
                    
                    elif self.serverType == "VLib":
                        self.V_Lib_Check()
    
                else:  #duplication will not run if space is not enough
                    self.prompt_dialog("Error", "Not enough space!")

    def V_Lib_Check(self):  #check for user selection in VLib settings dialog, will run different duplication algo based on selection
        #Program only chosen
        if self.PL == False and self.OCV == False and self.Pgm == True:
            if self.checked != []:
                self.setBtn()
                self.changebg()
                self.disableEverything()
                self.DuplicatePgm()
            else:
                self.prompt_dialog("Error","Please select one or more categories in Program Settings!")
        
        #Part or OCV only chosen
        elif (self.PL or self.OCV) and self.Pgm == False:
            print("Run here")
            self.setBtn()
            self.changebg()
            self.disableEverything()
            self.DuplicatePL_OCV()

        #Part or OCV chosen, together with Program
        elif (self.PL or self.OCV) and self.Pgm == True:
            print("Running vlib")
            self.setBtn()
            self.changebg()
            self.disableEverything()
            self.DuplicateVlib()        

    def find_files_needed(self):  #method to look for neccassary files before duplication starts
        if self.serverType == "VDSPC":  #look for repairTicket_post.txt
            if os.path.isfile(self.pname+"/"+self.files_needed[self.serverType]):
                return True
            else:
                self.prompt_dialog("Error", self.files_needed[self.serverType]+" is not inside the source!")
                return False

        elif self.serverType == "VLib":
            if (self.OCV or self.PL) and self.Pgm == False:  #look for .datj and .alt file and OCV folder (if needed)
                name, ext = os.path.splitext(self.pname)
                vlib_files = self.files_needed[self.serverType].split(",")
                if ext != vlib_files[0]:
                    self.prompt_dialog("Error", vlib_files[0] +" is not selected!")
                    return False
                elif os.path.isfile(name+vlib_files[1]) == False:
                    self.prompt_dialog("Error", vlib_files[1] +" is not inside the source!")
                    return False
                elif self.OCV:
                    if os.path.exists(self.defaultpath["VLib_OCV"] + "/" + name.split("/")[-1]) == False:
                        self.prompt_dialog("Error", "OCV folder not found!")
                        return False
                    else:
                        return True
                else:
                    return True
            
            else: #look for .plx file
                name, ext = os.path.splitext(self.pname)
                if ext != ".plx":
                    self.prompt_dialog("Error","wrong file selected")
                    return False
                else:
                    return True


    def changebg(self): #method for changing bg colour when process starts and ends
        if self.duplicating:
            self.setStyleSheet("""QMainWindow{background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 rgba(170, 255, 127, 255), stop:0.875 rgba(255, 255, 255, 255));}""")
        else:
            self.setStyleSheet("""QMainWindow{background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 rgba(255, 255, 127, 255), stop:0.875 rgba(255, 255, 255, 255));}""")

    def check_available_space(self): #compare space needed with space available on disk
        if self.able_copy >= int(self.number.text()):
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
        self.worker.setParam(self.pname, self.copies, self.VDSCPpath)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(lambda: self.resetParam(start_time))
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(self.reportProgress)
        self.thread.start()

    def DuplicatePL_OCV(self): #Part or OCV Library duplication process using thread
        self.proMsg("In Progress")
        vlib_files = self.files_needed[self.serverType].split(",")
        start_time = time.time()
        self.copies = int(self.number.text())
        self.label_progress_num.setText("0/"+str(self.copies))
        self.progressBar.setValue(0)
        self.thread = QThread()
        self.worker = pl_ocvDuplicateWorker.DuplicateObject()
        self.worker.moveToThread(self.thread)
        self.worker.setParam(self.pname, self.copies, self.PLpath, self.db, vlib_files, self.queries, self.OCV, self.OCVpath, self.defaultpath)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(lambda: self.resetParam(start_time))
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(self.reportProgress)
        self.thread.start() 

    def DuplicatePgm(self):  #Program Library duplication process using thread
        self.proMsg("In Progress")
        start_time = time.time()
        self.copies = int(self.number.text())
        self.label_progress_num.setText("0/"+str(self.copies))
        self.progressBar.setValue(0)
        self.thread = QThread()
        self.worker = pgmDuplicateWorker.DuplicateObject()
        self.worker.moveToThread(self.thread)
        self.worker.setParam(self.pname, self.copies, self.Pgmpath, self.checked)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(lambda: self.resetParam(start_time))
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(self.reportProgress)
        self.thread.start() 

    def DuplicateVlib(self):  #Part or OCV Library with Program Library duplication process using thread
        vlib_files = self.files_needed[self.serverType].split(",")
        self.proMsg("In Progress")
        start_time = time.time()
        self.copies = int(self.number.text())
        self.label_progress_num.setText("0/"+str(self.copies))
        self.progressBar.setValue(0)
        self.thread = QThread()
        self.worker = vlibDuplicateWorker.DuplicateObject()
        self.worker.moveToThread(self.thread)
        self.worker.setParam(self.pname_list, self.copies, self.PLpath, self.OCVpath, self.Pgmpath, self.db, self.queries, self.checked, vlib_files, self.OCV, self.defaultpath)
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
            if self.serverType == "VLib" and self.Pgm:
                self.prompt_dialog("Finished","Duplication finished.\nTime elapsed: "+"{:.2f}".format(time.time()-start_time)+" seconds\nPlease refresh program in SmartG!")
            else:
                self.prompt_dialog("Finished","Duplication finished.\nTime elapsed: "+"{:.2f}".format(time.time()-start_time)+" seconds")
        else:
            self.proMsg("Cancelled")
            self.prompt_dialog("Cancelled","Duplication Cancelled.\nTime elapsed: "+"{:.2f}".format(time.time()-start_time)+" seconds")
        self.duplicating = False
        self.setBtn()
        self.changebg()
        self.disableEverything()
        self.progressBar.setValue(0)
        self.find_disk_size()
        self.calculate_copies()

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

    def setSettingsBtn(self, servertype):
        if servertype == "VLib":
            self.settingsbtn.setEnabled(True)
            self.settingsbtn.setStyleSheet("""QPushButton{background-color: rgb(0, 157, 235);}
                                              QPushButton:hover{background-color: rgb(85, 170, 255);}""")
        else:
            self.settingsbtn.setEnabled(False)
            self.settingsbtn.setStyleSheet("background-color: gray; color: rgb(0, 0, 0);")

    def disableEverything(self):  #disables input while duplicating
        disabledSS = "background-color: gray; color: rgb(0, 0, 0);"
        enabledSS = """QPushButton{background-color: rgb(0, 157, 235);}
                       QPushButton:hover{background-color: rgb(85, 170, 255);}"""
        if self.duplicating:
            self.server.setDisabled(True)
            self.settingsbtn.setDisabled(True)
            self.settingsbtn.setStyleSheet(disabledSS)
            self.dnd.setDisabled(True)
            self.browse_folder.setDisabled(True)
            self.browse_folder.setStyleSheet(disabledSS)
            self.reset1.setDisabled(True)
            self.reset1.setStyleSheet(disabledSS)
            if self.serverType == "VDSPC":
                self.browse_path.setDisabled(True)
                self.browse_path.setStyleSheet(disabledSS)
            self.reset2.setDisabled(True)
            self.reset2.setStyleSheet(disabledSS)

        else:
            self.server.setDisabled(False)
            self.settingsbtn.setDisabled(False)
            self.settingsbtn.setStyleSheet(enabledSS)
            self.dnd.setDisabled(False)
            self.browse_folder.setDisabled(False)
            self.browse_folder.setStyleSheet(enabledSS)
            self.reset1.setDisabled(False)
            self.reset1.setStyleSheet(enabledSS)
            if self.serverType == "VDSPC":
                self.browse_path.setDisabled(False)
                self.browse_path.setStyleSheet(enabledSS)
            self.reset2.setDisabled(False)
            self.reset2.setStyleSheet(enabledSS)

#opening a window with widgets
if __name__ == '__main__':
    Socket_Singleton()
    # sys.excepthook = my_excepthook
    app=QApplication(sys.argv)
    app.setWindowIcon(QIcon(os.path.join(basedir,'folder.ico')))
    mainwindow=DuplicatorClass()
    widget=QtWidgets.QStackedWidget()
    widget.addWidget(mainwindow)
    widget.setWindowTitle("Duplicator")
    widget.setFixedWidth(800)
    widget.setFixedHeight(600)
    widget.show()
    app.exec()
    
    
