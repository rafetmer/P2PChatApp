import socket
import json
import time
import os
import pyDes
import random
import threading
import base64

user_list = {}
server_username = None
username = None


def action(user):
    global user_list  
    global server_username
    server_username = user
    select = input("Simply type 'Users', 'Chat', or 'History' to proceed.\n").lower()
    if select == 'users' or select == 'user':
        users(user)
    elif select == 'chat':
        chat_select(user)
    elif select == 'history':
        history(user)
    else:
        # print("Invalid input. Please try again.")
        action(user)


def users(user):
    print("Viewing online users...")
    if os.path.exists('neighbor_list.txt'):
        with open('neighbor_list.txt', 'r') as file:
            for line in file:
                if line.strip():
                    neighbor = json.loads(line.strip())
                    for ip, info in neighbor.items():
                        if user != info['username']:
                            status = 'Online' if time.time() - info['last_seen'] <= 10 else 'Away'
                            print(f"{info['username']} ({status})")
                            user_list[info['username']] = [ip]
        action(user)
    else:
        print("No users found.")
        action(user)


def chat_select(user):
    global user_to_chat_with
    print("Initiating chat...")
    user_to_chat_with = input("Enter the username of the user you want to chat with: ").lower()
    secure_or_not = input("Would you like to chat securely? (yes/no): ").lower()
    if secure_or_not == 'yes':
        print("Chatting securely...")
        secure_thread = threading.Thread(target=secure_chat, args=(user, user_to_chat_with))
        secure_thread.start()

    else:
        print("Chatting with no security...")
        unsecure_thread = threading.Thread(target=unsecure_chat, args=(user, user_to_chat_with))
        unsecure_thread.start()


def get_ip_address(user):
    try:
        user_info = user_list.get(user)
        ip_adress = user_info[0]
        return ip_adress
    except:
        print("User not found.")


def get_my_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


def get_username_from_ip(ip_address):
    if os.path.exists('neighbor_list.txt'):
        with open('neighbor_list.txt', 'r') as file:
            for line in file:
                if line.strip():  # check if line is not empty
                    neighbor = json.loads(line.strip())
                    for ip, info in neighbor.items():
                        if ip_address == ip:
                            return info['username']
    return None  # return None if no username found for the given IP address


def status_updater(message, sender, receiver):
    with open("log.json", "r+") as file:
        json_data = json.load(file)
        for message_data in json_data["chat_log"]:
            if message_data["sender"] == sender and message_data["receiver"] == receiver and message_data["message"] == message:
                message_data["status"] = "SENT"
        file.seek(0)
        json.dump(json_data, file, indent=4)
        file.truncate()


def secure_chat(user, user_to_chat_with):
    # Step 1: Generate a pair of private and public keys for each user
    p = 23  # A prime number
    g = 5   # A primitive root modulo p
    a = random.randint(1, p-1)  # The private key
    initiator_key = (g**a) % p  # The public key of the end-user

    ip_address = get_ip_address(user_to_chat_with)                                     
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        try:
            sock.connect((ip_address, 6001))
        except ConnectionRefusedError:
            print("Connection refused. Please try again.")
            chat_select(username)
        sock.send(json.dumps({"key": initiator_key}).encode())
        print("Public key sent to peer.")
        try:
            data = sock.recv(2048)
            if data:
                responder_key = json.loads(data.decode())["public_key"]
                # print(f"Public key received from peer: {responder_key}")
            else:
                print("No data received.")
            shared_secret_key_int = (responder_key**a) % p
            shared_secret_key = shared_secret_key_int.to_bytes(8, byteorder='big')

        except ConnectionError as e:
            print(f"Connection reset by peer. Please try again. {e}")
            chat_select(username)

        message = input("Enter your message: ").encode('utf-8')
        iv = bytes(random.getrandbits(8) for _ in range(8))
        des = pyDes.des(shared_secret_key, iv, pad=None, padmode=pyDes.PAD_PKCS5)
        encrypted_message = des.encrypt(message)
        # print(encrypted_message)

        encrypted_message_str = base64.b64encode(encrypted_message).decode('utf-8')
        sock.send(json.dumps({"encrypted_message": encrypted_message_str}).encode())
        message_logger(encrypted_message_str, user, user_to_chat_with)
        sock.close()
        action(username)


def unsecure_chat(user, user_to_chat_with):
    ip_address = get_ip_address(user_to_chat_with)
    if ip_address is None:
        print("Invalid username. Please try again.")
        chat_select(user)
    else:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            try:
                sock.connect((ip_address, 6001))
                print("Client has connected.")

            except ConnectionRefusedError:
                print("Connection with the end user cannot be established.")
                chat_select(user)
            unencrypted_message = input("Enter your message: ")
            try:
                sock.send(json.dumps({"unencrypted_message": unencrypted_message}).encode())
            except ConnectionResetError:
                print("Connection reset by peer. Please try again.")
            message_logger(unencrypted_message, user, user_to_chat_with)
            print("Your message has ben delivered.")
            sock.close()
            action(user)


def chat_responder():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        tcp_address = get_my_ip()
        if tcp_address is None:
            print(f"Invalid IP address for user")
        try:
            sock.bind((tcp_address, 6001))
        except OSError as e:
            print(f"Error binding to address {tcp_address}: {e}")
        while True:
            sock.listen()
            data, address = sock.accept()
            initiator_ip = data.getpeername()[0]
            print(initiator_ip)
            initiator_username = get_username_from_ip(initiator_ip)
            try:
                message = json.loads(data.recv(2048).decode())
                if "key" in message:
                    print("The public key received from peer.")
                    initiator_key = message["key"]
                    p = 23  # A prime number
                    g = 5   # A primitive root modulo p
                    b = random.randint(1, p-1)  # The private key
                    responder_key = (g**b) % p  # The public key
                    data.send(json.dumps({"public_key": responder_key}).encode())
                    shared_secret_key_int = (initiator_key**b) % p  # Compute the shared secret key
                    shared_secret_key = shared_secret_key_int.to_bytes(8, byteorder='big')
                    # print(f"Shared secret key: {shared_secret_key}")
                    # Receive and decrypt the encrypted message from the initiator
                    received_data = data.recv(2048).decode()
                    encrypted_message_dict = json.loads(received_data)
                    encrypted_message = encrypted_message_dict["encrypted_message"]
                    print(f"Encrypted message received from {initiator_username}: {encrypted_message}")
                    try:
                        iv = bytes(random.getrandbits(8) for _ in range(8))
                        des = pyDes.des(shared_secret_key, iv, pad=None, padmode=pyDes.PAD_PKCS5)
                        encrypted_message_bytes = base64.b64decode(encrypted_message)
                        decrypted_message = des.decrypt(encrypted_message_bytes)
                        decrypted_message = decrypted_message.decode('utf-8')
                        print(f"Decrypted message received from {initiator_username}: {decrypted_message}")
                        message_logger(decrypted_message, initiator_username, server_username)
                        print("To continue chatting, Please press Enter.")
                    except Exception as e:
                        print(f"Error decrypting message: {e}")

                elif "unencrypted_message" in message:
                    print(f"Received message from {initiator_username}: {message['unencrypted_message']}")
                    message_logger(message['unencrypted_message'], initiator_username, server_username)
                    print("To continue chatting, Please press Enter.")
                else:
                    print("Invalid message received.")
            except ConnectionError as e:
                print(f"Connection error: {e}")
                break
            chat_responder()


def message_logger(message, sender, receiver):
    message_data = {
        "message": message,
        "timestamp": time.time(),
        "sender": sender,
        "receiver": receiver,
        "status": "SENT"
    }

    if not os.path.exists("log.json"):
        with open("log.json", "w") as file:
            json.dump({"chat_log": []}, file, indent=4)

    with open("log.json", "r+") as file:
        try:
            json_data = json.load(file)
        except json.JSONDecodeError:
            json_data = {"chat_log": []}
        json_data["chat_log"].append(message_data)

        file.seek(0)
        json.dump(json_data, file, indent=4)
        file.truncate()


def history(user):
    print("Viewing chat history...")
    with open("log.json", "r") as file:
        chat_log = json.load(file)
        for log in chat_log["chat_log"]:
            if log["sender"] == user or log["receiver"] == user:
                print(f"{log['sender']} -> {log['receiver']}: {log['message']} at: {log['timestamp']} --> {log['status']}")
    action(user)


if __name__ == "__main__":
    username = input("Enter your username: ")
    action(username)

