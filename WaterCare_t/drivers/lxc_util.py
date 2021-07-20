import os
import pandas as pd
from datetime  import datetime
from binascii  import hexlify   as hex2str
from binascii  import unhexlify as str2hex

read_command = '107BFD7816'

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
    return datetime.now().strftime('%Y.%m.%d %H:%M:%S')


def to_csv(path, file_name, save_data):    
    df = pd.DataFrame([save_data], columns=['datetime', 'address', 'flow_rate', 'total_volume'])
    
    if not os.path.exists(path + file_name):
        df.to_csv(path + file_name, index=False, mode='w', encoding='utf-8-sig')
        
    else:
        df.to_csv(path + file_name, index=False, mode='a', encoding='utf-8-sig', header=False)


def read_data(read_data, from_start, to_end):
    return str(hex2str(str2hex(read_data)[from_start:to_end]))[2:-1]