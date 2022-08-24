import os
import shutil
import time

#src = 'C:/vdspc_image_vone/AXI-EZLEONG-NB[@$@]2022-08-15-08-43-26'


def searchLine(src, search_phrase): # function used to find out the line location of the 4 phrases
    f = open(src, 'r')
    line_num = 0
    for line in f.readlines():
        line_num += 1
        if line.find(search_phrase) >= 0:
            print(line_num)
            return (line_num)                     
    f.close()

def checkTime(Secs, Mins, Hours):
    if Secs == 60:
        Secs = 00
        Mins += 1

    if Mins == 60:
        Mins = 00
        Hours += 1
    
    return(Secs, Mins, Hours)
    

def editFile(dest, stringList):
    txt_file = open(dest, 'w')
    new_file_contents = "".join(stringList)
    txt_file.write(new_file_contents)
    txt_file.close



def editLine(TXTYear, TXTMonth, TXTDay, TXTHour, TXTMins, TXTSecs, dest, line_num, x):
    txt_file = open(dest, 'r')
    stringList =  txt_file.readlines()
    txt_file.close()
    line = stringList[line_num[x] - 1]
    condition = '='
    position = line.index(condition)
    beforeDate = line[:position+2]
    dateTime = line[position + 2 :]

    if x==0:
        TXTSecs -= 1
        if TXTSecs == -1:
            TXTSecs = 59
            TXTMins -= 1
        
        if TXTMins == -1:
            TXTMins == 59
            TXTHour -= 1

        stringList[line_num[x] - 1] = beforeDate + str(TXTYear).zfill(2) + '-' + str(TXTMonth).zfill(2) + '-' + str(TXTDay).zfill(2) + '-' + str(TXTHour).zfill(2) + '-' + str(TXTMins).zfill(2) + '-' + str(TXTSecs).zfill(2) + '\n'
        editFile(dest, stringList)


    elif x==1:
        stringList[line_num[x] - 1] = beforeDate + str(TXTYear).zfill(2) + '-' + str(TXTMonth).zfill(2) + '-' + str(TXTDay).zfill(2) + '-' + str(TXTHour).zfill(2) + '-' + str(TXTMins).zfill(2) + '-' + str(TXTSecs).zfill(2) + '\n'
        editFile(dest, stringList)

    elif x==2:
        TXTSecs += 1
        TXTSecs, TXTMins, TXTHour = checkTime(TXTSecs, TXTMins, TXTHour)
        stringList[line_num[x] - 1] = beforeDate + str(TXTYear).zfill(2) + '-' + str(TXTMonth).zfill(2) + '-' + str(TXTDay).zfill(2) + '-' + str(TXTHour).zfill(2) + '-' + str(TXTMins).zfill(2) + '-' + str(TXTSecs).zfill(2) + '\n'
        editFile(dest, stringList)
    
    elif x==3:
        TXTSecs += 1
        TXTSecs, TXTMins, TXTHour = checkTime(TXTSecs, TXTMins, TXTHour)
        TXTSecs += 1
        TXTSecs, TXTMins, TXTHour = checkTime(TXTSecs, TXTMins, TXTHour)
        stringList[line_num[x] - 1] = beforeDate + str(TXTYear).zfill(2) + '-' + str(TXTMonth).zfill(2) + '-' + str(TXTDay).zfill(2) + '-' + str(TXTHour).zfill(2) + '-' + str(TXTMins).zfill(2) + '-' + str(TXTSecs).zfill(2) + '\n'
        editFile(dest, stringList)

    txt_file.close

    
def DateAndTime(src):
    
    cond = ']'
    cond1 = '/'

    position = src.index(cond)
    position1 = src.rindex(cond1)

    print(position)
    print(position1)

    date1 = src[position + 1:]
    print(date1)

    frontName = src[position1 + 1 : position +1]
    print(frontName)

    YYYY = int(date1[0:4])
    MM = int(date1[5:7])
    DD = int(date1[8:10])

    HH = int(date1[11:13])
    MIN = int(date1[14:16])
    SS = int(date1[17:19])
    formating = [YYYY, MM, DD, HH, MIN, SS, frontName]

    return formating

def duplicateFolder(YYYY, MM, DD, HH, MIN, SS, frontName, src, opath):

    count = 0
    while count <= 0:
    # Destination path
        dest = opath + '/' + str(YYYY) + '/' + str(MM).zfill(2) + '/' + str(DD).zfill(2) + '/' + frontName + str(YYYY).zfill(2) + '-' + str(MM).zfill(2) + '-' + str(DD).zfill(2) + '-' + str(HH).zfill(2) + '-' + str(MIN).zfill(2) + '-' + str(SS).zfill(2)

        isdir = os.path.isdir(dest)

        if isdir == True:
            SS += 1
            SS, MIN, HH = checkTime(SS, MIN, HH)

        else: 
            shutil.copytree(src, dest) 
            count += 1
            return (dest)

def find_param(src):
    phrase = ['Panel insp start time', 'Panel insp end time', 'Board revision', 'Review start time']
    lineList = []
    for x in range (4):
        line = searchLine(src + "/repairTicket_post.txt", phrase[x])
        lineList.append(line)
    print(lineList)
    formating = DateAndTime(src)
    return (lineList, formating)

def main(src, opath, lineList, formating):

    dest = duplicateFolder(formating[0], formating[1], formating[2], formating[3], formating[4], formating[5], formating[6], src, opath)
    # count += 1

    print(dest)

    TXTYear, TXTMonth, TXTDay, TXTHour, TXTMins, TXTSecs, XX = DateAndTime(dest)

    print(TXTYear)
    print(TXTMonth)
    print(TXTDay)
    print(TXTHour)
    print(TXTMins)
    print(TXTSecs)

    for x in range(4):

        editLine(TXTYear, TXTMonth, TXTDay, TXTHour, TXTMins, TXTSecs, dest + '/repairTicket_post.txt', lineList, x)
