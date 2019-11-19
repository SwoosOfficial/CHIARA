import Arduino
import Sensor

class WaterSensor(Sensor.Sensor):
    
    __defaults = {
        "desc_char":"W",
    }
    
    def __init__(self, **kwargs):
        defaults = self.__defaults
        defaults.update(kwargs)
        self.__arduino = Arduino.Arduino()
        for key, value in defaults.items():
            if key in self.__defaults.keys():
                setattr(self, key, value)
    
        
    def initialise(self):
        self.__arduino.ensure_comm()
        
    def release(self):
        pass
    
    def read(self):
        self.__arduino.write(self.desc_char, "", "")
