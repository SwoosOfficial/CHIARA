import subprocess
import Devices.Device as Device
import copy



class PWM(Device.Device):
    
    __defaults = {
        "level":0,
        "pwm_desc_char":"P",
        "pwm_number":17,
        "frequency":0.25,
    }
    
    def __init__(self, **kwargs):
        super(PWM, self).__init__()
        defaults = copy.deepcopy(self.__defaults)
        defaults.update(kwargs)
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
            subprocess.run(["pigs", "p", str(self.pwm_number), str(int(255*new_level))] )
            return new_level
        
    def initialise(self):
        with self.lock:
            subprocess.run(["pigs", "modes", str(self.pwm_number), "w"] )
        
    def release(self):
        self.set_level(0)
        with self.lock:
            subprocess.run(["pigs", "modes", str(self.pwm_number), "r"] )