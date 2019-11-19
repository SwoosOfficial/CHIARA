import Motor
import Relais
import TempHygroSensor
import WaterSensor
import Arduino
#import threading
import GrocServer
import time

def __process_request(grocServerThread, request):
    try:
        request_str = request.decode('utf-8')
        if request_str == 'shutdown':
            return 'Shutting down Server!'.encode('utf-8')
        if request_str == 'disconnect':
            return 'Disconnected.'.encode('utf-8')
    except:
        return 'Could not decode!'.encode('utf-8')
    try:
        request_list = request_str.split('.')
        device_key = request_list[0]
        instruction = request_list[1]
    except:
        return 'Wrong Command format!'.encode('utf-8')
    try:
        device = grocServerThread.connected_devices[device_key]
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
    except:
        return 'Invalid Arguments!'.encode('utf-8')   
    if function_answer is None:
        answer = 'Success!'
    else:
        answer = str(function_answer)
    return answer.encode('utf-8')

def wake(timeZ,state):
    time.sleep(timeZ)
    connected_devices["wake_up_lamp"].switch(state)

def __main():
    server = True
    global connected_devices
    #create oTruzzbjects for devs
    connected_devices={
        "lid_motor" : Motor.Motor(0),
        "vent" : Relais.Relais(relais_number=4),
        "wake_up_lamp" : Relais.Relais(relais_number=3),
        "blue_lamp" : Relais.Relais(),
        "red_lamp" : Relais.Relais(relais_number=2),
        "tempHygro" : TempHygroSensor.TempHygroSensor(),
        "water_sens" : WaterSensor.WaterSensor()
    }
    arduino = Arduino.Arduino()
    #init devs
    for device in connected_devices:
        connected_devices[device].initialise()
    if server:
        #start thread
        grocServerThread = GrocServer.GrocServerThread(connected_devices, __process_request, '127.0.0.1', 65001)
        grocServerThread.start()
        grocServerThread.join()
        arduino.stop_comm()

if __name__ == '__main__':
    __main()