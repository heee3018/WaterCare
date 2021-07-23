from threading import Thread
from serial    import Serial
from serial    import serialutil
from config    import USE_DB
from config    import SAVE_CSV
from config    import FIND_COUNT
from config    import ADDRESS_LIST
from config    import CHOOSE_ONE_USB
from config    import DETECTED_ADDRESS
from drivers   import db
from drivers   import save_csv
from drivers.lxc_util import flip
from drivers.lxc_util import read_format
from drivers.lxc_util import current_time
from drivers.lxc_util import read_command
from drivers.lxc_util import to_select_command
from drivers.lxc_util import get_flow_rate
from drivers.lxc_util import get_total_volume
from drivers.lxc_util import get_return_address

    
class Setup:
    def __init__(self, name, port):
        self.state       = 'init'
        self.address     =  dict()
        self.name        =  name
        self.serial_port =  port
        self.db          =  db.Setup()
        
        self.set_serial()
        self.find_address()

        print(f"[LOG] {self.name} - state : '{self.state}'")
        
    def set_serial(self):
        find_count = FIND_COUNT
        while find_count > 0:
            find_count -= 1
            
            try: 
                self.ser = Serial(port=self.serial_port, baudrate=2400, parity='E', timeout=1)
                
                if self.ser.is_open is False:
                    print(f"[ERROR] {self.name} - 'self.ser' is closed.")
                    
                self.state = 'connected'
                
                break
                
            except serialutil.SerialException as e:
                error_message = str(e)
                error_port    = error_message[error_message.find('/dev/ttyUSB'):error_message.find(':')]
                if error_message[:9] == '[Errno 2]':
                    print(f"[ERROR] {self.name} - {error_port} Could not open port. {find_count+1}/{FIND_COUNT}")
                
                self.state = 'disable'
        
    def find_address(self):
        find_count = FIND_COUNT
        while find_count > 0 and self.state == 'connected':
            find_count -= 1
            
            address_list  = ADDRESS_LIST
            inverted_list = flip(address_list)
            
            for inverted_address in inverted_list:
                if inverted_address in DETECTED_ADDRESS:
                    # print(f"[LOG] {self.name} - {flip(inverted_address)} has already been detected. -> continue")
                    continue
                
                select_command = to_select_command(inverted_address)
                self.ser.write(select_command)
                
                response = self.ser.read(1)
                
                if response == b'\xE5':
                    print(f"[LOG] {self.name} - {flip(inverted_address)} was successfully selected.")
                    
                    DETECTED_ADDRESS.append(inverted_address)
                    # print(f"[LOG] {self.name} - Add {flip(inverted_address)} to DETECTED_ADDRESS")
                    
                    self.address[flip(inverted_address)] = {
                        'state'          : 'detected',
                        'select'         :  select_command,
                        'time'           :  current_time(),
                        'address'        :  flip(inverted_address),
                        'return_address' : '11111111',
                        'flow_rate'      :  1.111111,
                        'total_volume'   :  1.111111
                    }
                    # print(f"[LOG] {self.name} - Added the contents of {flip(inverted_address)} to 'self.address'")
                    
                    if CHOOSE_ONE_USB:
                        # If you are looking for only one
                        self.address = {flip(inverted_address) : self.address[flip(inverted_address)]}
                        break 
                
                else:
                    self.address[flip(inverted_address)] = {
                        'state'          : 'not detected',
                        'select'         :  select_command,
                        'time'           :  current_time(),
                        'address'        :  flip(inverted_address),
                        'return_address' : '99999999',
                        'flow_rate'      :  9.999999,
                        'total_volume'   :  9.999999
                    }
                    # print(f"[LOG] {self.name} - Couldn't find {flip(inverted_address)}")                    
                    pass

            if 'detected' in [self.address[key]['state'] for key in list(self.address.keys())]:
                self.state = 'running'
                break 
            
            else:
                print(f"[ERROR] {self.name} - couldn't find anything")
                self.state = 'not found'
                pass
                
    def start_thread(self):
        thread = Thread(target=self.to_read)
        thread.daemon = False
        thread.start()
    
    def to_read(self):
        while self.state == 'running':
            for key in list(self.address.keys()):
            
                if self.address[key]['state'] == 'detected': 
                    pass
                elif self.address[key]['state'] == 'reading success': 
                    pass
                else: 
                    continue 
                
                select_command = self.address[key]['select']
                self.ser.write(select_command)
                
                response = self.ser.read(1)
                
                if response == b'\xE5':
                    
                    self.ser.write(read_command)
                    
                    read_data = self.ser.read(39)
                    
                    if read_data == b'': 
                        self.state = 'empty response'
                        break
                    
                    try:
                        return_address = get_return_address(read_format(read_data, 7, 11))
                        flow_rate      = get_flow_rate(read_format(read_data, 27, 31))
                        total_volume   = get_total_volume(read_format(read_data, 21, 25))
                        
                    except:
                        print(f"[ERROR] {self.name} - read_data : {read_data}")
                        self.state = 'get error'
                        break
                    
                    if key == return_address:
                        self.address[key] = {
                            'state'          : 'reading success',
                            'select'         :  select_command,
                            'time'           :  current_time(),
                            'address'        :  key,
                            'return_address' :  return_address,
                            'flow_rate'      :  flow_rate,
                            'total_volume'   :  total_volume
                        }
                        
                    if CHOOSE_ONE_USB:
                        self.to_list = [
                            self.address[key]['time'],
                            self.address[key]['address'],
                            self.address[key]['flow_rate'],
                            self.address[key]['total_volume']
                        ]
                        
                    if SAVE_CSV:
                        path = f'csv/{key}_dt.'
                        save_csv.lxc_to_csv(path=path, data=self.to_list)
                        
                    if USE_DB:
                        self.db.send_lxc(data=self.to_list)
                        
        
                    
                else:
                    self.address[key] = {
                        'state'          : 'reading error',
                        'select'         :  select_command,
                        'time'           :  current_time(),
                        'address'        :  key,
                        'return_address' : '99999999',
                        'flow_rate'      :  9.999999,
                        'total_volume'   :  9.999999
                    }
        
        self.__init__(name=self.name, port=self.serial_port)


    def print_data(self):
        if self.state == 'running':
            for key in list(self.address.keys()):
                state        = self.address[key]['state']
                time         = self.address[key]['time']
                address      = self.address[key]['address']
                flow_rate    = self.address[key]['flow_rate']
                total_volume = self.address[key]['total_volume']
                
                print(f'[READ] {self.name} - {time} | {address} | {flow_rate:10.6f}㎥/h | {total_volume:10.6f}㎥ | {state}')
        
        else:
            pass        