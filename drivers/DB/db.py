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
    
    def send(self, table, key, time, address, flow_rate, total_volume):
        sql = f"INSERT INTO `{table}` VALUES ('{key}', '{time}', '{address}', '{flow_rate}', '{total_volume}')"
        self.cursor.execute(sql)
        self.db.commit()
        
    def close(self):
        self.db.close()
        
    def __del__(self):
        self.db.close()