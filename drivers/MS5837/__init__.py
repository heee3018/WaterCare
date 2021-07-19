from .ms5837 import * 
unit_atm        = UNITS_atm
unit_Torr       = UNITS_Torr
unit_psi        = UNITS_psi
unit_bar        = UNITS_bar
unit_Centigrade = UNITS_Centigrade
unit_Farenheit  = UNITS_Farenheit
unit_Kelvin     = UNITS_Kelvin

def Setup():
        i2c = MS5837_30BA() 
        if not i2c.init():
                print("MS5837 Sensor could not be initialized")
                return False
                
        if not i2c.read():
                print("Sensor read failed!")
                return False
                
        print("Pressure: %.2f atm  %.2f Torr  %.2f psi" % (
        i2c.pressure(UNITS_atm),
        i2c.pressure(UNITS_Torr),
        i2c.pressure(UNITS_psi)))

        print("Temperature: %.2f C  %.2f F  %.2f K" % (
        i2c.temperature(UNITS_Centigrade),
        i2c.temperature(UNITS_Farenheit),
        i2c.temperature(UNITS_Kelvin)))

        freshwaterDepth = i2c.depth() # default is freshwater
        i2c.setFluidDensity(DENSITY_SALTWATER)
        saltwaterDepth = i2c.depth() # No nead to read() again
        i2c.setFluidDensity(1000) # kg/m^3
        print("Depth: %.3f m (freshwater)  %.3f m (saltwater)"% (freshwaterDepth, saltwaterDepth))

        # fluidDensity doesn't matter for altitude() (always MSL air density)
        print("MSL Relative Altitude: %.2f m"% i2c.altitude()) # relative to Mean Sea Level pressure in air
        print("\n")
        
        return i2c
