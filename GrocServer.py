import threading
import socket

class GrocServerThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self, connected_devices, process_request, HOST, PORT):
        super(GrocServerThread, self).__init__()
        
        self._stop_event = threading.Event()
        self.__connected_devices = connected_devices
        self.__process_request = process_request
        self.__HOST = HOST
        self.__PORT = PORT
    
    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.__HOST, self.__PORT))
            s.listen()
            while not self.stopped():
            
                conn, addr = s.accept()
                
                with conn:
                        #print('Connected by', addr)
                    try:
                        while not self.stopped():
                            answer=self.__process_request(self, conn.recv(1024))
                            if answer.decode('utf-8') == 'Shutting down Server!':
                                self.stop()
                            conn.sendall(answer)
                    except:
                        pass
    
    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()
    
    @property
    def connected_devices(self):
        return self.__connected_devices