import os
import shutil

def get_dir_size(path='.'):
    total = 0
    with os.scandir(path) as it:
        for entry in it:
            if entry.is_file():
                total += entry.stat().st_size
            elif entry.is_dir():
                total += get_dir_size(entry.path)
    return total

def get_disk_size(path='.'):
    disk_stat = shutil.disk_usage(path)
    disk_stat_dict = {"Total" : disk_stat[0], "Used" : disk_stat[1], "Free" : disk_stat[2] }
    return disk_stat_dict
