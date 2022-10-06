#subclassing object and use moveToThread to let the thread handle this process

from PyQt5.QtCore import QObject, pyqtSignal
import vlibDuplicate, psycopg2, random, string
from datetime import datetime, timezone

class DuplicateObject(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)

    def __init__(self): #class constructor
        super(DuplicateObject, self).__init__()
        
    def setParam(self, source, copies, plpath, ocvpath, pgmpath, params, queries, selection, file_list, ocv, defaultpath): #set parameter before run
        self.source, self.copies, self.plpath, self.ocvpath, self.pgmpath, self.params, self.queries, self.selection, self.file_list, self.ocv, self.defaultpath = source, copies, plpath, ocvpath, pgmpath, params, queries, selection, file_list, ocv, defaultpath
        self.copied = 0
        self.threadactive = True

    def run(self): #method that will be executed when thread.start() is called
        self.conn = psycopg2.connect(**self.params)
        self.cur = self.conn.cursor()
        pgm, db, dbname = "", "", ""
        for i in self.source:
            if ".plx" in i:
                pgm = i
            if ".datj" in i:
                db = i
                dbname = (i.split("/")[-1]).split(".")[0]
            if pgm != "" and db != "":
                break
        
        for i in range(self.copies):
            if self.threadactive:
                database, program = vlibDuplicate.main(pgm, db, dbname, self.plpath, self.ocvpath, self.pgmpath, self.conn, self.cur, self.queries["q4"],self.selection, self.file_list, self.ocv, self.defaultpath)
                fam = self.create_fam(self.conn, self.cur, self.queries["q3"], self.ocv)
                dt = str(datetime.now(timezone.utc))

                q1 = self.queries["q1"]
                to_insert1 = (fam, dt)
                self.cur.execute(q1, to_insert1)

                q2 = self.queries["q2"]
                to_insert2 = (fam, database, dt)
                self.cur.execute(q2, to_insert2)

                self.conn.commit()
                self.copied = i + 1
                self.progress.emit(self.copied)
                print("Appending into database_map")
                with open ("C:/CPI/data/database_map.old", "a") as f:
                    f.write("m " + program + " " + database + " \n")
                    f.close()

                with open ("C:/CPI/data/database_map.txt", "a") as f:
                    f.write("m " + program + " " + database + " \n")
                    f.close()
                try:
                    with open("C:/CPI/cad/"+program+".fid", "r+") as f:
                        old = f.readlines()
                        for i in range (0,len(old)):
                            if "Map_database" in old[i]:
                                old[i] = "Map_database " + database + "\n"
                        f.seek(0)
                        f.write("".join(old))
                        f.close()
                except:
                    print("No fid file")
                    pass
            else:
                break
        self.finished.emit()

    def cancel(self): #stopping the duplication process when cancel is selected
        print("cancelling")
        self.threadactive = False

    def create_fam(self, conn, cur, query,  ocv):
        characters = string.ascii_letters + string.digits
        if ocv:
            result_str ="OCV_" + ''.join(random.choice(characters) for i in range(8))
        else:
            result_str ="PL_" + ''.join(random.choice(characters) for i in range(8))
        try:
            q = query
            cur.execute(q, (result_str,))
        except:
            self.create_fam(conn, cur)
        return result_str