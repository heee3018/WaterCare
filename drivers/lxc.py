from threading import Thread
from serial    import Serial, serialutil
from config    import USE_DB, USE_CSV, CHOOSE_ONE_USB
from config    import FIND_COUNT, SERIAL_NUMBER_LIST
from config    import HOST, USER, PASSWORD, DB, TABLE 
from drivers   import database
from drivers.library import current_time, current_date, save_as_csv
from drivers.library import READ_COMMAND, flip, read_format, to_select_command
from drivers.library import get_flow_rate, get_total_volume, get_return_serial_num


class Setup:
    def __init__(self, num, port):
        self.name             = 'lxc'
        self.state            = 'init'
        self.data             =  { }
        self.num              =  num
        self.serial_port      =  port
        self.db               =  database.Setup(HOST, USER, PASSWORD, DB, TABLE)
        self.error_cumulative = 0
        self.connect_serial()
        
    def connect_serial(self):
        connect_serial_count = 5
        while connect_serial_count > 0:
            connect_serial_count -= 1
        
            try:
                self.ser = Serial(port=self.serial_port, baudrate=2400, parity='E', timeout=1)
                if not self.ser.is_open:       
                    self.ser.open()
                
                self.state = 'connected'
                print(f"[LOG] {self.num} - Successfully opened the port")
                break
            
            except serialutil.SerialException as e:
                if str(e)[:9] == '[Errno 2]':
                    print(f"[ERROR] {self.num} - Could not open port {self.num}")
                    
                elif str(e)[:10] == '[Errno 72]':
                    print(f"[ERROR] {self.num} - {str(e)[10:]}")
                    
                self.state = 'disabled' 
                continue
            
            except OSError:
                print(f"[ERROR] {self.num} - Protocol error")
                self.state = 'disabled'
                continue
            
    def start_search_thread(self):
        thread = Thread(target=self.search_serial_num, daemon=True)
        thread.start()
        return thread
    
    def search_serial_num(self):
        find_count = FIND_COUNT
        while find_count > 0 and self.state == 'connected':
            find_count -= 1
            print(f"[LOG] {self.num} - looking for Serial number that matches {self.num}...")
            for reversed_num in flip(SERIAL_NUMBER_LIST):
                select_command = to_select_command(reversed_num)
                self.ser.write(select_command)
                
                if self.ser.read(1) == b'\xE5':
                    print(f"[LOG] {self.num} - {flip(reversed_num)} and {self.num} were successfully matched !")
                    self.data[flip(reversed_num)] = {
                        'state'          : 'detected',
                        'select'         :  select_command,
                        'time'           :  current_time(),
                        'serial_num'     :  None,
                        'flow_rate'      :  None,
                        'total_volume'   :  None
                    }
                    
                    if CHOOSE_ONE_USB:
                        # If you are looking for only one
                        self.data = {flip(reversed_num) : self.data[flip(reversed_num)]}
                        break 
                
                else:
                    self.data[flip(reversed_num)] = {
                        'state'          : 'not detected',
                        'select'         :  select_command,
                        'time'           :  current_time(),
                        'serial_num'     :  None,
                        'flow_rate'      :  None,
                        'total_volume'   :  None
                    }

            # If at least one 'state' in self.data is 'detected'
            if 'detected' in [self.data[key]['state'] for key in list(self.data.keys())]:
                self.state = 'running'
                break 
            
            else:
                print(f"[LOG] {self.num} - Cannot find Serial Number for {self.num}")
                self.state = 'not found'
                pass
                
    def start_read_thread(self):
        if self.state == 'running':
            thread = Thread(target=self.read_data, daemon=True)
            thread.start()
    
    def read_data(self):
        while True:
            for key in list(self.data.keys()):
                select_command = self.data[key]['select']
                self.ser.write(select_command)
                
                if self.ser.read(1) == b'\xE5':
                    repeat = 10
                    while repeat > 0:
                        repeat -= 1
                        
                        self.ser.write(READ_COMMAND)
                        read_data = self.ser.read(39)
                        
                        if read_data == b'':
                            print(f"[ERROR] {self.num} - Eempty response")
                            self.error_cumulative += 1
                            break
                        
                        try:
                            time         = current_time()
                            serial_num   = get_return_serial_num(read_format(read_data, 7, 11))
                            flow_rate    = get_flow_rate(read_format(read_data, 27, 31))
                            total_volume = get_total_volume(read_format(read_data, 21, 25))
                        except:
                            self.state = 'value error'
                            print(f"[ERROR] {self.num} - Eempty response")
                            self.error_cumulative += 1
                            break
                        
                        # Update self.data
                        if key == serial_num:
                            self.data[key] = {
                                'state'          : 'runnuing',
                                'select'         :  select_command,
                                'time'           :  current_time(),
                                'serial_num'     :  key,
                                'flow_rate'      :  flow_rate,
                                'total_volume'   :  total_volume
                            }
                        
                        # Save as csv
                        if USE_CSV:
                            path = f"csv/{current_date()}_{key}"
                            data = [time, serial_num, flow_rate, total_volume]
                            save_as_csv(device=self.name, save_data=data, file_name=path)
                        
                        # Send to db
                        if USE_DB:
                            self.db.send(f"INSERT INTO {self.db.table} (time, serial_num, flow_rate, total_volume) VALUES ('{time}', '{serial_num}', '{flow_rate}', '{total_volume}')")
                        
                        print(f"[READ] {self.num} - {time} | {serial_num:^12} | {flow_rate:11.6f} ㎥/h | {total_volume:11.6f} ㎥ |")
                                   
                else:
                    self.error_cumulative += 1
                
            if self.error_cumulative >= 10:
                print(f"[ERROR] {self.num} - Error accumulates and restarts..")
                self.connect_serial()
                search_thread = self.start_search_thread()
                search_thread.join()
                self.start_read_thread()
                break
                
    # def print_data(self):
    #     if self.state == 'running':
    #         for key in list(self.data.keys()):
    #             state        = self.data[key]['state']
    #             time         = self.data[key]['time']
    #             serial_num   = self.data[key]['serial_num']
    #             flow_rate    = self.data[key]['flow_rate']
    #             total_volume = self.data[key]['total_volume']
                
    #             print(f"[READ] {self.num} - {time.strftime('%Y-%m-%d %H:%M:%S')} | {serial_num:^12} | {flow_rate:11.6f} ㎥/h | {total_volume:11.6f} ㎥ | {state}")
    #             return {
    #                 "time"         : time,
    #                 "serial_num"   : serial_num,
    #                 "flow_rate"    : flow_rate,
    #                 "total_volume" : total_volume
    #             }

    #     else:
    #         return False   