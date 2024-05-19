import socket
import json
import time
import os
import pyDes
import random
import threading
import base64


class ChatApplication:
    def __init__(self):
        self.user_list = {}
        self.username = None
        self.user_to_chat_with = None

    def start(self):
        self.username = input("Enter your username: ")
        self.action()

    def action(self):
        select = input("Simply type 'Users', 'Chat', or 'History' to proceed.\n").lower()
        if select == 'users' or select == 'user':
            self.users()
        elif select == 'chat':
            self.chat_select()
        elif select == 'history':
            self.history()
        else:
            print("Invalid input. Please try again.")
            self.action()

    def users(self):
        print("Viewing online users...")
        if os.path.exists('neighbor_list.txt'):
            with open('neighbor_list.txt', 'r') as file:
                for line in file:
                    if line.strip():
                        neighbor = json.loads(line.strip())
                        for ip, info in neighbor.items():
                            if self.username != info['username']:
                                status = info['online_status']
                                print(f"{info['username']} ({status})")
                                self.user_list[info['username']] = [ip]
            self.action()
        else:
            print("No users found.")
            self.action()



    def chat_select(self):
        print("Initiating chat...")
        self.user_to_chat_with = input("Enter the username of the user you want to chat with: ").lower()
        secure_or_not = input("Would you like to chat securely? (yes/no): ").lower()
        if secure_or_not == 'yes':
            print("Chatting securely...")
            threading.Thread(target=self.secure_chat).start()
        else:
            print("Chatting with no security...")
            threading.Thread(target=self.unsecure_chat).start()

    def get_ip_address(self, username):
        user_info = self.user_list.get(username)
        return user_info[0] if user_info else None

    def get_my_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('10.255.255.255', 1))
            ip = s.getsockname()[0]
        except Exception:
            ip = '127.0.0.1'
        finally:
            s.close()
        return ip

    def status_updater(self, message, sender, receiver):
        with open("log.json", "r+") as file:
            json_data = json.load(file)
            for message_data in json_data["chat_log"]:
                if message_data["sender"] == sender and message_data["receiver"] == receiver and message_data["message"] == message:
                    message_data["status"] = "SENT"
            file.seek(0)
            json.dump(json_data, file, indent=4)
            file.truncate()

    def secure_chat(self):
        print("Chatting securely...")
        p = 23  # A prime number
        g = 5   # A primitive root modulo p
        a = random.randint(1, p-1)
        initiator_key = (g**a) % p

        ip_address = self.get_ip_address(self.user_to_chat_with)
        if not ip_address:
            print("User not found.")
            self.chat_select()
            return

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
                sock.connect((ip_address, 6001))
                sock.send(json.dumps({"key": initiator_key}).encode())
                print("Public key sent to peer.")
                data = sock.recv(2048)
                if not data:
                    print("No data received.")
                    self.chat_select()
                    return

                responder_key = json.loads(data.decode())["public_key"]
                print(f"Public key received from peer: {responder_key}")

                shared_secret_key_int = (responder_key**a) % p
                shared_secret_key = shared_secret_key_int.to_bytes(8, byteorder='big')

                message = input("Enter your message: ").encode('utf-8')
                iv = bytes(random.getrandbits(8) for _ in range(8))
                des = pyDes.des(shared_secret_key, iv, pad=None, padmode=pyDes.PAD_PKCS5)
                encrypted_message = des.encrypt(message)
                encrypted_message_str = base64.b64encode(encrypted_message).decode('utf-8')
                sock.send(json.dumps({"encrypted_message": encrypted_message_str}).encode())

                self.message_logger(encrypted_message_str, self.username, self.user_to_chat_with)
        except ConnectionRefusedError:
            print("Connection refused. Please try again.")
        except ConnectionError as e:
            print(f"Connection error: {e}")
        finally:
            self.action()

    def unsecure_chat(self):
        print("Chatting with no security...")
        ip_address = self.get_ip_address(self.user_to_chat_with)
        if not ip_address:
            print("Invalid username. Please try again.")
            self.chat_select()
            return

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
                sock.connect((ip_address, 6001))
                unencrypted_message = input("Enter your message: ")
                sock.send(json.dumps({"unencrypted_message": unencrypted_message}).encode())
                self.message_logger(unencrypted_message, self.username, self.user_to_chat_with)
                print("Your message has been delivered.")
        except ConnectionRefusedError:
            print("Connection with the end user cannot be established. Please make sure the server is running and try again.")
        except ConnectionResetError:
            print("Connection reset by peer. Please try again.")
        finally:
            self.action()

    def chat_responder(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            tcp_address = self.get_my_ip()
            if not tcp_address:
                print(f"Invalid IP address for user")
                return

            try:
                sock.bind((tcp_address, 6001))
                while True:
                    sock.listen()
                    print("Waiting for connection...")
                    conn, address = sock.accept()
                    with conn:
                        print(f"Connected to: {address}")
                        data = conn.recv(2048).decode()
                        if not data:
                            continue
                        message = json.loads(data)
                        if "key" in message:
                            self.handle_key_exchange(conn, message)
                        elif "unencrypted_message" in message:
                            print(f"Received message: {message['unencrypted_message']}")
                        else:
                            print("Invalid message received.")
            except OSError as e:
                print(f"Error binding to address {tcp_address}: {e}")

    def handle_key_exchange(self, conn, message):
        p = 23
        g = 5
        b = random.randint(1, p-1)
        responder_key = (g**b) % p
        initiator_key = message["key"]
        shared_secret_key_int = (initiator_key**b) % p
        shared_secret_key = shared_secret_key_int.to_bytes(8, byteorder='big')
        conn.send(json.dumps({"public_key": responder_key}).encode())

        try:
            received_data = conn.recv(2048).decode()
            encrypted_message = json.loads(received_data)["encrypted_message"]
            iv = bytes(random.getrandbits(8) for _ in range(8))
            des = pyDes.des(shared_secret_key, iv, pad=None, padmode=pyDes.PAD_PKCS5)
            decrypted_message = des.decrypt(base64.b64decode(encrypted_message))
            print(f"Decrypted message: {decrypted_message.decode('utf-8')}")
        except Exception as e:
            print(f"Error decrypting message: {e}")

    def message_logger(self, message, sender, receiver):
        message_data = {
            "message": message,
            "timestamp": time.time(),
            "sender": sender,
            "receiver": receiver,
            "status": "in the process"
        }
        if not os.path.exists("log.json"):
            with open("log.json", "w") as file:
                json.dump({"chat_log": []}, file)

        with open("log.json", "r+") as file:
            json_data = json.load(file)
            json_data["chat_log"].append(message_data)
            file.seek(0)
            json.dump(json_data, file, indent=4)

    def history(self):
        print("Viewing chat history...")
        if os.path.exists("log.json"):
            with open("log.json", "r") as file:
                chat_log = json.load(file)
                for log in chat_log["chat_log"]:
                    if log["sender"] == self.username or log["receiver"] == self.username:
                        print(f"{log['sender']} -> {log['receiver']}: {log['message']} at: {log['timestamp']} --> {log['status']}")
        self.action()


if __name__ == "__main__":
    chat_app = ChatApplication()
    chat_app.start()