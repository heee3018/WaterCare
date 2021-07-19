from serial  import Serial
from config  import ADDRESS_LIST
from config  import DETECTED_ADDRESS
from drivers.lxc_util import flip
from drivers.lxc_util import read_command
from drivers.lxc_util import to_select_command
from drivers.lxc_util import current_time

class Setup:
    def __init__(self, name, port):
        self.address = dict()
        self.name    = name
        self.ser     = Serial(port=port, baudrate=2400, parity='E', timeout=1)
        
        if self.ser.is_open is False:
            print(f"[ERROR] {self.name} 'self.ser' is closed")
            
        
        # self.find_address()
        
        
    def find_address(self):
        address_list  = ADDRESS_LIST
        inverted_list = flip(address_list)
        
        for inverted_address in inverted_list:
            if inverted_address in DETECTED_ADDRESS:
                print(f"[LOG] {inverted_address} has already been detected. -> continue")
                continue
            
            select_command = to_select_command(inverted_address)
            print("[LOG] Write Select command")
            self.ser.write(select_command)
            
            response = self.ser.read(1)
            print("[LOG] Read One byte")
            
            if response == b'\xE5':
                print(f"[LOG] {inverted_address} was successfully selected.")
                
                DETECTED_ADDRESS.append(inverted_address)
                print(f"[LOG] Add {inverted_address} to DETECTED_ADDRESS")
                
                self.address[flip(inverted_address)] = {
                    'state'       : 'is detected',
                    'select'      : select_command,
                    'time'        : current_time(),
                    'address'     : flip(inverted_address),
                    'flow_rate'   : 0.0,
                    'total_volume': 0.0
                }
                print(f"[LOG] Added the contents of {inverted_address} to 'self.address'")
                
            else:
                print(f"[LOG] Couldn't find {inverted_address}")
        
        
        if self.address == {}:
            print("[ERROR] Couldn't find anything.")
            print("[ERROR] re-execute the 'find_address' function")
            self.find_address()
            
        elif '99999999' in list(self.address.keys()):
            print("[ERROR] 'self.address' contains an Error code(99999999)")
            print("[ERROR] re-execute the 'find_address' function")
            
            self.find_address()  
            