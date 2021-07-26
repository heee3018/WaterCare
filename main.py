import os
from time    import sleep
from drivers import database, ms5837, lxc 
from config  import HOST, USER, PASSWORD, DB, TABLE 

os.system('sudo /etc/init.d/udev restart') # USB Restart
os.system('sudo rdate -s time.bora.net')   # Set to current time

if __name__ == '__main__':
        
    db    = database.Setup(HOST, USER, PASSWORD, DB)
    I2C_0 = ms5837.Setup()
    USB_0 = lxc.Setup(name='USB_0', port='/dev/ttyUSB0')
    USB_1 = lxc.Setup(name='USB_1', port='/dev/ttyUSB1')
    USB_2 = lxc.Setup(name='USB_2', port='/dev/ttyUSB2')
    USB_3 = lxc.Setup(name='USB_3', port='/dev/ttyUSB3')
    USB_4 = lxc.Setup(name='USB_4', port='/dev/ttyUSB4')
    USB_5 = lxc.Setup(name='USB_5', port='/dev/ttyUSB5')
    USB_6 = lxc.Setup(name='USB_6', port='/dev/ttyUSB6')
    print("[LOG] Initialization complete.")
    USB_0.start_thread()
    USB_1.start_thread()
    USB_2.start_thread()
    USB_3.start_thread()
    USB_4.start_thread()
    USB_5.start_thread()
    USB_6.start_thread()
    print("[LOG] Start threading.")
    print("[LOG] Main loop Start.")
    while True:
        try:
            I2C_0.print_data()
            USB_0.print_data()
            USB_1.print_data()
            USB_2.print_data()
            USB_3.print_data()
            USB_4.print_data()
            USB_5.print_data()
            USB_6.print_data()
        
            sleep(1)

        except KeyboardInterrupt:
            print("[LOG] Keyboard Interrupt.")
            break
    print("[LOG] The Main loop is over.")