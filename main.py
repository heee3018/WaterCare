# -*- coding: utf-8 -*-
import os
from time    import sleep
from serial  import Serial
from config  import Address, Mode
from drivers import LXC, MS5837

## USB Restart
# os.system('sudo /etc/init.d/udev restart')

print(f"\n===== Mode: {Mode} =====")
## Sensor Setup
i2c_0 = MS5837.Setup()
usb_0 = LXC.Setup(name='usb_0', port='/dev/ttyUSB0', addresses=Address, mode=Mode) # 3
usb_1 = LXC.Setup(name='usb_1', port='/dev/ttyUSB1', addresses=Address, mode=Mode) # 3
usb_2 = LXC.Setup(name='usb_2', port='/dev/ttyUSB2', addresses=Address, mode=Mode) # 2
usb_3 = LXC.Setup(name='usb_3', port='/dev/ttyUSB3', addresses=Address, mode=Mode)
usb_4 = LXC.Setup(name='usb_4', port='/dev/ttyUSB4', addresses=Address, mode=Mode)
usb_5 = LXC.Setup(name='usb_5', port='/dev/ttyUSB5', addresses=Address, mode=Mode)
usb_6 = LXC.Setup(name='usb_6', port='/dev/ttyUSB6', addresses=Address, mode=Mode)
    
## Master-Slave Communication
communicate = Serial(port='/dev/ttyAMA0', timeout=1, xonxoff=True)
interval    = 0.4

print(f"\n===== Main loop =====")
while True:
    sleep(interval)
    if Mode == 'master':
        if usb_0.address != None:
            for address in list(self.address.keys()):
                print(f"\n usb_0")
                print(f"  {usb_0.address[address]['time']}")
                print(f"  {usb_0.address[address]['address']}")
                print(f"  {usb_0.address[address]['flow_rate']}")
                print(f"  {usb_0.address[address]['total_volume']}")
            
        if usb_1.address != None:
            for address in list(self.address.keys()):
                print(f"\n usb_1")
                print(f"  {usb_1.address[address]['time']}")
                print(f"  {usb_1.address[address]['address']}")
                print(f"  {usb_1.address[address]['flow_rate']}")
                print(f"  {usb_1.address[address]['total_volume']}")
            
        if usb_2.address != None:
            for address in list(self.address.keys()):
                print(f"\n usb_2")
                print(f"  {usb_2.address[address]['time']}")
                print(f"  {usb_2.address[address]['address']}")
                print(f"  {usb_2.address[address]['flow_rate']}")
                print(f"  {usb_2.address[address]['total_volume']}")
            
        if usb_3.address != None:
            for address in list(self.address.keys()):
                print(f"\n usb_3")
                print(f"  {usb_3.address[address]['time']}")
                print(f"  {usb_3.address[address]['address']}")
                print(f"  {usb_3.address[address]['flow_rate']}")
                print(f"  {usb_3.address[address]['total_volume']}")
            
        if usb_4.address != None:
            for address in list(self.address.keys()):
                print(f"\n usb_4")
                print(f"  {usb_4.address[address]['time']}")
                print(f"  {usb_4.address[address]['address']}")
                print(f"  {usb_4.address[address]['flow_rate']}")
                print(f"  {usb_4.address[address]['total_volume']}")
            
        if usb_5.address != None:
            for address in list(self.address.keys()):
                print(f"\n usb_5")
                print(f"  {usb_5.address[address]['time']}")
                print(f"  {usb_5.address[address]['address']}")
                print(f"  {usb_5.address[address]['flow_rate']}")
                print(f"  {usb_5.address[address]['total_volume']}")
            
        if usb_6.address != None:
            for address in list(self.address.keys()):
                print(f"\n usb_6")
                print(f"  {usb_6.address[address]['time']}")
                print(f"  {usb_6.address[address]['address']}")
                print(f"  {usb_6.address[address]['flow_rate']}")
                print(f"  {usb_6.address[address]['total_volume']}")
             
        if i2c_0.read():
            print("P: %0.1f hPa  %0.3f bar\tT: %0.2f C  %0.2f F" % (
                i2c_0.pressure(), # Default is mbar (no arguments)
                i2c_0.pressure(MS5837.unit_bar), # Request psi
                i2c_0.temperature(), # Default is degrees C (no arguments)
                i2c_0.temperature(MS5837.unit_Farenheit))) # Request Farenheit
        else:
            print("Sensor read failed!")
            exit(1)
    # if Mode == 'master':
    #     print('\n')
    #     master_buf = []
    #     master_buf.append(usb_0.ReturnData())
    #     master_buf.append(usb_1.ReturnData())
    #     master_buf.append(usb_2.ReturnData())
    #     master_buf.append(usb_3.ReturnData())
    #     master_buf.append(usb_4.ReturnData())
    #     master_buf.append(usb_5.ReturnData())
    #     master_buf.append(usb_6.ReturnData())
        
    #     for i, data in enumerate(master_buf):
    #         if data[:5] == 'Error':
    #             continue
            
    #         print(f"[Master_{i}] {data}")
            
    #     received_by_slave = communicate.readline(377)
        
    #     if received_by_slave == b'':
    #         continue
        
    #     received_by_slave = str(received_by_slave)[2:-1].split('#')
        
    #     while '' in received_by_slave:
    #         received_by_slave.remove('')
            
    #     for i, data in enumerate(received_by_slave):
    #         if data[:5] == 'Error':
    #             continue
            
    #         print(f"[Slave_{i}]  {data}")

    #     sleep(interval)
        
    # elif Mode == 'slave':
               
    #     print('\n')
    #     slave_data_0 = usb_0.ReturnData()
    #     slave_data_1 = usb_1.ReturnData()
    #     slave_data_2 = usb_2.ReturnData()
    #     slave_data_3 = usb_3.ReturnData()
    #     slave_data_4 = usb_4.ReturnData()
    #     slave_data_5 = usb_5.ReturnData()
    #     slave_data_6 = usb_6.ReturnData()
        
    #     send_data  = slave_data_0 + '#'
    #     send_data += slave_data_1 + '#'
    #     send_data += slave_data_2 + '#'
    #     send_data += slave_data_3 + '#'
    #     send_data += slave_data_4 + '#'
    #     send_data += slave_data_5 + '#'
    #     send_data += slave_data_6
        
    #     while len(send_data) < 377:
    #         send_data += '#'
        
    #     communicate.write(send_data.encode('utf-8'))
        
    #     send_data_list = send_data.split('#')
        
    #     while '' in send_data_list:
    #         send_data_list.remove('')
            
    #     for i, data in enumerate(send_data_list):            
    #         if data[:5] == 'Error':
    #             continue
            
    #         print(f"[Slave_{i}] {len(data)} {data}")
        
        
    #     sleep(interval)
    
    # elif Mode == 'debug':
               
        # sleep(interval)
        
        # if i2c_0.read():
        #     print("P: %0.1f hPa  %0.3f bar\tT: %0.2f C  %0.2f F" % (
        #     i2c_0.pressure(), # Default is mbar (no arguments)
        #     i2c_0.pressure(ms5837.UNITS_bar), # Request psi
        #     i2c_0.temperature(), # Default is degrees C (no arguments)
        #     i2c_0.temperature(ms5837.UNITS_Farenheit))) # Request Farenheit
        # else:
        #     print("Sensor read failed!")
        #     exit(1)
    
    ## Common
