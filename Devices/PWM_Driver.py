import Devices.Device as Device
import threading
import time
import copy
import numpy as np
from datetime import datetime, timedelta

class DriverOperation(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self, pwm_driver, functionname, time_tup, args, kwargs):
        super(DriverOperation, self).__init__()
        self._stop_event = threading.Event()
        self.pwm_driver=pwm_driver
        self.functionname=functionname
        self.time_tup=time_tup
        self.total_time=time_tup[0]
        self.steps=time_tup[1]
        self.steps_p_time=self.steps/self.total_time
        self.args=args
        self.kwargs=kwargs
        #dyn inits
        self.now = datetime.now().timestamp()
        self.end = self.now + self.total_time
        self.space = np.linspace(self.now, self.end, self.steps)
        self.pos = 0
        self.timeout = False
        
    
    def run(self):
        with self.pwm_driver.lock:
            self.pwm_driver.operating = self
            if self.pwm_driver.relais is not None:
                self.pwm_driver.relais.switch(True)
        #for timeZ in self.space:
        while not self.stopped():
            try:
                getattr(self, self.functionname)(*self.args, **self.kwargs)
            except IndexError:
                break
        with self.pwm_driver.lock:
            if self.pwm_driver.relais is not None and not self.pwm_driver.keepOn:
                self.pwm_driver.relais.switch(False)
            if not self.pwm_driver.keepOn:
                self.pwm_driver.set_level(0)
            self.pwm_driver.operating = None
    
    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()
    
    def do_step_time(self, level, inf=False):
        with self.pwm_driver.lock:
            step=int(self.steps_p_time*(datetime.now().timestamp()-self.now))
            if self.timeout:
                n=0
            else:
                n=1
            if not inf:
                wait=self.space[self.pos+n]
            else:
                wait=self.space[0]+(self.pos+n)/self.steps_p_time
            self.pwm_driver.do_step(step, level)
            self.pos+=n
            self.timeout = not self.wait_until(wait,self.pwm_driver.cancel_timeout)
            
    
    def wait_until(self, end_timestamp, timeout):
        while True:
            diff = min(end_timestamp - datetime.now().timestamp(), timeout)
            val = timeout > diff
            if diff < 0:
                return val      # In case end_datetime was in past to begin with
            time.sleep(diff/2)
            if diff <= 0.1:
                return val


class PWM_Driver(Device.Device):
    
    __defaults = {
        "cancel_timeout" : 0.1,
        "relais" : None,
        "operating" : None,
        "keepOn": True,
    }
    
    def __init__(self, pwm_dev, **kwargs):
        super(PWM_Driver, self).__init__()
        defaults = copy.deepcopy(self.__defaults)
        defaults.update(kwargs)
        self.__pwm_dev = pwm_dev
        for key, value in defaults.items():
            if key in self.__defaults.keys():
                setattr(self, key, value)
    
    def initialise(self):
        pass
        
    def release(self):
        if self.operating is not None:
            self.stop()
    
    def quarter_sine(self, step, steps, startval="None", endval="None"):
        #print("{}/{}".format(step,steps))
        return np.sin((0.5*np.pi/steps)*step)
    
    def quarter_cos(self, step, steps):
        #print("{}/{}".format(step,steps))
        return np.cos((0.5*np.pi/steps)*step)
    
    def quarter_inv_cos(self, step, steps):
        return -1*np.cos((0.5*np.pi/steps)*step)+1
    
    def full_inv_cos(self, step, steps, width=1):
        return -0.5*np.cos((2*np.pi/width)*step)+0.5
    
    def start(self, func, time=3, steps=100, inf=False, **kwargs):
        with self.lock:
            if self.operating is None:
                def level(step):
                    return func(step, steps, **kwargs)
            
                operation = DriverOperation(self, "do_step_time", (time, steps), [level], {"inf":inf})
                operation.start()
                return "Started: "+func.__name__
            return "Did not start \"{}\", because another operation is still running!".format(func.__name__)
        
            
    def stop(self, keepOn=True):
        self.operating.pwm_driver.keepOn = keepOn
        self.operating.stop()
        self.operating.join()
    
    def do_step(self, cur_step, level):
        print(self.__pwm_dev.set_level(int(255*level(cur_step))))
    
    def set_level(self, level):
        self.__pwm_dev.set_level(int(level))
    
    def fade_in(self, time=10, steps=100, startval="None", endval="None"):
        self.keepOn=True
        time=int(time)
        steps=int(steps)
        return self.start(self.quarter_inv_cos, time=time, steps=steps)
    
    def fade_out(self, time=10, steps=100, startval="None", endval="None"):
        self.keepOn=False
        time=int(time)
        steps=int(steps)
        return self.start(self.quarter_cos, time=time, steps=steps)
    
    def breathe(self, time=30, steps=300, width=50, inf=False):
        self.keepOn=True
        time=int(time)
        steps=int(steps)
        width=int(width)
        if inf == "False" or not inf:
            inf=False
        else:
            inf=True
        return self.start(self.full_inv_cos, time=time, steps=steps, inf=inf, width=width)
        
        