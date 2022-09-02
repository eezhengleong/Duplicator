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
        
        
    def setParam(self, pathname, copies, outname): #set parameter before run
        self.pathname, self.copies, self.outname = pathname, copies, outname
        self.copied = 0
        self.threadactive = True

    def run(self, params, file_list, queries): #method that will be executed when thread.start() is called
        self.conn = psycopg2.connect(**params)
        self.cur = self.conn.cursor()
        dbname = vlibDuplicate.extractName(self.pathname)
        for i in range(self.copies):
            if self.threadactive:
                name = vlibDuplicate.main(self.pathname, self.outname, dbname, file_list, self.conn, self.cur, queries["q4"])
                fam = self.create_fam(self.conn, self.cur, queries["q3"])
                dt = str(datetime.now(timezone.utc))

                q1 = queries["q1"]
                to_insert1 = (fam, dt)
                self.cur.execute(q1, to_insert1)

                q2 = queries["q2"]
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

    def create_fam(self, conn, cur, query):
        characters = string.ascii_letters + string.digits
        result_str = ''.join(random.choice(characters) for i in range(8))
        try:
            q = query
            cur.execute(q, (result_str,))
        except:
            self.create_fam(conn, cur)
        return result_str