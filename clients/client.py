import socket
import readline

HOST ='127.0.0.1'
PORT = 65002

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    while True:
        send_str=input("Command:").encode('utf-8')
        if send_str == b'exit':
            break
        s.sendall(send_str)
        data = s.recv(1024)
        print('Received:\r\n'+data.decode('utf-8'))
        if data == b'Shutting down Server!' or data == b'Disconnected.':
            break
        
