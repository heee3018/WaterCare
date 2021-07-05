# -*- coding: utf-8 -*-
from time    import sleep
from serial  import Serial
from drivers import LXC
from config  import Address, Mode

data_buffer = [None] * 14

usb_0 = LXC.Setup(port='/dev/ttyUSB0', addresses=Address, mode=Mode)
usb_1 = LXC.Setup(port='/dev/ttyUSB1', addresses=Address, mode=Mode)
usb_2 = LXC.Setup(port='/dev/ttyUSB2', addresses=Address, mode=Mode)
usb_3 = LXC.Setup(port='/dev/ttyUSB3', addresses=Address, mode=Mode)
usb_4 = LXC.Setup(port='/dev/ttyUSB4', addresses=Address, mode=Mode)
usb_5 = LXC.Setup(port='/dev/ttyUSB5', addresses=Address, mode=Mode)
usb_6 = LXC.Setup(port='/dev/ttyUSB6', addresses=Address, mode=Mode)

sleep(5)

while True:
    sleep(1)
    if Mode == 'master':
        pass
    
    elif Mode == 'slave':
        pass