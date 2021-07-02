# -*- coding: utf-8 -*-
from time    import sleep
from serial  import Serial
from drivers import LXC
from config  import Address, Mode

data_buffer = [None] * 14

usb_0 = LXC.Setup(port='/dev/ttyUSB0', address=Address, mode=Mode)
usb_1 = LXC.Setup(port='/dev/ttyUSB1', address=Address, mode=Mode)
usb_2 = LXC.Setup(port='/dev/ttyUSB2', address=Address, mode=Mode)
usb_3 = LXC.Setup(port='/dev/ttyUSB3', address=Address, mode=Mode)
usb_4 = LXC.Setup(port='/dev/ttyUSB4', address=Address, mode=Mode)
usb_5 = LXC.Setup(port='/dev/ttyUSB5', address=Address, mode=Mode)
usb_6 = LXC.Setup(port='/dev/ttyUSB6', address=Address, mode=Mode)

sleep(5)

while True:
    sleep(1)
    if Mode == 'master':
        print(f"00  {usb_0.read}")
        print(f"01  {usb_1.read}")
        print(f"02  {usb_2.read}")
        print(f"03  {usb_3.read}")
        print(f"04  {usb_4.read}")
        print(f"05  {usb_5.read}")
        print(f"06  {usb_6.read}")
    elif Mode == 'slave':
        pass