import socket
import readline
import sys

HOST ='127.0.0.1'
PORT = 65002


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    if sys.argv[1] == "-i":
        while True:
            send_str=input("Command:").encode('utf-8')
            if send_str == b'exit':
                break
            s.sendall(send_str)
            data = s.recv(1024)
            print('Received:\r\n'+data.decode('utf-8'))
            if data == b'Shutting down Server!' or data == b'Disconnected.':
                break
    else:
        s.sendall(sys.argv[1].encode('utf-8'))
        data = s.recv(1024)
        print('Received:\r\n'+data.decode('utf-8'))
        
