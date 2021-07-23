import os
import pandas as pd
from datetime  import datetime
from binascii  import hexlify   as hex2str
from binascii  import unhexlify as str2hex
from struct    import unpack

read_command = str2hex('107BFD7816')

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

def to_select_command(inverted_address):
    if type(inverted_address) == list:
        result = list()
        for address in inverted_address:
            result.append(str2hex('680B0B6873FD52' + address + 'FFFFFFFF' + crc(address) + '16'))
            
        return result
    
    else:
        return str2hex('680B0B6873FD52' + inverted_address + 'FFFFFFFF' + crc(inverted_address) + '16')

def current_time():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def to_csv(path, file_name, save_data):    
    df = pd.DataFrame([save_data], columns=['datetime', 'address', 'flow_rate', 'total_volume'])
    
    if not os.path.exists(path + file_name):
        df.to_csv(path + file_name, index=False, mode='w', encoding='utf-8-sig')
        
    else:
        df.to_csv(path + file_name, index=False, mode='a', encoding='utf-8-sig', header=False)


def read_format(hex_data, from_start, to_end):
    read_data = hex_data[from_start:to_end]
    read_data = hex2str(read_data)
    read_data = str(read_data)[2:-1]
    return read_data

def get_return_address(str_data):
    return_address = flip(str_data)
    return return_address

def get_flow_rate(str_data):
    flow_rate = flip(str_data)
    flow_rate = str2hex(flow_rate)
    flow_rate = unpack('!f', flow_rate)[0]
    
    return flow_rate

def get_total_volume(str_data):
    total_volume = flip(str_data)
    total_volume = int(total_volume, 16) / 1000
    return total_volume