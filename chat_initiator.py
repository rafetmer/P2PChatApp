import socket
import json
import time
import os
import pyDes
import random

from cryptography.fernet import Fernet
from service_announcer import ServiceAnnouncer

user_list = {}


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
    global user_list  # Dictionary to store user IP addresses

    print("Viewing online users...")
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
    user_to_chat_with = input("Enter the username of the user you want to chat with: ").lower()
    secure_or_not = input("Would you like to chat securely? (yes/no): ").lower()
    if secure_or_not == 'yes':
        print("Chatting securely...")
        secure_chat(user_to_chat_with)
        # print(user_list)
    else:
        print("Chatting with no security...")
        # unsecure_chat()


def get_ip_address(username):
    try:
        user_info = user_list.get(username)
        ip_adress = user_info[0]
        return ip_adress
    except:
        print("User not found.")


def secure_chat(username):
    print("Chatting securely...")
    # Step 1: Generate a pair of private and public keys for each user
    p = 23  # A prime number
    g = 5   # A primitive root modulo p
    a = random.randint(1, p-1)  # The private key
    initiator_key = (g**a) % p  # The public key of the end-user

    ip_address = get_ip_address(username)                                      #TODO
    print(ip_address)                                                          #TODO
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:            #TODO
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)             #TODO
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)             #TODO
        try:                                                                   #TODO
            sock.connect((f"{ip_address}", 6001))                              #TODO
        except ConnectionRefusedError:                                         #TODO
            print("Connection refused. Please try again.")                     #TODO
            chat()
        sock.send(json.dumps({"key": initiator_key}).encode())   # Step 2: Send the public key to the other user
        print("Public key sent to peer.")
        time.sleep(1)
        data = sock.recv(1024)  # Step 3: Receive the other user's public key and compute the shared secret key
        responder_key = json.loads(data.decode())["public_key"]
        shared_secret_key = (responder_key**a) % p

        message = input("Enter your message: ")      # Step 4: Use the shared secret key to encrypt a message
        des = pyDes.des(shared_secret_key, pyDes.CBC, "\0\0\0\0\0\0\0\0", pad=None, padmode=pyDes.PAD_PKCS5)
        encrypted_message = des.encrypt(message)

        # Send the encrypted message to the other user
        sock.send(json.dumps({"encrypted_message": encrypted_message}).encode())
        message_logger(encrypted_message, "You", username)
        sock.close()
        action()  # End the TCP connection


def unsecure_chat(receiver_username):
    print("Chatting with no security...")
    # Add your unsecure chat functionality here
    ip_address = get_ip_address(receiver_username)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        try:
            sock.connect((ip_address, 6001))
        except ConnectionRefusedError:
            print("Connection with the end user cannot be established. Please try again.")
            chat()
        unencrypted_message = input("Enter your message: ")
        sock.send(json.dumps({"unencrypted message": unencrypted_message}).encode())
        message_logger(unencrypted_message, "You", receiver_username)
        sock.close()
        action()#End the TCP  connection


def message_logger(message, sender, receiver):
    message_data = {
        "message": message,
        "timestamp": time.time(),
        "sender": sender,
        "receiver": receiver,
        "status": "in the process"
    }
    with open("log.json", "r+") as file:
        # Read the existing JSON data
        json_data = json.load(file) # Load the existing JSON data
        json_data["chat_log"].append(message_data)  # Add the new message to the chat log
        file.seek(0)
        json.dump(json_data, file, indent=4)  # indent for readability


def history():
    announce = ServiceAnnouncer()
    username = "yusuf"    #TODO DENE BURAYI DÜZENLE
    print("Viewing chat history...")
    with open("log.json", "r") as file:
        chat_log = json.load(file)
        for log in chat_log["chat_log"]:
            if log["sender"] == username or log["receiver"] == username:
                print(f"{log['sender']} -> {log['receiver']}: {log['message']} at: {log['timestamp']} --> {log['status']}")

if __name__ == "__main__":
    action()