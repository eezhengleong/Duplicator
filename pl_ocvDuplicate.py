from genericpath import exists
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

def DuplicateFile(src, output, dbname, file_list, conn, cur, q, ocv, ocv_path, defaultpath):
    
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
            cur.execute(q,(output.split("/")[-1] + "/" + dbname + "_" + str(num) + ".dat",))
            conn.commit()
            check = cur.fetchone()
            print("executed: ", check)
            print(check != None)
            if check != None:
                num+=1
                print("Library exists inside sql")
            else:
                for i in file_list:
                    try:
                        os.makedirs(os.path.dirname(dest+i), exist_ok=True)
                        shutil.copyfile(name+i, dest+i)
                    except:
                        print("File not found")
                        pass
                
                print("Finding for: ", defaultpath["CPM"], "/", name.split("/")[-1])
                if os.path.exists(defaultpath["CPM"] + "/" + name.split("/")[-1]):
                    print(defaultpath["CPM"], "/", name.split("/")[-1], "found!")
                    shutil.copytree(defaultpath["CPM"] + "/" + name.split("/")[-1], defaultpath["CPM"] + "/" + dbname + "_" + str(num))
                
                print("Finding for: ", defaultpath["OCI"], "/", name.split("/")[-1])
                if os.path.exists(defaultpath["OCI"] + "/" + name.split("/")[-1]):
                    print(defaultpath["OCI"], "/", name.split("/")[-1], "found!")
                    shutil.copytree(defaultpath["OCI"] + "/" + name.split("/")[-1], defaultpath["OCI"] + "/" + dbname + "_" + str(num))
                
                if ocv:
                    shutil.copytree(ocv_path+"/"+dbname, ocv_path+"/"+dbname+"_"+str(num))

                count += 1
                filename = output.split("/")[-1] + "/" + dbname + "_" + str(num) + ".dat"
                return filename

def main(src, output, dbname, file_list, conn, cur, q, ocv, ocv_path, defaultpath):
    filename = DuplicateFile(src, output, dbname, file_list, conn, cur, q, ocv, ocv_path, defaultpath)
    return filename

