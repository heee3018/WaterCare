# -*- coding: utf-8 -*-
import os
import pandas as pd
from time      import sleep
from serial    import Serial
from struct    import unpack
from binascii  import hexlify as hex2str
from binascii  import unhexlify as str2hex
from threading import Thread, Lock
from datetime  import timedelta, datetime as dt
from config    import serial_info, send_to_db, save_as_csv, detected_addresses
        
def Flip(address):
    result = list()
    if address == None:
        return '00000000'
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

def ReadData(read_data, from_start, to_end):
    return str(hex2str(str2hex(read_data)[from_start:to_end]))[2:-1]

def toCSV(path, file_name, save_data):    
    df = pd.DataFrame([save_data], columns=['datetime', 'address', 'flow_rate', 'total_volume'])
    
    if not os.path.exists(path + file_name):
        df.to_csv(path + file_name, index=False, mode='w', encoding='utf-8-sig')
        
    else:
        df.to_csv(path + file_name, index=False, mode='a', encoding='utf-8-sig', header=False)

def SelectCommand(addresses):
    result = list()
    for address in addresses:
        result.append('680B0B6873FD52' + address + 'FFFFFFFF' + CRC(address) + '16')
    
    return result


class Setup(): 
    def __init__(self, port, addresses, mode):
        self.ser          = Serial()
        self.ser.port     = port                    # Default : '/dev/ttyUSB*'
        self.ser.baudrate = serial_info['baudrate'] # Default : 2400
        self.ser.bytesize = serial_info['bytesize'] # Default : 8
        self.ser.stopbits = serial_info['stopbits'] # Default : 1
        self.ser.parity   = serial_info['parity']   # Default : 'E'
        self.ser.timeout  = serial_info['timeout']  # Default : 1
        
        if not self.ser.is_open:
            self.ser.open()
                
        self.buf = {
            'time'         : None,
            'address'      : None,
            'flow_rate'    : None,
            'total_volume' : None
        }

        self.mode        = mode
        self.address     = self.SelectAddress(addresses)
        self.select_cmd  = '680B0B6873FD52' + Flip(self.address) + 'FFFFFFFF' + CRC(Flip(self.address)) + '16'
        self.read_cmd    = '107BFD7816'
        
        if self.address != None:
            self.StartThreading() 
            
        elif self.address == None:
            self.ser.close() 
            print("Threading could not start because the address could not be found.")
            
    def SelectAddress(self, addresses):
        inverted_addresses = Flip(addresses)
        selected_address   = None
        repeat             = True
        repeat_count       = 1
        send_and_receive   = True
        
        while repeat:
            for _ in range(repeat_count):
                for inverted_address in inverted_addresses: 
                    for detected_address in detected_addresses:
                        if inverted_address == detected_address:
                            print("The address is already connected.")
                            send_and_receive = False
                            break
                        elif inverted_address != detected_address:
                            send_and_receive = True
                            pass
                        
                    if send_and_receive is True:
                        select_command = '680B0B6873FD52' + inverted_address + 'FFFFFFFF' + CRC(inverted_address) + '16'
                        self.ser.write(str2hex(select_command))
                        response = self.ser.read(1)
                        if response == b'\xe5':
                            print('%s has been added !' %Flip(inverted_address))
                            self.select_cmd  = select_command
                            selected_address = Flip(inverted_address)
                            detected_addresses.append(inverted_address)
                            repeat = False
                            break
                        
                        elif response != b'\xe5': 
                            print('%s is not found...' %Flip(inverted_address))
                            continue
                        
                    send_and_receive = True
            
                if selected_address == None:
                    print('Address not found, Try again.')
            
            repeat = False    
            
        return selected_address
     
    def StartThreading(self):        
        self.running       = True
        self.thread        = Thread(target=self.run)
        self.thread.daemon = False
        self.thread.start()
    
    def run(self):
        while self.running:
            self.ser.write(str2hex(self.select_cmd))
            response = self.ser.read(1)
            if response != b'\xe5':
                self.buf['time']         = dt.now()
                self.buf['address']      = None
                self.buf['flow_rate']    = None
                self.buf['total_volume'] = None
                
            elif response == b'\xe5':
                for _ in range(10):
                    self.ser.write(str2hex(self.read_cmd))
                    read_raw_data = self.ser.read(39)
                    read_data = hex2str(read_raw_data)
                    
                    if len(read_data)/2 != 39:
                        continue # ==> Skip the code below and move on to the next one.

                    current_time = dt.now()# .strftime('%Y.%m.%d %H:%M:%S') 
                    self.buf['time'] = current_time 
                    address = ReadData(read_data, 7, 11)
                    self.buf['address'] = Flip(address)
                    flow_rate = ReadData(read_data, 27, 31)
                    flow_rate = Flip(flow_rate[6:8])
                    flow_rate = str2hex(flow_rate)
                    if flow_rate == b'\x00':
                        self.buf['flow_rate'] = 0.0
                    else:
                        self.buf['flow_rate'] = unpack("!f", flow_rate)[0]
                    total_volume = ReadData(read_data, 21, 25)
                    total_volume = Flip(total_volume)
                    total_volume = str2hex(total_volume)
                    if total_volume == b'\x00':
                        self.buf['total_volume'] = 0.0
                    else:
                        self.buf['total_volume'] = int(hex2str(total_volume), 16) / 1000
                    
                    if save_as_csv is True:
                        save_data = [
                            self.buf['time'], 
                            self.buf['address'], 
                            self.buf['flow_rate'],
                            self.buf['total_volume'] 
                        ]
                        
                        file_name = current_time.strftime('%Y_%m_%d') + '.csv'
                        toCSV(path='gathering/', file_name=file_name, save_data=save_data)
                    
                    if send_to_db is True:
                        pass                    
                        sql = "INSERT INTO `%s` VALUES ('%s', '%s', '%f', '%f')" %(
                            'ufm-lxc', 
                            self.buf['time'], 
                            self.buf['address'], 
                            self.buf['flow_rate'], 
                            self.buf['total_volume'])
                        # self.lxc_db.send(sql)
                    
                    # if self.mode == 'master': 
                    #     self.read_2 = self.com.read(39)
                        
                    # elif self.mode == 'slave':
                    #     self.com.write(read_raw)
                        
                    # print(f'{self.time}  Address: {self.return_address}  Flow Rate: {self.flow_rate:11.6f}㎥/h  Total Volume: {self.total_volume:11.6f}㎥')
