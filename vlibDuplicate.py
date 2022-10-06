from distutils import filelist
import os, shutil, pl_ocvDuplicate, pgmDuplicate

from pgmDuplicate import produceName

def main(pgm, db, dbname, plpath, ocvpath, pgmpath, conn, cur, q, selection, file_list, ocv, defaultpath):
    program = pgmDuplicate.main(pgm, selection, pgmpath)
    database = pl_ocvDuplicate.main(db, plpath, dbname, file_list, conn, cur, q, ocv, ocvpath, defaultpath)
    return database, program
    # newpgmname = producePgmName(pgmname, pgmpath)
    # newdbname = produceDbName(dbname, plpath, conn, cur, q)
    # duplicatemethod(source, newpgmname, newdbname, plpath, ocvpath, pgmpath)

def duplicatemethod(source, newpgmname, newdbname, plpath, ocvpath, pgmpath):
    for i in source:
        if i.split(".")[-1] == "datj" or i.split(".")[-1] == "alt":
            shutil.copyfile(i, plpath + "/" + newdbname + i.split(".")[-1])
        elif os.path.exists(i+"/model_info.ocv"):
            shutil.copytree(i, ocvpath + "/" + newdbname)
        else:
            pass

def producePgmName(pgmname, pgmpath):
    count = 0
    while True:
        newName = pgmname + "_" + str(count)
        if os.path.exists(pgmpath + "/" + newName + ".plx") == False:
            return newName
        else:
            count += 1

def produceDbName(dbname, plpath, conn, cur, q):
    count = 0
    while True:
        newName = dbname + "_" + str(count)
        if os.path.exists(plpath + "/" + newName + ".datj"):
            count += 1
        else:
            cur.execute(q,("cad/" + newName + ".dat",))
            conn.commit()
            check = cur.fetchone()
            if check != None:
                print("Library exists inside SQL")
                count += 1
            else:
                return newName

