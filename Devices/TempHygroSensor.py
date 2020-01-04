import Devices.Sensor as Sensor
import Adafruit_DHT


class TempHygroSensor(Sensor.Sensor):
    
    __defaults = {
        "sensor":Adafruit_DHT.AM2302,
        "pin":"4"
    }
    
    def __init__(self, **kwargs):
        super(TempHygroSensor, self).__init__()
        defaults = self.__defaults
        defaults.update(kwargs)
        for key, value in defaults.items():
            if key in self.__defaults.keys():
                setattr(self, key, value)
    
    def initialise(self):
        pass
    
    def release(self):
        pass
    
    def read(self):
        with self.lock:
            hum, temp =Adafruit_DHT.read_retry(self.sensor, self.pin)
            return 'Temperature: {:3.1f} °C\r\nHumidity {:3.1f} %'.format(temp, hum)