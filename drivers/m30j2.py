from smbus     import SMBus
from time       import sleep
from datetime   import datetime
from ctypes     import c_uint

from threading       import Thread
from config          import USE_DB, USE_CSV
from config          import HOST, USER, PASSWORD, DB, TABLE 
from drivers         import database
from drivers.library import current_time, current_date, save_as_csv, check_internet

# Conversion factors (from native unit, mbar)
UNITS_Pa     = 100.0
UNITS_hPa    = 1.0
UNITS_kPa    = 0.1
UNITS_mbar   = 1.0
UNITS_bar    = 0.001
UNITS_atm    = 0.000986923
UNITS_Torr   = 0.750062
UNITS_psi    = 0.014503773773022

# Valid units
UNITS_Centigrade = 1
UNITS_Farenheit  = 2
UNITS_Kelvin     = 3

# Oversampling options
OSR_256  = 0
OSR_512  = 1
OSR_1024 = 2
OSR_2048 = 3
OSR_4096 = 4
OSR_8192 = 5

def unsigned(n):
    return c_uint(n).value

def toHex(read):
    res = [None] * len(read)
    
    for i in range(len(read)):
        res[i] = hex(read[i])
    return res    

class M30J2(object):
    _ADDRESS = 0x28
    _P1      = 1638.3   # 10% * 16383 -A Type # 2^14
    _P2      = 13106.4  # 80% * 16383 -A Type # 2^14
    _P_MAX   = 15.0
    _P_MIN   = 0.0
    
    def __init__(self, tag):
        self.bus = SMBus(1)
    
    def init(self):
        if self.bus is None:
            print(f"No bus")
            return False
        
        return True
    
    def read(self, oversampling=OSR_8192):
        if self.bus is None:
            print(f"No bus")
            return False
        
        if oversampling < OSR_256 or oversampling > OSR_8192:
            print("Invalid oversampling option!")
            return False
        
        sleep(2.5e-6 * 2**(8+oversampling)) # 0.02048
        
        read = self.bus.read_i2c_block_data(self._ADDRESS, 0, 4)
        
        print(' S ' + str(bin(self._ADDRESS | 0x100))[4:] + 'R' + ' A ' + str(bin(read[0] | 0x100))[3:] + ' A ' + str(bin(read[1] | 0x100))[3:] + ' A ' 
            + str(bin(read[2] | 0x100))[3:] + ' A ' + str(bin(read[3] | 0x100))[3:] + ' N P ' )
        
        if (read[0] & 0xc0) == 0x00:
            d_pressure    = (unsigned((read[0] & 0x3f) << 8) + read[1])
            d_temperature = (unsigned((read[2]) << 3) + read[3] >> 5)
            self._pressure    = (d_pressure - self._P1) * (self._P_MAX - self._P_MIN) / self._P2 + self._P_MIN
            self._temperature = (d_temperature * 200) / 2047 - 50
        
        else:
            return False
        
    def pressure(self, conversion=UNITS_bar):
        return self._pressure * conversion

    def temperature(self, conversion=UNITS_Centigrade):
        degC = self._temperature / 100.0
        
        if conversion == UNITS_Farenheit:
            return (9.0/5.0)*degC + 32
        
        elif conversion == UNITS_Kelvin:
            return degC + 273
        
        return degC
        
    
class Setup(M30J2):
    def __init__(self, tag, interval):
        M30J2.__init__(self, tag)
        self.name     = 'm30j2'
        self.tag      =  tag
        self.data     =  { }
        self.interval = interval
        
        if not self.init():
            print(f"{'[ERROR]':>10} {self.tag} - M30J2 Sensor could not be initialized")
        if not self.read():
            print(f"{'[ERROR]':>10} {self.tag} - Sensor read failed!")
        else:
            print(f"{'[LOG]':>10} {self.tag} - Pressure: {self._pressure:.2f} bar  Temperature:  {self._temperature:.2f} C")
    
    def connect_db(self):
        if USE_DB and check_internet():
            self.db = database.Setup(HOST, USER, PASSWORD, DB, TABLE)
            # print(f"{'[LOG]':>10} {self.tag} - You have successfully connected to the db!")
        
        elif USE_DB and not check_internet():
            print(f"{'[WARNING]':>10} {self.tag} - You must be connected to the internet to connect to the db.")
    
    def start_read_thread(self):
        thread = Thread(target=self.read_data, daemon=True)
        thread.start()
    
    def read_data(self):
        while True:
            sleep(self.interval)
            try:
                if not self.init():
                    print(f"{'[ERROR]':>10} {self.tag} - M30J2 Sensor could not be initialized")
                if not self.read():
                    print(f"{'[ERROR]':>10} {self.tag} - Sensor read failed!")
                else:
                
                    time        = current_time()
                    print(f"{'[READ]':>10} {self.tag} - {time} | {'':12} | {self._pressure:11.6f} bar  | {self._temperature:11.6f} C  |")
                    # pressure    = self._pressure
                    # temperature = self._temperature
    
                    # self.data['serial_num'] = {
                    #     'time'        : time,
                    #     'pressure'    : pressure,
                    #     'temperature' : temperature
                    # }
                    # if USE_CSV:
                    #     path = f"csv/{current_date()}_{'ms5837'}"
                    #     data = [time, pressure, temperature]
                    #     save_as_csv(device=self.name, data=data, path=path)
                        
                    # if USE_DB:
                    #     self.db.send(f"INSERT INTO {self.db.table} (time, pressure, temperature) VALUES ('{time}', '{pressure}', '{temperature}')")
                    
                    
            except OSError:
                time = current_time()
                print(f"{'[ERROR]':>10} {self.tag} - {time} | {'':48} |")
                # print(f"{'[ERROR]':>10} I2C_0 - {time} | {'':12} | {'':16} | {'':14} |")
                # print(f"{'[ERROR]':>10} I2C_0 - {time} | {'MS5837 Sensor not found.':^48} |")
