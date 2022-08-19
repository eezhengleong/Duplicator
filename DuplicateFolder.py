# Python program to explain shutil.copytree() method
	
# importing os module
import os

# importing shutil module
import shutil

#importing time and date module
from datetime import date
from datetime import datetime

# path
path = 'C:/vdspc_image_vone'

# List files and directories
# in 'C:/vdspc_image_vone'
print("Before copying file:")
dirs = os.listdir(path)

#print all the detected folder in the directory path
for folder in dirs:
    print(folder)


# Source path
src = 'C:/vdspc_image_vone/AXI-EZLEONG-NB[@$@]2022-08-11-08-31-30'



#---------------------------------------------------------------------

cond = ']'

position = src.index(cond)

print(position)

date1 = src[position + 1:]
print(date1)

YYYY = int(date1[0:4])
MM = int(date1[5:7])
DD = int(date1[8:10])

HH = int(date1[11:13])
#MIN = int(date1[14:16])
MIN = 59
#SS = int(date1[17:19])
SS = 50
print("YYYY= ", YYYY)
print("MM= ", MM)
print("DD= ", DD)

print("HH= ", HH)
print("MM= ", MIN)
print("SS= ", SS)

#--------------------------------------------------------------------

for x in range(20):
    
    # Destination path
    dest = 'D:/vdspc_image_vone/' + str(YYYY) + '/' + str(MM).zfill(2) + '/' + str(DD).zfill(2) + '/AXI-EZLEONG-NB[@$@]2022-08-11-' + str(HH).zfill(2) + '-' + str(MIN).zfill(2) + '-' + str(SS).zfill(2)

    #-----------------------------------------------------------------------
    # Copy the content of
    # source to destination
    destination = shutil.copytree(src, dest)
    #SS1= int(SS)
    SS += 1
    if SS == 60:
        SS = 0
        MIN += 1
        
    if MIN == 60:
        MIN = 0
        HH += 1
    #SS= str(SS1)



    