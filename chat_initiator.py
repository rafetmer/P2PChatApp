import socket
import json
import time
import os

from diffiehellman import DiffieHellman
from cryptography.fernet import Fernet

from service_announcer import ServiceAnnouncer


announcer = ServiceAnnouncer()


def action():
    select = input("Simply type 'Users', 'Chat', or 'History' to proceed.\n").lower()
    if select == 'users' or select == 'user':
        users()
    elif select == 'chat':
        chat()
    elif select == 'history':
        history()
    else:
        print("Invalid input. Please try again.")
        action()


def users():
    print("Viewing online users...")
    user_list = {}  # Dictionary to store user IP addresses
    if os.path.exists('neighbor_list.txt'):
        with open('neighbor_list.txt', 'r') as file:
            for line in file:
                if line.strip():                        # check if line is not empty
                    neighbor = json.loads(line.strip())
                    for ip, info in neighbor.items():
                        status = 'Online' if time.time() - info['last_seen'] <= 10 else 'Away'
                        print(f"{info['username']} ({status})")
                        user_list[info['username']] = [ip]
        print(user_list)
        action()
    else:
        print("No users found.")
        action()


def chat():
    print("Initiating chat...")
    user_to_chat_with = input("Enter the username of the user you want to chat with: ")
    secure_or_not = input("Would you like to chat securely? (yes/no): ").lower()
    if secure_or_not == 'yes':
        print("Chatting securely...")
        secure_chat(user_to_chat_with)
    else:
        print("Chatting with no security...")
        # unsecure_chat()

def secure_chat(user_to_chat_with):
    number = input("Please input a number: ")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("localhost", 12345))
    server_socket.listen(1)
    print("Waiting for connection...")
    connection, addr = server_socket.accept()
    print("Connected to", addr)

    key_exchange = DiffieHellman()
    public_key = key_exchange.gen_public_key()
    connection.send(str(public_key).encode())
    other_public_key = int(connection.recv(1024).decode())
    shared_key = generate_shared_key(key_exchange, other_public_key)
    connection.send(json.dumps({"key": number}).encode())

    # Receiving another number from the specified user
    other_number = connection.recv(1024).decode()
    shared_key = generate_shared_key(key_exchange, int(other_number))

def history():
    print("Viewing chat history...")
    # Add your chat history functionality here

if __name__ == "__main__":
    action()