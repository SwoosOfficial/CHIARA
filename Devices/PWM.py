import Devices.Arduino as Arduino
import Devices.Device as Device
import copy


class PWM(Device.Device):
    
    __defaults = {
        "level":0,
        "pwm_desc_char":"P",
        "pwm_number":1
    }
    
    def __init__(self, **kwargs):
        super(PWM, self).__init__()
        defaults = copy.deepcopy(self.__defaults)
        defaults.update(kwargs)
        self.__arduino = Arduino.Arduino()
        self.__level = defaults.pop("level")
        for key, value in defaults.items():
            if key in self.__defaults.keys():
                setattr(self, key, value)
    
    @property
    def level(self):
        with self.lock:
            return self.__level
    
    #@level.setter
    def set_level(self, new_level):
        with self.lock:
            new_level_str="{:03d}".format(int(new_level))
            answer=self.__arduino.write_n_read(self.pwm_desc_char, self.pwm_number, new_level_str)
            self.__level = new_level
            return answer
        
    def initialise(self):
        with self.lock:
            self.__arduino.ensure_comm()
        
    def release(self):
        pass