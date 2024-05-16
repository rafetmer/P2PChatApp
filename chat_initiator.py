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


def action(username):
    select = input("Simply type 'Users', 'Chat', or 'History' to proceed.\n").lower()
    if select == 'users' or select == 'user':
        users(username)
    elif select == 'chat':
        chat_select(username)
    elif select == 'history':
        history(username)
    else:
        print("Invalid input. Please try again.")
        action(username)


def users(username):
    global user_list  # Dictionary to store user IP addresses
    global server_username
    server_username = username
    print("Viewing online users...")
    if os.path.exists('neighbor_list.txt'):
        with open('neighbor_list.txt', 'r') as file:
            for line in file:
                if line.strip():                        # check if line is not empty
                    neighbor = json.loads(line.strip())
                    for ip, info in neighbor.items():
                        if username != info['username']:
                            status = 'Online' if time.time() - info['last_seen'] <= 10 else 'Away'
                            print(f"{info['username']} ({status})")
                            user_list[info['username']] = [ip]
        #print(user_list)
        action(username)
    else:
        print("No users found.")
        action(username)


def chat_select(username):
    global user_to_chat_with
    print("Initiating chat...")
    user_to_chat_with = input("Enter the username of the user you want to chat with: ").lower()
    secure_or_not = input("Would you like to chat securely? (yes/no): ").lower()
    if secure_or_not == 'yes':
        print("Chatting securely...")
        secure_thread = threading.Thread(target=secure_chat, args=(username, user_to_chat_with))
        secure_thread.start()

    else:
        print("Chatting with no security...")
        unsecure_thread = threading.Thread(target=unsecure_chat, args=(username, user_to_chat_with))
        unsecure_thread.start()




def get_ip_address(username):
    try:
        user_info = user_list.get(username)
        ip_adress = user_info[0]
        return ip_adress
    except:
        print("User not found.")

def get_my_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP




def status_updater(message, sender, receiver):
    with open("log.json", "r+") as file:
        json_data = json.load(file)    # Load the existing JSON data
        for message_data in json_data["chat_log"]:
            if message_data["sender"] == sender and message_data["receiver"] == receiver and message_data["message"] == message:
                message_data["status"] = "SENT"  # Update the status to "SENT"
        file.seek(0)  # Move the file pointer to the beginning of the file
        json.dump(json_data, file, indent=4)  # Write the updated data back to the file
        file.truncate()  # Remove any remaining old data


def secure_chat(username, user_to_chat_with):
    print("Chatting securely...")
    # Step 1: Generate a pair of private and public keys for each user
    p = 23  # A prime number
    g = 5   # A primitive root modulo p
    a = random.randint(1, p-1)  # The private key
    initiator_key = (g**a) % p  # The public key of the end-user

    ip_address = get_ip_address(user_to_chat_with)                                     
    print(ip_address)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        try:
            sock.connect((ip_address, 6001))
        except ConnectionRefusedError:
            print("Connection refused. Please try again.")
            chat_select(username)
        sock.send(json.dumps({"key": initiator_key}).encode())   # Step 2: Send the public key to the other user
        print("Public key sent to peer.")
        try:
            print("TRYİNG TO RECEIVE.")
            data = sock.recv(2048)
            print(data)
            if data:
                responder_key = json.loads(data.decode())["public_key"]
                print(f"Public key received from peer: {responder_key}") #7
            else:
                print("No data received.")
            shared_secret_key_int = (responder_key**a) % p
            shared_secret_key = shared_secret_key_int.to_bytes(8, byteorder='big')  # Convert integer to 8-byte byte string (big-endian)

        except ConnectionError as e:
            print(f"Connection reset by peer. Please try again. {e}")
            chat_select(username)

        message = input("Enter your message: ").encode('utf-8')
        iv = bytes(random.getrandbits(8) for _ in range(8))
        des = pyDes.des(shared_secret_key, iv, pad=None, padmode=pyDes.PAD_PKCS5)
        encrypted_message = des.encrypt(message)
        print(encrypted_message)

        encrypted_message_str = base64.b64encode(encrypted_message).decode('utf-8')  # Convert bytes to base64 encoded string# Convert bytes to string
        sock.send(json.dumps({"encrypted_message": encrypted_message_str}).encode())
        encrypted_message_str = base64.b64encode(encrypted_message).decode('utf-8')  # Convert bytes to base64 encoded string
        message_logger(encrypted_message_str, username, user_to_chat_with)
        sock.close()
        action(username)  # End the TCP connection


def unsecure_chat(username, user_to_chat_with):
    print("Chatting with no security...")
    ip_address = get_ip_address(user_to_chat_with)
    if ip_address is None:
        print("Invalid username. Please try again.")
        chat_select(username)
    else:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            try:
                print("TRYİNG TO CONNECT.")
                sock.connect((ip_address, 6001))
                print("Client has connected .")

            except ConnectionRefusedError:
                print("Connection with the end user cannot be established. Please make sure the server is running and try again.")
                chat_select(username)
            unencrypted_message = input("Enter your message: ")
            try:
                sock.send(json.dumps({"unencrypted_message": unencrypted_message}).encode())
            except ConnectionResetError:
                print("Connection reset by peer. Please try again.")
                chat_select(username)
            message_logger(unencrypted_message, username, user_to_chat_with)
            print("Your message has ben delivered.")
            time.sleep(5) # Wait for the response message
            sock.close()
            action(username)  # End the TCP connection

def chat_responder():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        tcp_address = get_my_ip()
        print(get_my_ip())

        print(f"Server IP address: {tcp_address}")
        if tcp_address is None:
            print(f"Invalid IP address for user")
        try:
            sock.bind(('192.168.1.49', 6001))
            # print("Socket is being bound.")
        except OSError as e:
            print(f"Error binding to address {tcp_address}: {e}")

        # print("Server is now listening for connections.")
        while True:
            sock.listen()
            print("Waiting for connection...")
            data, address = sock.accept()
            print(f"Connected to: {address}")

            try:
                message = json.loads(data.recv(2048).decode())
                #print(message)

                if "key" in message:  # Initiator's public key is received
                    print("The public key received from peer.")
                    initiator_key = message["key"]

                    # Generate a pair of private and public keys for the responder
                    p = 23  # A prime number
                    g = 5   # A primitive root modulo p
                    b = random.randint(1, p-1)  # The private key
                    responder_key = (g**b) % p  # The public key

                    try:
                        data.send(json.dumps({"public_key": responder_key}).encode())
                    except:
                        print("Error sending public key to initiator.")

                    shared_secret_key_int = (initiator_key**b) % p  # Compute the shared secret key
                    shared_secret_key = shared_secret_key_int.to_bytes(8, byteorder='big')  # Convert integer to 8-byte byte string (big-endian)
                    print(f"Shared secret key: {shared_secret_key}")
                    # Receive and decrypt the encrypted message from the initiator
                    received_data = data.recv(2048).decode()
                    print(received_data)
                    encrypted_message_dict = json.loads(received_data)
                    encrypted_message = encrypted_message_dict["encrypted_message"]
                    print(f"Encrypted message received: {encrypted_message}")
                    try:
                        iv = bytes(random.getrandbits(8) for _ in range(8))
                        des = pyDes.des(shared_secret_key, iv, pad=None, padmode=pyDes.PAD_PKCS5)
                        encrypted_message_bytes = base64.b64decode(encrypted_message)  # Convert base64 encoded string back to bytes
                        decrypted_message = des.decrypt(encrypted_message_bytes)
                        print(f"Decrypted message: {decrypted_message}")
                        break
                    except Exception as e:
                        print(f"Error decrypting message: {e}")

                elif "unencrypted_message" in message:
                    print(f"Received message: {message['unencrypted_message']}")

                    # Implement logic to handle unencrypted messages (e.g., send response)

                else:
                    print("Invalid message received.")

            except ConnectionError as e:
                print(f"Connection error: {e}")
                break  # Exit the inner loop on connection error
        action(server_username)  # End the TCP connection


def message_logger(message, sender, receiver):
    message_data = {
        "message": message,
        "timestamp": time.time(),
        "sender": sender,
        "receiver": receiver,
        "status": "in the process"
    }
    with open("log.json", "r+") as file:
        try:
            json_data = json.load(file)  # Try to load the existing JSON data
        except json.JSONDecodeError:
            json_data = {"chat_log": []}  # Load the existing JSON data
        json_data["chat_log"].append(message_data)  # Add the new message to the chat log
        file.seek(0)
        json.dump(json_data, file, indent=4)  # indent for readability


def history(username):
    print("Viewing chat history...")
    with open("log.json", "r") as file:
        chat_log = json.load(file)
        for log in chat_log["chat_log"]:
            if log["sender"] == username or log["receiver"] == username:
                print(f"{log['sender']} -> {log['receiver']}: {log['message']} at: {log['timestamp']} --> {log['status']}")


if __name__ == "__main__":
    username = input("Enter your username: ")
    action(username)