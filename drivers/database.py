import pymysql
from datetime import datetime


class Setup():
    def __init__(self, host, user, password, db):
        self.db = pymysql.connect(host=host, user=user, passwd=password, db=db, charset='utf8')
        self.cursor = self.db.cursor()
    
    def send(self, sql):
        self.cursor.execute(sql)
        self.db.commit()
        
    def close(self):
        self.db.close()
        
    def __del__(self):
        self.db.close()