import os
import threading
from time       import sleep
from datetime   import datetime
from serial     import Serial

from drivers import lxc

# os.system('sudo /etc/init.d/udev restart') # USB Restart
# os.system('sudo rdate -s time.bora.net')   # Set to current time

print("[LOG] Initializing")

USB_0 = lxc.Setup(name='USB_0', port='/dev/ttyUSB0')
USB_1 = lxc.Setup(name='USB_1', port='/dev/ttyUSB1')
USB_2 = lxc.Setup(name='USB_2', port='/dev/ttyUSB2')
USB_3 = lxc.Setup(name='USB_3', port='/dev/ttyUSB3')
USB_4 = lxc.Setup(name='USB_4', port='/dev/ttyUSB4')
USB_5 = lxc.Setup(name='USB_5', port='/dev/ttyUSB5')
USB_6 = lxc.Setup(name='USB_6', port='/dev/ttyUSB6')

print("[LOG] Initialization complete.")

print("[LOG] Main loop Start.")
while True:
    try:
        sleep(1)
        print('main loop')
    
    except KeyboardInterrupt:
        print("[LOG] Keyboard Interrupt.")
        break

print("[LOG] The Main loop is over.")serial.serialutil.SerialException