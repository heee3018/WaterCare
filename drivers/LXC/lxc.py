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

"""
# Condition
1. 주어진 주소 목록에서 해당되는 주소를 찾음
    감지된 주소가 "1개" 이거나 "2개 이상"인 경우를 구분하지 않고 코딩
2. 아무런 주소가 감지되지 않으면 __init__에서 None을 반환하고 넘어감
3. Sensor값을 main.py에서 사용할 수 있도록 Class 내부 변수에 저장
4. 터미널 출력, CSV 저장, DB 전송, AP간 데이터 공유 등 
    모든 기능은 main.py에 구현
"""

class Setup(): 
    def __init__(self, name, port, addresses, mode):
        self.ser              = Serial()
        self.ser.port         = port                     # Default : '/dev/ttyUSB*'
        self.ser.baudrate     = serial_info['baudrate']  # Default : 2400
        self.ser.bytesize     = serial_info['bytesize']  # Default : 8
        self.ser.stopbits     = serial_info['stopbits']  # Default : 1
        self.ser.parity       = serial_info['parity']    # Default : 'E'
        self.ser.timeout      = serial_info['timeout']   # Default : 1
        
        self.usb_num          = name
        self.mode             = mode     # 'master', 'slave', 'debug'
        self.address          = dict()
        self.read_cmd         = '107BFD7816'
        
        self.SelectAddress(addresses)
        
        while not self.ser.is_open:
            try:
                self.ser.open()
            except:
                self.ser.close()
                print(f"{self.usb_num} Check the USB connection..")
                return None
            
        print(f"{self.usb_num} / {self.mode} / {self.address}")
        
        if '99999999' not in list(self.address.keys()):
            print(f"{self.usb_num} Found the address!")
            print(f"{list(self.address.keys())}")
            self.StartThreading() 
            
        elif '99999999' in list(self.address.keys()):
            sleep(1)
            print(f"{self.usb_num} Address not found")
            
            # print("Threading could not start because the address not be found.")
        
        
        
    def SelectAddress(self, addresses):
        inverted_addresses = Flip(addresses)  # Flip Input Addresses
        repeat             = 1                # number of repeat      
        
        for _ in range(repeat):
            # Select the Fliped addresses one by one
            for inverted_address in inverted_addresses:  
                # Check if the flipped address is in the list of detected addresses
                if inverted_address in detected_addresses:
                    # print("The address is already connected.")
                    continue # go to next address
                
                # else if inverted_address not in detected_addresses
                select_command = '680B0B6873FD52' + inverted_address + 'FFFFFFFF' + CRC(inverted_address) + '16'

                try:
                    self.ser.write(str2hex(select_command))
                    
                    response = self.ser.read(1)
                    
                    if response == b'\xe5':
                        # print('%s has been added !' %Flip(inverted_address))
                        detected_addresses.append(inverted_address)  # Add to Detected Address
                        self.address[Flip(inverted_address)] = {'select_cmd': select_command,
                                                                'time':         dt.now().strftime('%Y.%m.%d %H:%M:%S'),
                                                                'address':      Flip(inverted_address),
                                                                'flow_rate':    0.0,
                                                                'total_volume': 0.0}
                    
                    elif response != b'\xe5': 
                        # print('%s is not found...' %Flip(inverted_address))
                        continue        
            
                except:
                    pass
                    #print(f"{self.usb_num} {Flip(inverted_address)} ser.write Error")
                    
        if self.address == {}:
            # if nothing
            self.address['99999999'] = {'select_cmd': 'Select command not found',
                                        'time':         dt.now().strftime('%Y.%m.%d %H:%M:%S'),
                                        'address':     '99999999',
                                        'flow_rate':    9.999999,
                                        'total_volume': 9.999999}
        
            
            
    def StartThreading(self):
        self.running       = True
        self.thread        = Thread(target=self.CommonThread)
        self.thread.daemon = False
        self.thread.start()
            
                  
            
    def CommonThread(self):
        while self.running:
            for address in list(self.address.keys()):
                
                select_command = self.address[address]
                self.ser.write(str2hex(select_command))
                response = self.ser.read(1)
                
                if response != b'\xe5':
                    self.address[address]['time']         = dt.now().strftime('%Y.%m.%d %H:%M:%S')
                    self.address[address]['address']      = address
                    self.address[address]['flow_rate']    = 9.999999
                    self.address[address]['total_volume'] = 9.999999
                    
                elif response == b'\xe5':
                    if len(list(self.address.keys())) == 1:
                        repeat = 10
                    else:
                        repeat = 1
                        
                    for _ in range(repeat):
                        self.ser.write(str2hex(self.read_cmd))
                        read_raw_data = self.ser.read(39)
                        read_data = hex2str(read_raw_data)
                        
                        if len(read_data)/2 != 39:
                            # Skip the code below and move on to the next one.
                            continue
                        
                        # ---------- Time
                        current_time = dt.now().strftime('%Y.%m.%d %H:%M:%S') # .strftime('%Y.%m.%d %H:%M:%S') 
                        self.address[address]['time'] = current_time 
                        
                        # ---------- Address
                        address = ReadData(read_data, 7, 11)
                        self.address[address]['address'] = Flip(address)
                        
                        # ---------- Flow Rate
                        flow_rate = ReadData(read_data, 27, 31)
                        flow_rate = Flip(flow_rate[6:8])
                        flow_rate = str2hex(flow_rate)
                        if flow_rate == b'\x00':
                            self.address[address]['flow_rate'] = 0.0
                        else:
                            self.address[address]['flow_rate'] = unpack("!f", flow_rate)[0]
                            
                        # ---------- Total Volume
                        total_volume = ReadData(read_data, 21, 25)
                        total_volume = Flip(total_volume)
                        total_volume = str2hex(total_volume)
                        if total_volume == b'\x00':
                            self.address[address]['total_volume'] = 0.0
                        else:
                            self.address[address]['total_volume'] = int(hex2str(total_volume), 16) / 1000
                        
                
                        if save_as_csv is True:
                            save_data = [
                                self.address[address]['time'], 
                                self.address[address]['address'], 
                                self.address[address]['flow_rate'],
                                self.address[address]['total_volume'] 
                            ]
                            
                            file_name = current_time.strftime('%Y_%m_%d') + '.csv'
                            toCSV(path='gathering\\', file_name=file_name, save_data=save_data)
                        
                        if send_to_db is True:
                            # sql = "INSERT INTO `%s` VALUES ('%s', '%s', '%f', '%f')" %(
                            #     'ufm-lxc', 
                            #     self.address[address]['time'], 
                            #     self.address[address]['address'], 
                            #     self.address[address]['flow_rate'], 
                            #     self.address[address]['total_volume'])
                            # self.lxc_db.send(sql)
                            pass


    # def ReturnData(self):
    #     if self.mode == 'debug':
    #         return 'Debug/99999999/9.999999/9.999999'
    #     time         = self.address[address]['time']
    #     address      = self.address[address]['address']
    #     flow_rate    = self.address[address]['flow_rate']
    #     total_volume = self.address[address]['total_volume']
        
    #     try:
    #         send_data = str(time) + '/' + address + '/' + str(flow_rate) + '/' + str(total_volume)
    #     except:
    #         send_data = 'Error/99999999/9.999999/9.999999'
           
    #     return send_data
        
        
        
    # def PrintData(self):
    #     if self.mode == 'master': 
    #         time         = self.address[address]['time'] 
    #         address      = self.address[address]['address']
    #         flow_rate    = self.address[address]['flow_rate']
    #         total_volume = self.address[address]['total_volume']
    #         print(f'[Master] {time}  Address: {address}  Flow Rate: {flow_rate:11.6f}㎥/h  Total Volume: {total_volume:11.6f}㎥')
            
    #         try:
    #             time         = self.address[address]['slave_time'] 
    #             address      = self.address[address]['slave_address']
    #             flow_rate    = self.address[address]['slave_flow_rate']
    #             total_volume = self.address[address]['slave_total_volume']
    #             print(f'[Slave]  {time}  Address: {address}  Flow Rate: {flow_rate:11.6f}㎥/h  Total Volume: {total_volume:11.6f}㎥')
            
    #         except:
    #             print('[Slave] Print Error')
                
        # elif self.mode == 'slave':
        #     time         = self.buf['time'] 
        #     address      = self.buf['address']
        #     flow_rate    = self.buf['flow_rate']
        #     total_volume = self.buf['total_volume']
        #     print(f'[Slave] {time}  Address: {address}  Flow Rate: {flow_rate:11.6f}㎥/h  Total Volume: {total_volume:11.6f}㎥')
            
