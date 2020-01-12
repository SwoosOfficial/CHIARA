import socketserver
import time
import threading
import traceback
import Devices.PWM as PWM
import Devices.PWM_Driver as PWM_Driver
import Devices.RGB_Driver as RGB_Driver


class DeviceHandler(socketserver.BaseRequestHandler):

    def __process_request(self, request):
        try:
            request_str = request.decode('utf-8')
            if request_str == 'shutdown':
                return 'Shutting down Server!'.encode('utf-8')
        except:
            return 'Could not decode!'.encode('utf-8')
        try:
            request_list = request_str.split('.')
            device_key = request_list[0]
            instruction = request_list[1]
        except:
            return 'Wrong Command format!'.encode('utf-8')
        try:
            device = connected_devices[device_key]
        except:
            return 'Unknown Device!'.encode('utf-8')
        try:
            function = getattr(device, instruction)
        except:
            return 'Invalid Instruction!'.encode('utf-8')
        try:
            if request_list[2:] != []:
                function_answer = function(*request_list[2:])
            else:
                function_answer = function()
        except Exception as E:
            traceback.print_tb(E.__traceback__)
            print(E)
            return 'Error: {}!'.format(E).encode('utf-8')   
        if function_answer is None:
            answer = 'Success!'
        else:
            answer = str(function_answer)
        return answer.encode('utf-8')

    def handle(self):
        # self.request is the TCP socket connected to the client
        with self.request as socket:
            addr=socket.getpeername()
            print("Opened Connection with {}".format(addr))
            while True:
                req=socket.recv(1024)
                if not req:
                    break
                answer=self.__process_request(req)
                try:
                    socket.sendall(answer)
                except:
                    pass
                if answer.decode('utf-8') == 'Disconnected.':
                    break
                if answer.decode('utf-8') == 'Shutting down Server!':
                    shutdown()
                    break
            print("Closed Connection with {}".format(addr))
            

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

def shutdown():
    kill_thread=threading.Thread(target=server.shutdown)
    kill_thread.start()
    kill_thread.join()
    for device in connected_devices:
        connected_devices[device].release()
    #server.shutdown()
    server.server_close()
    print("Server shutting down...")

if __name__ == "__main__":

    connected_devices={
        "red_light_pwm" : PWM.PWM(),
        "green_light_pwm" : PWM.PWM(pwm_number=23),
        "blue_light_pwm" : PWM.PWM(pwm_number=27),
    }
    connected_devices.update({
        "red_light_driver":PWM_Driver.PWM_Driver(connected_devices["red_light_pwm"],
                                                  relais=None),
        "green_light_driver":PWM_Driver.PWM_Driver(connected_devices["green_light_pwm"],
                                                  relais=None),
        "blue_light_driver":PWM_Driver.PWM_Driver(connected_devices["blue_light_pwm"],
                                                  relais=None),
                              })
    connected_devices.update({
        "rgb_driver":RGB_Driver.RGB_Driver(connected_devices["red_light_driver"],
                                           connected_devices["green_light_driver"],
                                           connected_devices["blue_light_driver"],
                                           ),
                              })
    #init devs
    for device in connected_devices:
        connected_devices[device].initialise()

    HOST, PORT = "localhost", 65002

    server = ThreadedTCPServer((HOST, PORT), DeviceHandler)
    server_thread = threading.Thread(target=server.serve_forever)
    #server_thread.daemon = True
    server_thread.start()
    #server_thread.join()
    

