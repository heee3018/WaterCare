from .ms5837 import * 
# 수
def Setup():
        i2c = MS5837_30BA() 
        if not i2c.init():
                print("Sensor could not be initialized")
                exit(1)
        if not i2c.read():
                print("Sensor read failed!")
                exit(1)
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

        return i2c
