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
        self.name        = 'lxc'
        self.state       = 'init'
        self.data        =  { }
        self.num         =  num
        self.serial_port =  port
        self.db          =  database.Setup(HOST, USER, PASSWORD, DB, TABLE)
        
        find_count = FIND_COUNT
        while find_count > 0:
            find_count -= 1
            
            try: 
                self.ser = Serial(port=self.serial_port, baudrate=2400, parity='E', timeout=1)
                self.ser.open()
                self.state = 'connected'
                
            except OSError as e:
                error_message = str(e)
                error_port    = error_message[error_message.find('/dev/ttyUSB'):error_message.find(':')]
                if error_message[:9] == '[Errno 2]':
                    print(f"[ERROR] {self.num} - {error_port} Could not open port. {find_count+1}/{FIND_COUNT}")
                
                self.state = 'disable'
                
            except serialutil.SerialException as e:
                error_message = str(e)
                error_port    = error_message[error_message.find('/dev/ttyUSB'):error_message.find(':')]
                if error_message[:9] == '[Errno 2]':
                    print(f"[ERROR] {self.num} - {error_port} Could not open port. {find_count+1}/{FIND_COUNT}")
                
                self.state = 'disable'
        
    def find_serial_num(self):
        find_count = FIND_COUNT
        while find_count > 0 and self.state == 'connected':
            find_count -= 1
        
            for reversed_num in flip(SERIAL_NUMBER_LIST):
                select_command = to_select_command(reversed_num)
                self.ser.write(select_command)
                
                if self.ser.read(1) == b'\xE5':
                    print(f"[LOG] {self.num} - {flip(reversed_num)} was successfully selected.")
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
                print(f"[ERROR] {self.num} - couldn't find anything")
                self.state = 'not found'
                pass
                
    def start_thread(self):
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
                            self.state = 'empty response'
                            break
                        
                        try:
                            time         = current_time()
                            serial_num   = get_return_serial_num(read_format(read_data, 7, 11))
                            flow_rate    = get_flow_rate(read_format(read_data, 27, 31))
                            total_volume = get_total_volume(read_format(read_data, 21, 25))
                            
                        except:
                            print(f"[ERROR] {self.num} - read_data : {read_data}")
                            self.state = 'get error'
                            break
                        
                        if key == serial_num:
                            self.data[key] = {
                                'state'          : 'runnuing',
                                'select'         :  select_command,
                                'time'           :  current_time(),
                                'serial_num'     :  key,
                                'flow_rate'      :  flow_rate,
                                'total_volume'   :  total_volume
                            }
                            
                        if USE_CSV:
                            path = f"csv/{current_date()}_{key}"
                            data = [self.data[key]['time'], 
                                    self.data[key]['serial_num'], 
                                    self.data[key]['flow_rate'], 
                                    self.data[key]['total_volume']]
                            save_as_csv(device=self.name, save_data=data, file_name=path)
                        
                        if USE_DB:
                            self.db.send(f"INSERT INTO {self.db.table} (time, serial_num, flow_rate, total_volume) VALUES ('{time}', '{serial_num}', '{flow_rate}', '{total_volume}')")
                        
                        print(f"[READ] {self.num} - {time} | {serial_num:^12} | {flow_rate:11.6f} ㎥/h | {total_volume:11.6f} ㎥ |")
                                   
                else:
                    self.data[key] = {
                        'state'          : 'reading error',
                        'select'         :  select_command,
                        'time'           :  current_time(),
                        'serial_num'     :  None,
                        'flow_rate'      :  None,
                        'total_volume'   :  None
                    }
                


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