from datetime import datetime
import time

def wait_until(end_datetime):
    while True:
        diff = (end_datetime - datetime.now()).total_seconds()
        if diff < 0:
            return False      # In case end_datetime was in past to begin with
        time.sleep(diff/2)
        print(diff)
        if diff <= 0.1:
            return True
        
if __name__ == '__main__':
    day=int(input("day?"))
    hour=int(input("hour?"))
    minute=int(input("minute?"))
    wake_time=datetime.today()
    wake_time=wake_time.replace(day=day,hour=hour,minute=minute)
    print(wake_time)
    if wait_until(wake_time):
        import socket

        HOST ='127.0.0.1'
        PORT = 65001

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            send_str="wake_up_lamp.switch.True".encode('utf-8')
            s.sendall(send_str)
            data = s.recv(1024)
    
    