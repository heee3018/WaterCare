import os
from time       import sleep
from threading  import Thread

from drivers    import lxc

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
        
        thread_0 = Thread(target=USB_0.to_read)
        thread_1 = Thread(target=USB_1.to_read)
        thread_2 = Thread(target=USB_2.to_read)
        thread_3 = Thread(target=USB_3.to_read)
        thread_4 = Thread(target=USB_4.to_read)
        thread_5 = Thread(target=USB_5.to_read)
        thread_6 = Thread(target=USB_6.to_read)
        thread_0.start()
        thread_1.start()
        thread_2.start()
        thread_3.start()
        thread_4.start()
        thread_5.start()
        thread_6.start()
        thread_0.join()
        thread_1.join()
        thread_2.join()
        thread_3.join()
        thread_4.join()
        thread_5.join()
        thread_6.join()
        
        USB_0.print_data()
        USB_1.print_data()
        USB_2.print_data()
        USB_3.print_data()
        USB_4.print_data()
        USB_5.print_data()
        USB_6.print_data()   
    
    
    except KeyboardInterrupt:
        print("[LOG] Keyboard Interrupt.")
        break

print("[LOG] The Main loop is over.")