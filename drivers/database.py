import pymysql
from datetime  import datetim
from config    import USE_DB

class Setup():
    def __init__(self, host, user, password, db, table):
        if USE_DB:
            self.db = pymysql.connect(host=host, user=user, passwd=password, db=db, charset='utf8')
            self.table = table
            self.cursor = self.db.cursor()
        
    def send(self, sql):
        self.cursor.execute(sql)
        self.db.commit()
        
    def close(self):
        self.db.close()