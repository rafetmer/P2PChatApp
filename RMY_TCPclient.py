import socket

port = 12345
localhost = '127.0.0.1'

socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.connect((localhost, port))
socket.send('hello world'.encode('utf-8'))

print(socket.recv(1024))