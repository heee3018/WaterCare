from smbus2 import SMBus
from time import sleep
from datetime import datetime as dt
from ctypes import *
  
address = 0x28
P1 = 1638.3   # 10% * 16383 -A Type # 2^14
P2 = 13106.4  # 80% * 16383 -A Type # 2^14
Pmax = 15.0
Pmin = 0.0
bus = SMBus(1)

def unsigned(n):
  return c_uint(n).value

def toHex(read):
    res = [None] * len(read)
    
    for i in range(len(read)):
        res[i] = hex(read[i])
    return res    

while True:
    read = bus.read_i2c_block_data(address, 0, 4)
    
    sleep(1)
    print('\n')
    print(' S ' + str(bin(address | 0x100))[4:] + 'R' + ' A ' + str(bin(read[0] | 0x100))[3:] + ' A ' + str(bin(read[1] | 0x100))[3:] + ' A ' 
        + str(bin(read[2] | 0x100))[3:] + ' A ' + str(bin(read[3] | 0x100))[3:] + ' N P ' )
    
    if (read[0] & 0xc0) == 0x00:
        d_pressure    = (unsigned((read[0] & 0x3f) << 8) + read[1])
        d_temperature = (unsigned((read[2]) << 3) + read[3])
        pressure      = (d_pressure - P1) * (Pmax - Pmin) / P2 + Pmin
        temperature   = (d_temperature * 200) / 2047 - 50
        
        print(str(dt.now()))
        print(f"pres: %.5f ({toHex(read[:2])})" %pressure)
        print(f"temp: %.5f ({toHex(read[2:])})" %temperature)
     