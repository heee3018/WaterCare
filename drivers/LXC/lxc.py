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
    def __init__(self, name, port, addresses, mode):
        self.ser          = Serial()
        self.ser.port     = port                     # Default : '/dev/ttyUSB*'
        self.ser.baudrate = serial_info['baudrate']  # Default : 2400
        self.ser.bytesize = serial_info['bytesize']  # Default : 8
        self.ser.stopbits = serial_info['stopbits']  # Default : 1
        self.ser.parity   = serial_info['parity']    # Default : 'E'
        self.ser.timeout  = serial_info['timeout']   # Default : 1
        
        if not self.ser.is_open:
            self.ser.open()
                
        self.buf = {
            'time'               : dt.now(),
            'address'            : None,
            'flow_rate'          : None,
            'total_volume'       : None
        }
        
        
        self.read_cmd    = '107BFD7816'
        self.select_cmd  = 'No address selected yet'
        
        self.mode        = mode     # 'master', 'slave'
        self.address     = self.SelectAddress(addresses)
        print(f"{name} / {self.mode} / {self.address}")
        
        if self.address != '99999999':
            self.StartThreading() 
            
        elif self.address == '99999999':
            self.ser.close() 
            # print("Threading could not start because the address not be found.")
        
    def SelectAddress(self, addresses):
        inverted_addresses = Flip(addresses)  # Flip Input Addresses
        selected_address   = None             # address to be returned
        repeat_count       = 1                # number of repeat      
    
        for _ in range(repeat_count):
            # Select the Fliped addresses one by one
            for inverted_address in inverted_addresses:  
                # Check if the flipped address is in the list of detected addresses
                if inverted_address in detected_addresses:
                    # print("The address is already connected.")
                    break # go to next address
                
                # else if inverted_address not in detected_addresses
                select_command = '680B0B6873FD52' + inverted_address + 'FFFFFFFF' + CRC(inverted_address) + '16'
                self.ser.write(str2hex(select_command))
                    
                response = self.ser.read(1)
                if response == b'\xe5':
                    # print('%s has been added !' %Flip(inverted_address))
                    self.select_cmd  = select_command               # update the command
                    selected_address = Flip(inverted_address)       # Save Fliped address as selected address
                    detected_addresses.append(inverted_address)     # Add to Detected Address

                    break
                
                elif response != b'\xe5': 
                    # print('%s is not found...' %Flip(inverted_address))
                    continue
        
            if selected_address != None:
                # Exit the for, if the selected address is found
                break
            
            elif selected_address == None:
                # If there is no selected address, an error code is returned and for exits.
                selected_address = '99999999'
                break
            
        return selected_address
     
    def StartThreading(self):
        self.running       = True
        self.thread        = Thread(target=self.CommonThread)
        self.thread.daemon = False
        self.thread.start()
            
    def CommonThread(self):
        while self.running:
            self.ser.write(str2hex(self.select_cmd))
            response = self.ser.read(1)
            
            if response != b'\xe5':
                self.buf['time']         = dt.now()
                self.buf['address']      = '99999999'
                self.buf['flow_rate']    = '9.999999'
                self.buf['total_volume'] = '9.999999'
                
            elif response == b'\xe5':
                for _ in range(10):
                    self.ser.write(str2hex(self.read_cmd))
                    read_raw_data = self.ser.read(39)
                    read_data = hex2str(read_raw_data)
                    
                    if len(read_data)/2 != 39:
                        # Skip the code below and move on to the next one.
                        continue

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
                    
                    # self.PrintData()
                    
                    if save_as_csv is True:
                        save_data = [
                            self.buf['time'], 
                            self.buf['address'], 
                            self.buf['flow_rate'],
                            self.buf['total_volume'] 
                        ]
                        
                        file_name = current_time.strftime('%Y_%m_%d') + '.csv'
                        toCSV(path='gathering\\', file_name=file_name, save_data=save_data)
                    
                    if send_to_db is True:
                        pass                    
                        sql = "INSERT INTO `%s` VALUES ('%s', '%s', '%f', '%f')" %(
                            'ufm-lxc', 
                            self.buf['time'], 
                            self.buf['address'], 
                            self.buf['flow_rate'], 
                            self.buf['total_volume'])
                        # self.lxc_db.send(sql)

#
    # def MasterThread(self):
    #     # Recive #
    #     while self.running:
    #         interval = 0.4
    #         received_by_slave = self.communicate.readline()
    #         # print(f"[Recive] {received_by_slave}")
            
    #         if received_by_slave == b'':
    #             # received_by_slave = "b'error/99999999/9.999999/9.999999'"
    #             continue
            
    #         received_buf = str(received_by_slave)[2:-1].split('/')
            
    #         self.buf['slave_time']         = str(received_buf[0])
    #         self.buf['slave_address']      = str(received_buf[1])
    #         self.buf['slave_flow_rate']    = float(received_buf[2])
    #         self.buf['slave_total_volume'] = float(received_buf[3])
    #         # print(f"[Recive] {time}  Address: {address}  Flow Rate: {flow_rate:11.6f}㎥/h  Total Volume: {total_volume:11.6f}㎥")
            
    #         sleep(interval)
            
    # def SlaveThread(self):
    #     # Transmit #  
    #     while self.running:
    #         interval     = 0.4
    #         time         = self.buf['time']
    #         address      = self.buf['address']
    #         flow_rate    = self.buf['flow_rate']
    #         total_volume = self.buf['total_volume']
            
    #         try:
    #             send_data = str(time) + '/' + address + '/' + str(flow_rate) + '/' + str(total_volume)
    #             send_data = send_data.encode(encoding='utf-8')
    #             send_to_master = self.communicate.write(send_data)
    #             print(f"[Transmit] Send: {send_data} [length {send_to_master}]")
                
    #         except:
    #             continue
            
    #         sleep(interval)
#           
    def ReturnData(self):
        time         = self.buf['time']
        address      = self.buf['address']
        flow_rate    = self.buf['flow_rate']
        total_volume = self.buf['total_volume']
        
        try:
            send_data = str(time) + '/' + address + '/' + str(flow_rate) + '/' + str(total_volume)
        except:
            send_data = 'Error/99999999/9.999999/9.999999'
           
        return send_data
        
    def PrintData(self):
        if self.mode == 'master': 
            time         = self.buf['time'] 
            address      = self.buf['address']
            flow_rate    = self.buf['flow_rate']
            total_volume = self.buf['total_volume']
            print(f'[Master] {time}  Address: {address}  Flow Rate: {flow_rate:11.6f}㎥/h  Total Volume: {total_volume:11.6f}㎥')
            
            try:
                time         = self.buf['slave_time'] 
                address      = self.buf['slave_address']
                flow_rate    = self.buf['slave_flow_rate']
                total_volume = self.buf['slave_total_volume']
                print(f'[Slave]  {time}  Address: {address}  Flow Rate: {flow_rate:11.6f}㎥/h  Total Volume: {total_volume:11.6f}㎥')
            except:
                print('[Slave] Print Error')
                
        # elif self.mode == 'slave':
        #     time         = self.buf['time'] 
        #     address      = self.buf['address']
        #     flow_rate    = self.buf['flow_rate']
        #     total_volume = self.buf['total_volume']
        #     print(f'[Slave] {time}  Address: {address}  Flow Rate: {flow_rate:11.6f}㎥/h  Total Volume: {total_volume:11.6f}㎥')
            
