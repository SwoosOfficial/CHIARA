import Devices.PWM_Driver as PWM_Driver
import Devices.Device as Device
import pygame
import time
import threading

from collections import OrderedDict


class RGBDriverOperation(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self, rgb_driver, functionname, kwargs):
        super(RGBDriverOperation, self).__init__()
        self._stop_event = threading.Event()
        self.rgb_driver=rgb_driver
        self.functionname=functionname
        #self.args=args
        self.kwargs=kwargs
    
    def run(self):
        with self.rgb_driver.lock:
            self.rgb_driver.operating = self
        while not self.stopped():
            self.kwargs["init_color"]=getattr(self.rgb_driver, self.functionname)(**self.kwargs)
        with self.rgb_driver.lock:
            self.rgb_driver.operating = None
    
    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()
        

class RGB_Driver(PWM_Driver.PWM_Driver):
    
    def __init__(self, red_driver, green_driver, blue_driver, **kwargs):
        Device.Device.__init__(self)
        self.RGB=OrderedDict(
                  [("red", red_driver),
                  ("green", green_driver),
                  ("blue", blue_driver)]
                  )
        self.operating=None
        
    def initialise(self):
        #for pwm_driver in self.RGB:
        #    pwm_driver.initialise()
        pygame.mixer.init()
        pygame.mixer.music.load("gong.mp3")
        pass
        
    def release(self):
        self.stop()
    
    def start(self, func, time=3, steps=100, inf=False, **kwargs):
        raise NotYetImplementedError
        
            
    def stop(self, abort=True):
        if self.operating is not None:
            self.operating.stop()
        
        if abort:
            for pwm_driver in self.RGB:
                self.RGB[pwm_driver].stop()
                self.RGB[pwm_driver].set_level(0)
            
        if self.operating is not None:
            self.operating.join()
    
    def do_step(self, cur_step, rgb_tuple):
        raise NotYetImplementedError
    
    def set_level(self, rgb_tuple):
        for pwm_driver, color in zip(self.RGB, rgb_tuple):
            self.RGB[pwm_driver].set_level(color)
    
    def join_RGB(self):
        for pwm_driver in self.RGB:
            try:
                self.RGB[pwm_driver].operating.join()
            except AttributeError:
                pass
    
    def fade_in(self,
                time=10,
                steps=100,
                start_rgb_tup=(0,0,0),
                end_rgb_tup=(1,1,1), func="inv_cos"):
        answers=[]
        for pwm_driver, start_color, end_color in zip(self.RGB,  start_rgb_tup,  end_rgb_tup):
            self.RGB[pwm_driver].keepOn=True
            if func == "inv_cos":
                answers.append(self.RGB[pwm_driver].fade_in(
                                            time=time,
                                            steps=steps,
                                            start_val=start_color,
                                            end_val=end_color)
                           )
            elif func == "sine":
                answers.append(self.RGB[pwm_driver].fade_in_sine(
                                            time=time,
                                            steps=steps,
                                            start_val=start_color,
                                            end_val=end_color)
                               )
            else:
                raise NotYetImplementedError 
        return self.__compose_answer(answers)
    
    def fade_out(self,
                 time=10,
                 steps=100,
                 start_rgb_tup=(1,1,1),
                 end_rgb_tup=(0,0,0)):
        answers=[]
        for pwm_driver, start_color, end_color in zip(self.RGB, start_rgb_tup, end_rgb_tup):
            self.RGB[pwm_driver].keepOn=False
            answers.append(self.RGB[pwm_driver].fade_out(
                                            time=time,
                                            steps=steps,
                                            start_val=start_color,
                                            end_val=end_color)
                           )
        return self.__compose_answer(answers)
    
    def breathe(self,
                time=30,
                steps=300,
                width=50,
                inf=False,
                low_color_tup=(0,0,0),
                high_color_tup=(1,1,1)):
        answers=[]
        for pwm_driver, start_color, end_color in zip(self.RGB, low_color_tup, high_color_tup):
            self.RGB[pwm_driver].keepOn=True
            answers.append(self.RGB[pwm_driver].breathe(
                                            time=time,
                                            steps=steps,
                                            width=width,
                                            inf=inf,
                                            low_val=start_color,
                                            high_val=end_color)
                           )
        return self.__compose_answer(answers)

    def rev_breathe(self,
                time=30,
                steps=300,
                width=50,
                inf=False,
                low_color_tup=(0,0,0),
                high_color_tup=(1,1,1)):
        answers=[]
        for pwm_driver, start_color, end_color in zip(self.RGB, low_color_tup, high_color_tup):
            self.RGB[pwm_driver].keepOn=True
            answers.append(self.RGB[pwm_driver].rev_breathe(
                                            time=time,
                                            steps=steps,
                                            width=width,
                                            inf=inf,
                                            low_val=start_color,
                                            high_val=end_color)
                           )
        return self.__compose_answer(answers)

    def __compose_answer(self, answers):
        for pwm_driver, answer in zip(self.RGB, answers):
            if answer[:5] != "Start":
                return "Failed ({}):".format(str(self.RGB[pwm_driver])) + answer
            return answer

    def start_circle(self,
                     **kwargs
                     ):
        with self.lock:
            func="circle"
            if self.operating is None:
                operation = RGBDriverOperation(self, func, kwargs)
                operation.start()
                return "Started: "+func
            return "Did not start \"{}\", because another operation is still running!".format(func)
        
    
    def circle(self,#
                     circle_time=30.0,
                     countdown_time=10,
                     pause_time=25,
                     fade_time=2.0,
                     sound=True,
                     fps=60,
                     bpc=4,
                     bpp=5,
                     start_green=(0.1,0.7,0),
                     end_green=(0.15,1,0),
                     start_red=(0.3,0,0),
                     end_red=(1,0.05,0),
                     init_color=(0,0,0),
                     yellow=(1,0.4,0.0),
                     gong_delay=0.25,
                     ):
        if sound:
            pygame.mixer.music.play()
            time.sleep(gong_delay)
            circle_time-=gong_delay
        self.fade_in(fade_time,fade_time*fps,init_color,start_green, func="sine") #inv_cos (0.45)
        self.join_RGB()
        if self.operating is None:
            return
        if self.operating.stopped():
            return
        self.breathe(circle_time-fade_time,(circle_time-fade_time)*fps,(circle_time-fade_time)*fps/bpc,False,start_green,end_green)
        self.join_RGB()
        if self.operating is None:
            return
        if self.operating.stopped():
            return
        self.rev_breathe(fade_time,fade_time*fps,fade_time*fps,False,(0,0,0),start_green)
        self.join_RGB()
        if self.operating is None:
            return
        if self.operating.stopped():
            return
        self.breathe(circle_time-fade_time-countdown_time,(circle_time-fade_time-countdown_time)*fps,(circle_time-fade_time-countdown_time)*fps/bpc,False,start_green,end_green)
        self.join_RGB()
        if self.operating is None:
            return
        if self.operating.stopped():
            return
        self.fade_out(fade_time,fade_time*fps,start_green,(0,0,0))
        self.join_RGB()
        if self.operating is None:
            return
        if self.operating.stopped():
            return
        self.breathe(countdown_time-fade_time,(countdown_time-fade_time)*fps,fps,False,(0.0,0.0,0.0),yellow)
        self.join_RGB()
        if self.operating is None:
            return
        if self.operating.stopped():
            return
        if sound:
            pygame.mixer.music.play()
            time.sleep(gong_delay)
            pause_time-=gong_delay
        self.fade_in(fade_time,fade_time*fps,(0,0,0),start_red, func="sine")
        self.join_RGB()
        if self.operating is None:
            return
        if self.operating.stopped():
            return
        self.breathe(pause_time-fade_time,(pause_time-fade_time)*fps,(pause_time-fade_time)*fps/bpp,False,start_red,end_red)
        self.join_RGB()
        if self.operating is None:
            return
        if self.operating.stopped():
            return
        return end_red
        #pygame.mixer.music.play()