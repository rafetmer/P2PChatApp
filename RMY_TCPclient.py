import socket

port = 18932
ip_address = '0.0.0.0'
is_continue = 1

socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.connect((ip_address, port))

while is_continue:
    message = input("Write your message\n")
    socket.send(message.encode('utf-8'))
    print(socket.recv(1024))
    # is_continue = input("Do you wanna continue:\n 'Yes' Type '1'\n 'No' Type '0'")