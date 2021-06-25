# -*- coding: utf-8 -*-
import os
import pandas as pd
from time import sleep
from serial import Serial
from struct import unpack
from binascii import hexlify as hex2str
from binascii import unhexlify as str2hex
from threading import Thread
from datetime import timedelta, datetime as dt

from config import serial_info

def Flip(address):
    result = list()
    if type(address) != list:
        address = [address]
    for addr in address:
        flip = addr[6:8] + addr[4:6] + addr[2:4] + addr[0:2]
        result.append(flip)
    if len(result) == 1:
        result = str(result)[2:-2]
    return result

def CRC(address):
    return ('%x' %sum(str2hex('73FD52' + address + 'FFFFFFFF')))[-2:]

def Preprocessing(read_data, from_start, to_end):
    return str(hex2str(str2hex(read_data)[from_start:to_end]))[2:-1]

def ToCsv(path, file_name, read_data):
    file_name = self.time.strftime('%Y%m%d') + '_' + file_name
    
    df = pd.DataFrame([read_data], columns=['datetime', 'address', 'flow_rate', 'total_volume'])
    
    if not os.path.exists(path + file_name):
        df.to_csv(path + file_name, index=False, mode='w', encoding='utf-8-sig')
        
    else:
        df.to_csv(path + file_name, index=False, mode='a', encoding='utf-8-sig', header=False)

class Setup(): 
    def __init__(self, port, address, mode):
        
        # Serial communication parameter passing
        self.com          = Serial(port='/dev/ttyAMA0')
        self.ser          = Serial()
        self.ser.port     = port
        self.ser.baudrate = serial_info['baudrate']
        self.ser.bytesize = serial_info['bytesize']
        self.ser.stopbits = serial_info['stopbits']
        self.ser.parity   = serial_info['parity']
        self.ser.timeout  = serial_info['timeout']
        try:
            self.ser.open()
            self.com.open()
            
        except:
            pass
        
        self.mode = mode
        
        self.running = True
        self.address = '00000000'
        self.commands = {
            'select': None,
            'read'  : '107BFD7816'
        }
        
        self.AddressCheck(Flip(address))
        self.Threading()
        
    def AddressCheck(self, addresses):
        for address in addresses: 
            selection = '680B0B6873FD52' + address + 'FFFFFFFF' + CRC(address) + '16'
        
            for _ in range(3):
                self.ser.write(str2hex(selection))
                sleep(1)
                response = self.ser.read(1)
                if response == b'\xe5':
                    print('%s has been added !' %Flip(address))
                    self.commands['select'] = selection
                    break
                
                else:
                    print('Can not find the address..')
                    continue
                
            if self.commands['select'] != None:
                break
            
            else:
                self.running = False
                
    def Threading(self):
        self.thread  = Thread(target=self.run)
        self.thread.daemon = False
        self.thread.start()
    
    def run(self):
        while self.running:
            self.ser.write(str2hex(self.commands['select']))
            sleep(0.5)
            read_check = self.ser.read(1)

            if read_check == b'\xe5':
                self.ser.write(str2hex(self.commands['read']))
                sleep(0.5)
                
                read_raw = self.ser.read(39)
                read_data = hex2str(read_raw)
                if len(read_data) != 78:
                    ## Failure ##
                    continue

                self.time = dt.now() # .strftime('%Y.%m.%d %H:%M:%S') 
                self.address = Preprocessing(read_data, 7, 11)
                self.address = Flip(self.address)
                self.total_volume = Preprocessing(read_data, 21, 25)
                self.total_volume = Flip(self.total_volume)
                self.total_volume = str2hex(self.total_volume)
                self.total_volume = int(hex2str(self.total_volume), 16) / 1000
                self.flow_rate = Preprocessing(read_data, 27, 31)
                self.flow_rate = Flip(self.flow_rate[6:8])
                self.flow_rate = str2hex(self.flow_rate)
                self.flow_rate = unpack("!f", self.flow_rate)[0]

                self.read = [self.time, self.address, self.flow_rate, self.total_volume]
                
                ToCSV(path='gatering/', file_name='lxc.csv', read_data=self.read)
                             
                if self.mode == 'master': 
                    self.read_2 = self.com.read(39)
                    
                elif self.mode == 'slave':
                    self.com.write(read_raw)
                    
                # print(f'{self.time}  Address: {self.return_address}  Flow Rate: {self.flow_rate:11.6f}㎥/h  Total Volume: {self.total_volume:11.6f}㎥')

                # # DB Sender
                # sql = "INSERT INTO `%s` VALUES ('%s', '%s', '%f', '%f')" %('ufm-lxc', self.time, self.return_address, self.flow_rate, self.total_volume)
                # self.lxc_db.send(sql)

            else:
                # 날짜 및 시간 기록
                self.time = dt.now().strftime('%Y.%m.%d %H:%M:%S') 
                # print('%s   Address = %s   LXC Error' %(self.time, self.return_address))
                pass    