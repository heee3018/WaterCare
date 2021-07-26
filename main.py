import os
from time    import sleep
from drivers import database, ms5837, lxc 
from config  import HOST, USER, PASSWORD, DB, TABLE 

os.system('sudo /etc/init.d/udev restart') # USB Restart
os.system('sudo rdate -s time.bora.net')   # Set to current time

if __name__ == '__main__':
    lxc_list = list()
    
    db    = database.Setup(HOST, USER, PASSWORD, DB)
    I2C_0 = ms5837.Setup()
    
    lxc_list.append(lxc.Setup(name='USB_0', port='/dev/ttyUSB0'))
    lxc_list.append(lxc.Setup(name='USB_1', port='/dev/ttyUSB1'))
    lxc_list.append(lxc.Setup(name='USB_2', port='/dev/ttyUSB2'))
    lxc_list.append(lxc.Setup(name='USB_3', port='/dev/ttyUSB3'))
    lxc_list.append(lxc.Setup(name='USB_4', port='/dev/ttyUSB4'))
    lxc_list.append(lxc.Setup(name='USB_5', port='/dev/ttyUSB5'))
    lxc_list.append(lxc.Setup(name='USB_6', port='/dev/ttyUSB6'))
    print("[LOG] Initialization complete.")
    
    for lxc in lxc_list:
        lxc.start_thread()
        
    print("[LOG] Start threading.")
    print("[LOG] Main loop Start.")
    
    while True:
        try:
            ms5837_data = I2C_0.print_data()
            time        = ms5837_data["time"]
            pressure    = ms5837_data["pressure"]
            temperature = ms5837_data["temperature"]
            db.send(f"INSERT INTO {TABLE} (time, pressure, temperature) VALUES ('{time}', '{pressure}', '{temperature}')")
            
            for lxc in lxc_list:
                lxc_data     = lxc.print_data()
                if not lxc_data:
                    continue
                time         = lxc_data["time"]
                address      = lxc_data["address"]
                flow_rate    = lxc_data["flow_rate"]
                total_volume = lxc_data["total_volume"]
                db.send(f"INSERT INTO {TABLE} (time, address, flow_rate, total_volume) VALUES ('{time}', '{address}', '{flow_rate}', '{total_volume}')")
            
            sleep(1)

        except KeyboardInterrupt:
            print("[LOG] Keyboard Interrupt.")
            break
    print("[LOG] The Main loop is over.")