#subclassing object and use moveToThread to let the thread handle this process

from unittest import result
from PyQt5.QtCore import QObject, pyqtSignal
import vlibDuplicate, psycopg2, random, string, configparser
from datetime import datetime, timezone

class DuplicateObject(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)

    def __init__(self): #class constructor
        super(DuplicateObject, self).__init__()
        
        
    def setParam(self, pathname, copies, outname, params, file_list, queries, ocv, ocv_path): #set parameter before run
        self.pathname, self.copies, self.outname, self.params, self.file_list, self.queries, self.OCV, self.OCVpath = pathname, copies, outname, params, file_list, queries, ocv, ocv_path
        self.copied = 0
        self.threadactive = True

    def run(self): #method that will be executed when thread.start() is called
        self.conn = psycopg2.connect(**self.params)
        self.cur = self.conn.cursor()
        dbname = vlibDuplicate.extractName(self.pathname)
        for i in range(self.copies):
            if self.threadactive:
                name = vlibDuplicate.main(self.pathname, self.outname, dbname, self.file_list, self.conn, self.cur, self.queries["q4"],self.OCV, self.OCVpath)
                fam = self.create_fam(self.conn, self.cur, self.queries["q3"], self.OCV)
                dt = str(datetime.now(timezone.utc))

                q1 = self.queries["q1"]
                to_insert1 = (fam, dt)
                self.cur.execute(q1, to_insert1)

                q2 = self.queries["q2"]
                to_insert2 = (fam, name, dt)
                self.cur.execute(q2, to_insert2)

                self.conn.commit()
                self.copied = i + 1
                self.progress.emit(self.copied)
            else:
                break
        self.finished.emit()
        self.cur.close()
        self.conn.close()

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