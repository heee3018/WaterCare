import os
import pandas as pd
from time      import sleep
from datetime  import datetime
from binascii  import hexlify   as hex2str
from binascii  import unhexlify as str2hex
from struct    import unpack

READ_COMMAND = str2hex('107BFD7816')

def count_down(num=5):
    for count_down in reversed(range(num)):
        print(f"[LOG] {count_down + 1}")
        sleep(1)
        
def current_time():
    return datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]  # format : 2020-05-04 10:18:32.926

def current_date():
    return datetime.now().strftime('%Y_%m_%d')  # format : 2020_05_04
    
def save_as_csv(device, save_data, file_name):    
    if device == 'ms5837':
        data = pd.DataFrame([save_data], columns=['time', 'pressure', 'temperature'])
        
    elif device == 'lxc':
        data = pd.DataFrame([save_data], columns=['time', 'serial_num', 'flow_rate', 'total_volume'])
    
    if file_name[-4:] != '.csv':
        file_name += '.csv'
    
    if not os.path.exists(file_name):
        try:
            data.to_csv(file_name, index=False, mode='w', encoding='utf-8-sig')
        except FileNotFoundError as e:
            print(f"[ERROR] File Not Found Error {str(e)[56:]")
            os.system('sudo mkdir /home/pi/WaterCare/csv')
            pass
    else:
        data.to_csv(file_name, index=False, mode='a', encoding='utf-8-sig', header=False)

def flip(address):
    if type(address) == list:
        result = list()
        
        for addr in address:
            addr = addr[6:8] + addr[4:6] + addr[2:4] + addr[0:2]
            result.append(addr)
            
        return result
    
    else:
        return address[6:8] + address[4:6] + address[2:4] + address[0:2]

def crc(address):
    return ('%x' %sum(str2hex('73FD52' + address + 'FFFFFFFF')))[-2:]

def to_select_command(reversed_num):
    if type(reversed_num) == list:
        result = list()
        for address in reversed_num:
            result.append(str2hex('680B0B6873FD52' + address + 'FFFFFFFF' + crc(address) + '16'))
            
        return result
    
    else:
        return str2hex('680B0B6873FD52' + reversed_num + 'FFFFFFFF' + crc(reversed_num) + '16')

def read_format(hex_data, from_start, to_end):
    read_data = hex_data[from_start:to_end]
    read_data = hex2str(read_data)
    read_data = str(read_data)[2:-1]
    return read_data

def get_return_serial_num(str_data):
    retrun_serial_num = flip(str_data)
    return retrun_serial_num

def get_flow_rate(str_data):
    flow_rate = flip(str_data)
    flow_rate = str2hex(flow_rate)
    flow_rate = unpack('!f', flow_rate)[0]
    
    return flow_rate

def get_total_volume(str_data):
    total_volume = flip(str_data)
    total_volume = int(total_volume, 16) / 1000
    return total_volume