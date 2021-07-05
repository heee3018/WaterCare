# -*- coding: utf-8 -*-
from time    import sleep
from serial  import Serial
from drivers import LXC
from config  import Address, Mode

communicate         = Serial()
communicate.port    = '/dev/ttyAMA0'
communicate.timeout = 1
interval            = 0.4

if not communicate.is_open:
    communicate.open()

data_buffer = [None] * 14

usb_0 = LXC.Setup(port='/dev/ttyUSB0', addresses=Address, mode=Mode)
usb_1 = LXC.Setup(port='/dev/ttyUSB1', addresses=Address, mode=Mode)
usb_2 = LXC.Setup(port='/dev/ttyUSB2', addresses=Address, mode=Mode)
usb_3 = LXC.Setup(port='/dev/ttyUSB3', addresses=Address, mode=Mode)
usb_4 = LXC.Setup(port='/dev/ttyUSB4', addresses=Address, mode=Mode)
usb_5 = LXC.Setup(port='/dev/ttyUSB5', addresses=Address, mode=Mode)
usb_6 = LXC.Setup(port='/dev/ttyUSB6', addresses=Address, mode=Mode)

for i in range(5):
    sleep(1)
    print(i + 1)
    
while True:
    if Mode == 'master':
        received_by_slave = communicate.readline()
        if received_by_slave == b'':
            continue
        
        received_buf = str(received_by_slave)[2:-1].split('#')
        
        master_data_0 = usb_0.ReturnData()
        master_data_1 = usb_1.ReturnData()
        master_data_2 = usb_2.ReturnData()
        master_data_3 = usb_3.ReturnData()
        master_data_4 = usb_4.ReturnData()
        master_data_5 = usb_5.ReturnData()
        master_data_6 = usb_6.ReturnData()
        master_buf    = list()
        master_buf.append(master_data_0)
        master_buf.append(master_data_1)
        master_buf.append(master_data_2)
        master_buf.append(master_data_3)
        master_buf.append(master_data_4)
        master_buf.append(master_data_5)
        master_buf.append(master_data_6)
        
        slave_data_0  = received_buf[0].split('/')
        slave_data_1  = received_buf[1].split('/')
        slave_data_2  = received_buf[2].split('/')
        slave_data_3  = received_buf[3].split('/')
        slave_data_4  = received_buf[4].split('/')
        slave_data_5  = received_buf[5].split('/')
        slave_data_6  = received_buf[6].split('/')
        
        for data in master_buf:
            print(f"[Master] {data}")
        for data in received_buf:
            print(f"[Slave]  {data}")
        
    elif Mode == 'slave':
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
        send_data.encode(encoding='utf-8')
        
        send_to_master = communicate.write(send_data)
        
        print(f"\n [Length] {send_to_master}")
        for data in  send_data.split('#'):
            print(f"[Transmit] {data}")
            
    sleep(interval)