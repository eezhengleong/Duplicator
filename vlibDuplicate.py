import os
from queue import Empty
import shutil

def extractName(src):
    condition = '/'
    condition2 = '.'
    position = src.rindex(condition)
    position2 = src.rindex(condition2)

    DBName = src[position + 1 : position2]

    return(DBName)

def DuplicateFile(src, output, dbname, file_list, conn, cur, q):
    
    count = 0
    num = 0 

    while count <= 0:
        name, ext = os.path.splitext(src)
        dest = output + '/' + dbname + '_' + str(num)

        #print(dest)

        isdir = os.path.exists(dest+".datj")
        
        #print(isdir)
        
        if isdir == True:
            num += 1
        
        else:
            cur.execute(q,("cad/" + dbname + "_" + str(num) + ".dat",))
            conn.commit()
            check = cur.fetchone()
            print("executed: ", check)
            print(check != None)
            if check != None:
                num+=1
                print("Library exists inside sql")
            else:
                for i in file_list:
                    os.makedirs(os.path.dirname(dest+i), exist_ok=True)
                    shutil.copyfile(name+i, dest+i)

                count += 1
                filename = "cad/" + dbname + "_" + str(num) + ".dat"
                return filename

def main(src,output, dbname, file_list, conn, cur, q):
    filename = DuplicateFile(src, output, dbname, file_list, conn, cur, q)
    return filename

