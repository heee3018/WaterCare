import os
from threading       import Thread
from drivers         import m30j2, ms5837, lxc 
from drivers.library import count_down

os.system('sudo /etc/init.d/udev restart')      # USB Restart
os.system('sudo ntpdate -u 3.kr.pool.ntp.org')  # Set to current time

if __name__ == '__main__':
    try:
        device = list()
        device.append(ms5837.Setup(tag='I2C_0', interval=0.5))
        device.append(m30j2.Setup(tag='I2C_1', interval=0.5))
        device.append(lxc.Setup(tag='USB_0', port='/dev/ttyUSB0'))
        device.append(lxc.Setup(tag='USB_1', port='/dev/ttyUSB1'))
        device.append(lxc.Setup(tag='USB_2', port='/dev/ttyUSB2'))
        device.append(lxc.Setup(tag='USB_3', port='/dev/ttyUSB3'))
        device.append(lxc.Setup(tag='USB_4', port='/dev/ttyUSB4'))
        device.append(lxc.Setup(tag='USB_5', port='/dev/ttyUSB5'))
        device.append(lxc.Setup(tag='USB_6', port='/dev/ttyUSB6'))

        # Connect Database (lxc and ms5837)
        for dev in device:
            dev.connect_db()

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
                print(f"{'[LOG]':>10} {dev.tag} - {dev.state}")

        count_down(5)
            
        # Start threading
        for dev in device:
            if dev.state == 'enabled': 
                    dev.start_read_thread()
        
        while True:
            pass

    except KeyboardInterrupt:
        print(f"{'[LOG]':>10} Keyboard Interrupt.")

    print(f"{'[LOG]':>10} The Main loop is over.")