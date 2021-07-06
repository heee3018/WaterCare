# -*- coding: utf-8 -*-
from time    import sleep
from serial  import Serial
from drivers import LXC
from config  import Address, Mode

communicate = Serial(port='/dev/ttyAMA0', timeout=3, xonxoff=True)
interval    = 0.4

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
        
        sleep(interval)
        
        master_buf    = []
        master_buf.append(usb_0.ReturnData())
        master_buf.append(usb_1.ReturnData())
        master_buf.append(usb_2.ReturnData())
        master_buf.append(usb_3.ReturnData())
        master_buf.append(usb_4.ReturnData())
        master_buf.append(usb_5.ReturnData())
        master_buf.append(usb_6.ReturnData())
        
        for i, data in enumerate(master_buf):
            print(f"[Master_{i}] {data}")
            
            
            
        received_by_slave = communicate.readline(377)
        received_by_slave = received_by_slave.[2:-1].split('#')
        
        while '' in received_by_slave:
            received_by_slave.remove('')
            
        for i, data in enumerate(received_by_slave):
            print(f"[Slave_{i}] {data}")
        
        print('\n')
        # if received_by_slave == b'':
        #     continue
        
        # received_buf = str(received_by_slave)[2:-1].split('#')
        # print(received_buf)
        
        # slave_data_0  = received_buf[0].split('/')
        # slave_data_1  = received_buf[1].split('/')
        # slave_data_2  = received_buf[2].split('/')
        # slave_data_3  = received_buf[3].split('/')
        # slave_data_4  = received_buf[4].split('/')
        # slave_data_5  = received_buf[5].split('/')
        # slave_data_6  = received_buf[6].split('/')
        
        # for i, data in enumerate(received_buf):
        #     print(f"[Slave_{i}]  {data}")
            
            
    elif Mode == 'slave':
        
        sleep(interval)
        
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
            print(f"[Slave_{i}] {len(data)} {data}")
        
        print('\n')
        
        # send_data.encode(encoding='utf-8')
        # print(send_data)
        
        # send_to_master = communicate.write(send_data)
        
        # print(f"\n [Length] {send_to_master}")
        
        # for i, data in enumerate(send_data.split('#')):
        #     print(f"[Transmit_{i}] {data}")
            