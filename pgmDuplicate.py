from operator import index
import os
import shutil, json

# programName = 'AOITestBoard'
# databaseName = 'AOITestBoard.datj'

source = 'C:/CPI/cad/AOITestBoard_1.plx'

userSelectionFromUI = ['program', 'sideCam', 'Unpop', 'customLocation', 'centerPin', 'ZHeight','tile']

# By program name
program = ['.plx', '.pls', '.skip', '.fid', '.epad', '.eplx', '.emask', '.empn', '.ehole', '.epin', '.epth', '.global', '.bss', '_block.skip'] 

sideCam = ['.scskip', '.sidedat'] 

Unpop = ['.npm2', '.npm'] 

customLocation = ['.vewloc', '.vewxloc'] 

centerPin = ['.ctc'] 

ZHeight = ['.plz', '.mza', '.zinfo'] 

existFile = []



def extractSRC(source):
    cond = '/'
    position = source.rindex(cond)
    plxName = source[position + 1:]
    source_path = source[:position]
    name, ext = os.path.splitext(plxName)
    return name, source_path

def check(selection, programName, progPath):
    for x in range(len(selection)):
        fileName = programName + selection[x]
        print(fileName)
        isdir = os.path.exists(progPath + '/' + fileName) #source path
        if isdir == True:
            existFile.append(selection[x])
    print(existFile)


def duplicateTile(progName, newName): #duplicate .tile file
    count=0
    tile_file = open('C:/CPI/tiles/' + progName + '_1.tile', 'r')

    while count < 1:
        for line in tile_file.readlines():
            if line.find('.jpg') >= 0:
                count += 1
                firstLine = line
                print(line)
                break
    tile_file.close()

    condition = '.jpg'
    position = firstLine.index(condition)
    print(position)
    tileName = firstLine[8:position - 6]
    print(tileName) 

    tile_file = open('C:/CPI/tiles/' + progName + '_1.tile', 'r')

    # stringList = tile_file.readlines()
    newContent = []
    for line in tile_file.readlines():
        line = line.replace(tileName, newName)
        newContent.append(line)
        # print(line)

    tile_file.close()
    
    os.makedirs(os.path.dirname('C:/CPI/tiles/' + newName + '_1.tile'), exist_ok=True)
    
    tile_file = open('C:/CPI/tiles/' + newName + '_1.tile', 'w')
    new_file_contents = "".join(newContent)
    tile_file.write(new_file_contents)
    tile_file.close
    return tileName


def duplicateTileImage(tileName, newName):
    dir_list = os.listdir('C:/CPI/tiles')
    for name in dir_list:
        index_list = []
        print(name)
        for i in range (len(name)):
            if name[i] == '_':
                index_list.append(str(i))
        print(index_list)
        position = index_list[len(index_list) - 3 : len(index_list) - 2]
        if (len(position) != 0):
            print(position[0])
            extractName = name[:int(position[0])]
            extractNumber = name[int(position[0]):]
            print(extractName)
            print(extractNumber)
            if extractName == tileName and name.endswith('.tile') == False:
                newTileName = newName + extractNumber
                os.makedirs(os.path.dirname('C:/CPI/tiles/' + newTileName), exist_ok=True)
                shutil.copyfile('C:/CPI/tiles/' + name, 'C:/CPI/tiles/' + newTileName)

def checkFile(userSelectionFromUI, progName, newName, progPath):

    numberOfSelection = len(userSelectionFromUI)
    for x in range(numberOfSelection):
        if userSelectionFromUI[x] == 'program':
            check(program, progName, progPath)
        
        elif userSelectionFromUI[x] == 'sideCam':
            check(sideCam, progName, progPath)

        elif userSelectionFromUI[x] == 'Unpop':
            check(Unpop, progName, progPath)
            isdir = os.path.exists('C:/CPI/data/Unpop/' + progName + '.hm')
            if isdir == True:
                os.makedirs(os.path.dirname('C:/CPI/data/Unpop/' + newName + '.hm'), exist_ok=True)
                shutil.copyfile('C:/CPI/data/Unpop/' + progName + '.hm', 'C:/CPI/data/Unpop/' + newName + '.hm')
            
        elif userSelectionFromUI[x] == 'customLocation':
            check(customLocation, progName, progPath)

        elif userSelectionFromUI[x] == 'centerPin':
            check(centerPin, progName, progPath)

        elif userSelectionFromUI[x] == 'ZHeight':
            check(ZHeight, progName, progPath)

        elif userSelectionFromUI[x] == 'tile':
            isdir = os.path.exists('C:/CPI/tiles/' + progName + '_1.tile')
            if isdir == True:
                return True
            else:
                print('No tile image') #prompt error message
            
def produceName(progName, output):
    count = 0
    x = 0
    while count < 1:

        newName = progName + '_' + str(x) + '.plx'
        print(newName)
        
        isdir = os.path.exists(output + '/' + newName) #output path
        #print(isdir)
        if isdir == False:
            count += 1
            name, ext = os.path.splitext(newName)
            #print(newName)
            return(name)

        else:
            x += 1


                
def duplicateFile(progName, newName, existFile, progPath, output):
    shutil.copyfile(progPath + '/' + progName + ".plx",output + '/' + newName + ".plx")
    for x in range(len(existFile)):

        # newName = produceName(existFile[x])
        if existFile[x] == ".plx":
            continue
        # print(newName)
        src = progPath + '/' + progName + existFile[x] #source path
        dest = output + '/' + newName + existFile[x] #output path
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        try:
            shutil.copyfile(src, dest)
        except:
            pass
        if existFile[x] == ".global":
            with open(output + '/' + newName + existFile[x], "r+") as f: #output path
                data = json.load(f)
                data["program_name"] = newName
                f.seek(0)
                json.dump(data, f)
                f.truncate()
        print(dest)

def main(source, userSelectionFromUI, output):
    progName, progPath = extractSRC(source)
    newName = produceName(progName, output)
    flag = checkFile(userSelectionFromUI, progName, newName, progPath)
    print(flag)
    duplicateFile(progName, newName, existFile, progPath, output)
    if flag == True:
        tileName = duplicateTile(progName, newName)
        duplicateTileImage(tileName, newName)

    return newName





    

