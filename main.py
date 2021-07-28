import os
from threading       import Thread
from drivers         import ms5837, lxc 
from drivers.library import count_down

os.system('sudo /etc/init.d/udev restart') # USB Restart
os.system('sudo ntpdate -u 3.kr.pool.ntp.org')   # Set to current time

if __name__ == '__main__':
    try:
        device = list()
        device.append(ms5837.Setup(interval=0.5))
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
                thread = dev.start_search_thread()
                threads.append(thread)
                
        for thread in threads:
            thread.join()
        
        for dev in device:
            if dev.name == 'lxc':
                if dev.state == 'running': 
                    print(f"{'[LOG]':>8} {dev.num} - Enabled")
                else:
                    print(f"{'[LOG]':>8} {dev.num} - Desabled")

        count_down(5)
            
        # Start threading
        for dev in device:
            dev.start_read_thread()
        
        while True:
            pass

    except KeyboardInterrupt:
        print(f"{'[LOG]':>8} Keyboard Interrupt.")

    print(f"{'[LOG]':>8} The Main loop is over.")