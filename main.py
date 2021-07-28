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
        device.append(lxc.Setup2(tag='USB_0', port='/dev/ttyUSB0'))
        device.append(lxc.Setup2(tag='USB_1', port='/dev/ttyUSB1'))
        device.append(lxc.Setup2(tag='USB_2', port='/dev/ttyUSB2'))
        device.append(lxc.Setup2(tag='USB_3', port='/dev/ttyUSB3'))
        device.append(lxc.Setup2(tag='USB_4', port='/dev/ttyUSB4'))
        device.append(lxc.Setup2(tag='USB_5', port='/dev/ttyUSB5'))
        device.append(lxc.Setup2(tag='USB_6', port='/dev/ttyUSB6'))
        
        
        # LXC Find Serial Number
        threads = [ ]
        for dev in device:
            if dev.name == 'lxc':
                if dev.connect_port():
                    thread = dev.start_search_thread()
                    threads.append(thread)
                
        for thread in threads:
            thread.join()
        
        for dev in device:
            if dev.name == 'lxc':
                if dev.state == 'enabled': 
                    print(f"{'[LOG]':>10} {dev.tag} - Enabled")
                else:
                    print(f"{'[LOG]':>10} {dev.tag} - Desabled")

        count_down(5)
            
        # Start threading
        for dev in device:
            if dev.name == 'lxc':
                if dev.state == 'enabled':
                    dev.start_read_thread()
            if dev.name == 'ms5837':
                dev.start_read_thread()
        
        while True:
            pass

    except KeyboardInterrupt:
        print(f"{'[LOG]':>10} Keyboard Interrupt.")

    print(f"{'[LOG]':>10} The Main loop is over.")