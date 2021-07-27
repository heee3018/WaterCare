import os
from time      import sleep
from threading import Thread
from drivers   import database, ms5837, lxc 
from config    import HOST, USER, PASSWORD, DB, TABLE 

os.system('sudo /etc/init.d/udev restart') # USB Restart
os.system('sudo /usr/bin/rdate -s time.bora.net')   # Set to current time

if __name__ == '__main__':
    try:
        device = list()
        device.append(ms5837.Setup())
        device.append(lxc.Setup(num='USB_0', port='/dev/ttyUSB0'))
        device.append(lxc.Setup(num='USB_1', port='/dev/ttyUSB1'))
        device.append(lxc.Setup(num='USB_2', port='/dev/ttyUSB2'))
        device.append(lxc.Setup(num='USB_3', port='/dev/ttyUSB3'))
        device.append(lxc.Setup(num='USB_4', port='/dev/ttyUSB4'))
        device.append(lxc.Setup(num='USB_5', port='/dev/ttyUSB5'))
        device.append(lxc.Setup(num='USB_6', port='/dev/ttyUSB6'))
        
        # LXC Find Serial Number
        threads = [ ]
        for dev in device:
            if dev.name == 'lxc':
                thread = Thread(target=dev.find_serial_number, daemon=True)
                thread.start()
                threads.append(thread)
                
        for thread in threads:
            thread.join()
            
        # Start threading
        for dev in device:
            dev.start_thread()

    except KeyboardInterrupt:
        print("[LOG] Keyboard Interrupt.")
        break
    
    print("[LOG] The Main loop is over.")