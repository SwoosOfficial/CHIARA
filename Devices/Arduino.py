import serial
import threading


class StoppableThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self, arduino):
        super(StoppableThread, self).__init__()
        
        self._stop_event = threading.Event()
        
        self.arduino=arduino
    
    def run(self):
        while not self.stopped():
            self.arduino.read_responses()
    
    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()


class Arduino():
    
    __instance = None
    
    def __new__(
        cls,
        serialObj=serial.Serial('/dev/ttyACM0', 9600),
        outputFile='logs/arduino.log'
    ):
        if Arduino.__instance is None:
            Arduino.__instance = object.__new__(cls)
            Arduino.__instance.s = serialObj
            Arduino.__instance.outputFile = outputFile
            Arduino.__instance.thread=StoppableThread(Arduino.__instance)
            Arduino.__instance.__connected = False
            Arduino.__instance.lock = threading.RLock()
            Arduino.__instance.wait_for_answer = threading.Lock()
            Arduino.__instance.__response_available = False
            Arduino.__instance.response_notifier = threading.Condition()
        return Arduino.__instance
    
    def start_comm(self):
        with self.lock:
            try:
                self.s.close()
            except:
                pass
            self.s.open()
            self.__connected=True
            self.wait_for_answer.acquire()
            self.thread.start()
    
    def stop_comm(self):
        with self.lock:
            self.write('0',0,'0')
            self.thread.stop()
            self.thread.join()
            self.__connected=False
            self.s.close()
    
    def ensure_comm(self):
        with self.lock:
            if not self.__connected:
                self.start_comm()
    #@property
    def response_available(self):
        return self.__response_available
    
    
    def write(self, Device, DeviceNumber, command):
        with self.lock:
            commstring=Device+str(DeviceNumber)+command+';'
            self.s.write(commstring.encode())
            self.wait_for_answer.release()       
    
    def write_n_read(self, Device, DeviceNumber, command):
        with self.lock:
            self.__response_available = False
            with self.response_notifier:
                self.write(Device, DeviceNumber, command)
                self.response_notifier.wait_for(self.response_available)
            return self.response
    
    def read_responses(self):
        self.wait_for_answer.acquire()
        with self.response_notifier:
            try:
                self.response = self.s.readline().decode('utf-8')
                self.response += self.s.readline().decode('utf-8')[:-3]
                self.__response_available = True
                self.response_notifier.notify()
                with open(self.outputFile, 'a') as file:
                    file.write(self.response.decode('UTF-8'))    
            except:
                pass
    
            
        