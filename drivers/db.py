import pymysql
from datetime import datetime
from config import HOST
from config import USER
from config import PASSWORD
from config import DB
from config import TABLE

class Setup():
    def __init__(self):
        self.db = pymysql.connect(host=HOST, user=USER, passwd=PASSWORD, db=DB, charset='utf8')
        self.cursor = self.db.cursor()
    
    def send(self, sql):
        self.cursor.execute(sql)
        self.db.commit()
        
    def send_lxc(self, data):
        sql = f"INSERT INTO `{TABLE}` VALUES ('0', '{data[0]}', '{data[1]}', '{data[2]}', '{data[3]}')"
        self.cursor.execute(sql)
        self.db.commit()
        
    def close(self):
        self.db.close()
        
    def __del__(self):
        self.db.close()