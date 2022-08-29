import os
import shutil

src = 'C:/CPI/cad/AOITestBoard.datj'

def extractName(src):
    condition = '/'
    condition2 = '.'
    position = src.rindex(condition)
    position2 = src.rindex(condition2)

    DBName = src[position + 1 : position2]

    return(DBName)


def DuplicateFile(src):
    
    count = 0
    num = 0 

    while count <= 0:

        DBName = extractName(src)
        print(DBName)

        dest = 'D:/CPI/cad/' + DBName + '_' + str(num) + '.datj'

        print(dest)

        isdir = os.path.exists(dest)
        
        print(isdir)
        
        if isdir == True:
            num += 1
        
        else:
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            shutil.copyfile(src, dest)
            count += 1
            return (num)



def main(src):
    
    num = DuplicateFile(src)
    print(num)

main(src)
