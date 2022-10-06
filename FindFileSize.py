import os
import shutil
import sys
import logging

def my_excepthook(type, value, tback):
    # log the exception here

    # then call the default handler
    sys.__excepthook__(type, value, tback)



def get_dir_size(path='.'):
    total = 0
    if os.path.isdir(path):
        with os.scandir(path) as it:
            for entry in it:
                try:
                    if entry.is_file():
                        total += entry.stat().st_size
                    elif entry.is_dir():
                        total += get_dir_size(entry.path)
                except Exception as e:
                    print(e)
                    return -1
        return total
    else:
        try:
            return os.path.getsize(path)
        except:
            print("file not found")
            return 0

    
        

def get_disk_size(path='.'):
    disk_stat = shutil.disk_usage(path)
    disk_stat_dict = {"Total" : disk_stat[0], "Used" : disk_stat[1], "Free" : disk_stat[2] }
    return disk_stat_dict
