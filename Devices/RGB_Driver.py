import Devices.PWM_Driver as PWM_Driver
import Devices.Device as Device


class RGB_Driver(PWM_Driver.PWM_Driver):
    
    def __init__(self, red_driver, green_driver, blue_driver, **kwargs):
        super(Device.Device, self).__init__()
        self.RGB={
                  "red" : red_driver,
                  "green" : green_driver,
                  "blue" : blue_driver
                  }
        
    def initialise(self):
        #for pwm_driver in self.RGB:
        #    pwm_driver.initialise()
        pass
        
    def release(self):
        if self.operating is not None:
            raise NotYetImplementedError
            self.stop()
            for pwm_driver in self.RGB:
                self.RGB[pwm_driver].release()
        else:
            #for pwm_driver in self.RGB:
            #    pwm_driver.release()
            pass
    
    def start(self, func, time=3, steps=100, inf=False, **kwargs):
        raise NotYetImplementedError
        
            
    def stop(self, keepOn=True):
        if self.operating is not None:
            raise NotYetImplementedError
            self.operating.pwm_driver.keepOn = keepOn
            self.operating.stop()
            self.operating.join()
        else:
            for pwm_driver in self.RGB:
                pwm_driver.stop()
    
    def do_step(self, cur_step, rgb_tuple):
        raise NotYetImplementedError
    
    def set_level(self, level):
        for pwm_driver, color in zip(self.RGB, rgb_tuple):
            pwm_driver.set_level(int(255*level(color)))
    
    def fade_in(self,
                time=10,
                steps=100,
                start_rgb_tup=("None","None","None"),
                end_rgb_tup=("None","None","None")):
        time=int(time)
        steps=int(steps)
        answers=[]
        for pwm_driver, start_color, end_color in zip(self.RGB, start_rgb_tup, start_rgb_tup):
            pwm_driver.keepOn=True
            answers.append(pwm_driver.start(pwm_driver.quarter_inv_cos,
                                            time=time,
                                            steps=steps,
                                            startval=start_color,
                                            endval=end_color)
                           )
        return self.__compose_answer(answers)
    
    def fade_out(self,
                 rgb_tuple,
                 time=10,
                 steps=100,
                 start_rgb_tup=("None","None","None"),
                 end_rgb_tup=("None","None","None")):
        time=int(time)
        steps=int(steps)
        answers=[]
        for pwm_driver, start_color, end_color in zip(self.RGB, start_rgb_tup, start_rgb_tup):
            pwm_driver.keepOn=False
            answers.append(pwm_driver.start(pwm_driver.quarter_cos,
                                            time=time,
                                            steps=steps,
                                            startval=start_color,
                                            endval=end_color)
                           )
        return self.__compose_answer(answers)
    
    def breathe(self, rgb_tuple, time=30, steps=300, width=50, inf=False, low_color_tup=("None","None","None"), high_color_tup=("None","None","None")):
        time=int(time)
        steps=int(steps)
        width=int(width)
        answers=[]
        for pwm_driver, start_color, end_color in zip(self.RGB, start_rgb_tup, start_rgb_tup):
            pwm_driver.keepOn=True
            answers.append(pwm_driver.start(pwm_driver.full_inv_cos,
                                            time=time,
                                            steps=steps,
                                            startval=start_color,
                                            endval=end_color)
                           )
        return self._compose_answer(answers)
    
    def __compose_answer(self, answers):
        for pwm_driver, answer in zip(self.RGB, answers):
            if answer[:5] != "Star":
                return "Failed ({}):".format(pwm_driver.__name__) + answer
            return "Started fade_in"

                
    