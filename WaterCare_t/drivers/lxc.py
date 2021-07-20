from serial  import Serial, serialutil
from config  import ADDRESS_LIST
from config  import DETECTED_ADDRESS
from drivers.lxc_util import flip
from drivers.lxc_util import read_command
from drivers.lxc_util import to_select_command
from drivers.lxc_util import current_time
from drivers.lxc_util import read_format
from drivers.lxc_util import get_return_address
from drivers.lxc_util import get_flow_rate
from drivers.lxc_util import get_total_volume

class Setup:
    def __init__(self, name, port):
        self.address = dict()
        self.state   = 'init' # 'good' or 'error'
        self.name    = name
        
        try: 
            self.ser = Serial(port=port, baudrate=2400, parity='E', timeout=1)
            
            if self.ser.is_open is False:
                print(f"[ERROR] {self.name} 'self.ser' is closed.")
            
            self.find_address()
            
        except serialutil.SerialException as e:
            error_message = str(e)
            error_port    = error_message[error_message.find('/dev/ttyUSB'):error_message.find(':')]
            if error_message[:9] == '[Errno 2]':
                print(f"[ERROR] {self.name} - {error_port} Could not open port.")
            self.state = 'desable'
        
        
    def find_address(self):
        address_list  = ADDRESS_LIST
        inverted_list = flip(address_list)
        
        for inverted_address in inverted_list:
            if inverted_address in DETECTED_ADDRESS:
                print(f"[LOG] {inverted_address} has already been detected. -> continue")
                continue
            
            select_command = to_select_command(inverted_address)
            self.ser.write(select_command)
            
            response = self.ser.read(1)
            
            if response == b'\xE5':
                self.state = 'good'
                print(f"[LOG] {inverted_address} was successfully selected.")
                
                DETECTED_ADDRESS.append(inverted_address)
                print(f"[LOG] Add {inverted_address} to DETECTED_ADDRESS")
                
                self.address[flip(inverted_address)] = {
                    'state'       : 'is detected',
                    'select'      :  select_command,
                    'time'        :  current_time(),
                    'address'     :  flip(inverted_address),
                    'flow_rate'   :  0.0,
                    'total_volume':  0.0
                }
                print(f"[LOG] Added the contents of {inverted_address} to 'self.address'")
                
            else:
                print(f"[LOG] Couldn't find {inverted_address}")
                
                self.address[flip(inverted_address)] = {
                    'state'       : 'select error',
                    'select'      :  select_command,
                    'time'        :  current_time(),
                    'address'     : '99999999',
                    'flow_rate'   :  9.999999,
                    'total_volume':  9.999999
                 }
        
        if self.address == {}:
            self.state = 'error'
            print(f"[ERROR] {self.name} - Could not find anything.")
            # self.find_address()
            
        elif '99999999' in list(self.address.keys()):
            self.state = 'error'
            print("[ERROR] 'self.address' contains an Error code(99999999)")
            # self.find_address()  
    
    def to_read(self):
        if self.state == 'good':
            for key in list(self.address.key()):
            
                select_command = self.address[key]['select']
                self.ser.write(select_command)
                
                response = self.ser.read(1)
                
                if response == b'\xE5':
                    self.ser.write(read_command)
                    read_data = self.ser.read(39)
                    
                    return_address = get_return_address(read_format(read_data, 7, 11))
                    flow_rate      = get_flow_rate(read_format(read_data, 27, 31))
                    total_volume   = get_total_volume(read_format(read_data, 21, 25))

                    self.address[key] = {
                        'state'       : 'read data',
                        'select'      :  select_command,
                        'time'        :  current_time(),
                        'address'     :  return_address,
                        'flow_rate'   :  flow_rate,
                        'total_volume':  total_volume
                    }
                    
                else:
                    self.address[key] = {
                        'state'       : 'read error',
                        'select'      :  select_command,
                        'time'        :  current_time(),
                        'address'     : '99999999',
                        'flow_rate'   :  9.999999,
                        'total_volume':  9.999999
                    }

        elif self.state == 'desable':
            pass
        
        else:
            print(f"[ERROR] {self.name} - Please check 'self.state = {self.state}'.")
        
        
    def print_data(self):
        if self.state == 'good':
            for key in list(self.address.key()):
                time         = self.address[key]['time']
                address      = self.address[key]['address']
                flow_rate    = self.address[key]['flow_rate']
                total_volume = self.address[key]['total_volume']
                
                print(f'[READ] {self.name} - {time} | {address} | {flow_rate:11.6f}㎥/h | {total_volume:11.6f}㎥')
        
        else:
            pass        
        