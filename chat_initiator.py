import socket
import json
import time
import os

from cryptography.fernet import Fernet
import diffiehellman
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
    public_key1 = input("Please input a number: ")
    ip_address = get_ip_address(username)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        try:
            sock.connect((ip_address, 6001))
        except ConnectionRefusedError:
            print("Connection refused. Please try again.")
            chat()
        print("Key sent to peer.")

        def generate_shared_key(dh, other_public_key):
            shared_key = dh.gen_shared_key(other_public_key)
            return shared_key

        def encrypt_message(message, shared_key):
            cipher_suite = Fernet(shared_key)
            cipher_text = cipher_suite.encrypt(message.encode())
            return cipher_text.decode()

        # Create a DiffieHellman object
        dh = diffiehellman.DiffieHellman()
        # Send the public key to the other user
        sock.send(json.dumps({"key": public_key1}).encode())

        # Receive the other user's public key
        public_key2 = int(sock.recv(1024).decode())

        # Generate the shared secret key
        shared_key = generate_shared_key(dh, public_key2)

        # Get a message from the user
        message = input("Enter your message: ")

        # Encrypt the message with the shared key
        encrypted_message = encrypt_message(message, shared_key)

        # Send the encrypted message to the other user
        sock.send(json.dumps({"encrypted message": encrypted_message}).encode())

        sock.close()
        action()#End the TCP connection

def unsercure_chat(receiver_username):
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
    }
    with open("log.json", "r+") as file:
        # Read the existing JSON data
        json_data = json.load(file) # Load the existing JSON data
        json_data["chat_log"].append(message_data)  # Add the new message to the chat log
        json.dump(json_data, file, indent=4)  # indent for readability


def history():
    announce = ServiceAnnouncer()
    username = announce.receive_broadcasts()     #TODO DENE BURAYI DÜZENLE
    print("Viewing chat history...")
    with open("log.json", "r") as file:
        chat_log = json.load(file)
        for log in chat_log["chat_log"]:
            if log["sender"] == username or log["receiver"] == username:
                print(f"{log['sender']} -> {log['receiver']}: {log['message']} at {log['timestamp']}")

if __name__ == "__main__":
    action()