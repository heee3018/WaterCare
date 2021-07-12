# -*- coding: utf-8 -*-
import os
from time    import sleep
from serial  import Serial
from drivers import LXC
from drivers import MS5837
from config  import Address, Mode

os.system('sudo /etc/init.d/udev restart')

communicate = Serial(port='/dev/ttyAMA0', timeout=1, xonxoff=True)
interval    = 0.4

i2c_0 = ms5837.MS5837_30BA() 
usb_0 = LXC.Setup(name='usb_0', port='/dev/ttyUSB0', addresses=Address, mode=Mode)
usb_1 = LXC.Setup(name='usb_1', port='/dev/ttyUSB1', addresses=Address, mode=Mode)
usb_2 = LXC.Setup(name='usb_2', port='/dev/ttyUSB2', addresses=Address, mode=Mode)
usb_3 = LXC.Setup(name='usb_3', port='/dev/ttyUSB3', addresses=Address, mode=Mode)
usb_4 = LXC.Setup(name='usb_4', port='/dev/ttyUSB4', addresses=Address, mode=Mode)
usb_5 = LXC.Setup(name='usb_5', port='/dev/ttyUSB5', addresses=Address, mode=Mode)
usb_6 = LXC.Setup(name='usb_6', port='/dev/ttyUSB6', addresses=Address, mode=Mode)
    
while True:
    
    while not communicate.is_open:
        try:
            communicate.open()
        except:
            communicate.close()
            print(f"communicate.open() Error")
            pass
    
    print(communicate)
        
    if Mode == 'master':
        
        print('\n')
        master_buf    = []
        master_buf.append(usb_0.ReturnData())
        master_buf.append(usb_1.ReturnData())
        master_buf.append(usb_2.ReturnData())
        master_buf.append(usb_3.ReturnData())
        master_buf.append(usb_4.ReturnData())
        master_buf.append(usb_5.ReturnData())
        master_buf.append(usb_6.ReturnData())
        
        for i, data in enumerate(master_buf):
            if data[:5] == 'Error':
                continue
            
            print(f"[Master_{i}] {data}")
            
        
        received_by_slave = communicate.readline(377)
        
        if received_by_slave == b'':
            continue
        
        received_by_slave = str(received_by_slave)[2:-1].split('#')
        
        while '' in received_by_slave:
            received_by_slave.remove('')
            
        for i, data in enumerate(received_by_slave):
            if data[:5] == 'Error':
                continue
            
            print(f"[Slave_{i}]  {data}")

        sleep(interval)
        
        print("Pressure: %.2f atm  %.2f Torr  %.2f psi"% (
            i2c_0.pressure(MS5837.UNITS_atm),
            i2c_0.pressure(MS5837.UNITS_Torr),
            i2c_0.pressure(MS5837.UNITS_psi)))

        print("Temperature: %.2f C  %.2f F  %.2f K" % (
            i2c_0.temperature(MS5837.UNITS_Centigrade),
            i2c_0.temperature(MS5837.UNITS_Farenheit),
            i2c_0.temperature(MS5837.UNITS_Kelvin)))

            
    elif Mode == 'slave':
               
        print('\n')
        slave_data_0 = usb_0.ReturnData()
        slave_data_1 = usb_1.ReturnData()
        slave_data_2 = usb_2.ReturnData()
        slave_data_3 = usb_3.ReturnData()
        slave_data_4 = usb_4.ReturnData()
        slave_data_5 = usb_5.ReturnData()
        slave_data_6 = usb_6.ReturnData()
        
        send_data  = slave_data_0 + '#'
        send_data += slave_data_1 + '#'
        send_data += slave_data_2 + '#'
        send_data += slave_data_3 + '#'
        send_data += slave_data_4 + '#'
        send_data += slave_data_5 + '#'
        send_data += slave_data_6
        
        while len(send_data) < 377:
            send_data += '#'
        
        communicate.write(send_data.encode('utf-8'))
        
        send_data_list = send_data.split('#')
        
        while '' in send_data_list:
            send_data_list.remove('')
            
        for i, data in enumerate(send_data_list):            
            if data[:5] == 'Error':
                continue
            
            print(f"[Slave_{i}] {len(data)} {data}")
        
        
        sleep(interval)