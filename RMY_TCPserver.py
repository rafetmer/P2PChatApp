import socket

port = 18932

ip_address = '0.0.0.0'

serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.bind((ip_address, port))
serverSocket.listen(5)

print('server is ready to receive')

while 1:
    connectionSocket, addr = serverSocket.accept()
    print(f"connected to {addr}")
    message = connectionSocket.recv(1024).decode('utf-8')
    print(f"message from client is: \n{message}")
    connectionSocket.send("Got your message".encode('utf-8'))

connectionSocket.close()
print("connection with address ended.")




























