import Devices.Arduino as Arduino
import Devices.Device as Device
import copy


class Relais(Device.Device):
    
    __defaults = {
        "inverted":False,
        "state":False,
        "relais_desc_char":"R",
        "relais_number":1
    }
    
    def __init__(self, **kwargs):
        super(Relais, self).__init__()
        defaults = copy.deepcopy(self.__defaults)
        defaults.update(kwargs)
        self.__arduino = Arduino.Arduino()
        self.__state = defaults.pop("state")
        for key, value in defaults.items():
            if key in self.__defaults.keys():
                setattr(self, key, value)
    
    @property
    def state(self):
        with self.lock:
            return self.__state
    
    #@state.setter
    #def state(self, new_state):
        #self.__state=new_state
        
    def initialise(self):
        with self.lock:
            self.__arduino.ensure_comm()
        
    def release(self):
        pass
    
    def switch(self, state):
        with self.lock:
            if state == "False":
                state=False
            if self.inverted != state:
                int_state=1
            else:
                int_state=0
            answer=self.__arduino.write_n_read(self.relais_desc_char, self.relais_number, str(int_state))
            self.__state = state
            return answer
