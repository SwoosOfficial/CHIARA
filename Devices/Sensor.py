import Devices.Device as Device
from abc import abstractmethod

class Sensor(Device.Device):
    
    def __init__(self, **kwargs):
        super(Sensor, self).__init__()
    
    @abstractmethod
    def read(self):
        pass
    
    