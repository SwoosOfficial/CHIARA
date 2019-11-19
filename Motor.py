import time
import Arduino
import Device

class Motor(Device.Device):

    __default_sequence = (
        (1,0,0,0),
        (1,1,0,0),
        (0,1,0,0),
        (0,1,1,0),
        (0,0,1,0),
        (0,0,1,1),
        (0,0,0,1),
        (1,0,0,1)
    )
    
    __default_properties = {
        "max_pos":270,
        "full_speed_delay":50,
        "sequence":__default_sequence
        
    }
     
    __defaults = {
        "motor_properties":__default_properties,
        "init_pos":0,
        "motor_desc_char":"M",
        "motor_number":1
    }
    
    def __init__(self, pos, **kwargs):
        super(Motor, self).__init__()
        defaults = self.__defaults
        defaults.update(kwargs)
        self.__arduino = Arduino.Arduino()
        self.__pos=pos
        for key, value in defaults.items():
            if key in self.__defaults.keys():
                setattr(self, key, value)
    @property
    def pos(self):
        return self.__pos
    
    @pos.setter
    def pos(self, new_pos):
        #saveFile.save(self, new_pos)
        self.__pos=new_pos
    
    def initialise(self):
        with self.lock:
            self.__arduino.ensure_comm()
            self.drive_to_pos(self.init_pos)
        
    def release(self):
        with self.lock:
            self.set_step(0,0,0,0)  

    def set_step(self, w1, w2, w3, w4):
        with self.lock:
            self.__arduino.write(self.motor_desc_char, self.motor_number, str(w1)+str(w2)+str(w3)+str(w4))
 
    def forward(self, delay, steps):
        with self.lock:
            steps=int(steps)
            delay=int(delay)
            sequence=self.motor_properties["sequence"]
            for i in range(steps):
                for j in range(len(sequence)):
                    self.set_step(sequence[j][0], sequence[j][1], sequence[j][2], sequence[j][3])
                    time.sleep(delay)
            self.pos+=steps
            self.set_step(0,0,0,0) 

    def backward(self, delay, steps):
        with self.lock:
            steps=int(steps)
            delay=int(delay)
            sequence=self.motor_properties["sequence"]
            for i in range(steps):
                for j in reversed(range(len(sequence))):
                    self.set_step(sequence[j][0], sequence[j][1], sequence[j][2], sequence[j][3])
                    time.sleep(delay)
            self.pos-=steps#
            self.set_step(0,0,0,0)
                
    def drive_to_pos(self, d_pos, delay=None):
        d_pos=int(d_pos)
        if delay is None:
            delay=self.motor_properties["full_speed_delay"]
        else:
            delay=int(delay)
        if d_pos > self.pos:
                self.backward(delay / 1000.0, d_pos-self.pos)
        elif d_pos < self.pos:
                self.forward(delay / 1000.0, self.pos-d_pos)
        self.pos = d_pos