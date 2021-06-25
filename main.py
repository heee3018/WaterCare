# -*- coding: utf-8 -*-
from time    import sleep
from serial  import Serial
from drivers import LXC
from config  import Address, Mode

lxc_01 = LXC.Setup(port='/dev/ttyUSB0', address=Address, mode=Mode)
lxc_02 = LXC.Setup(port='/dev/ttyUSB1', address=Address, mode=Mode)
lxc_03 = LXC.Setup(port='/dev/ttyUSB2', address=Address, mode=Mode)
lxc_04 = LXC.Setup(port='/dev/ttyUSB3', address=Address, mode=Mode)
lxc_05 = LXC.Setup(port='/dev/ttyUSB4', address=Address, mode=Mode)
lxc_06 = LXC.Setup(port='/dev/ttyUSB5', address=Address, mode=Mode)
lxc_07 = LXC.Setup(port='/dev/ttyUSB6', address=Address, mode=Mode)

while True:
    sleep(1)
    if Mode == 'master':
        print(f"01  {lxc_01.read}")
        print(f"02  {lxc_02.read}")
        print(f"03  {lxc_03.read}")
        print(f"04  {lxc_04.read}")
        print(f"05  {lxc_05.read}")
        print(f"06  {lxc_06.read}")
        print(f"07  {lxc_07.read}")
        
        print(f"08  {lxc_01.read_2}")
        print(f"09  {lxc_02.read_2}")
        print(f"10  {lxc_03.read_2}")
        print(f"11  {lxc_04.read_2}")
        print(f"12  {lxc_05.read_2}")
        print(f"13  {lxc_06.read_2}")
        print(f"14  {lxc_07.read_2}")