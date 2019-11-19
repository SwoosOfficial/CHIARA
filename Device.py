from abc import ABC, abstractmethod
import threading

class Device(ABC):
    
    def __init__(self):
        self.lock = threading.Lock()
    
    @abstractmethod
    def initialise(self):
        pass
    
    @abstractmethod
    def release(self):
        pass

    