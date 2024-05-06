import socket
import json
import time


class ServiceAnnouncer:
    def __init__(self):
        self.username = None
        self.broadcast_ip = None  # Consider using get_broadcast_address()

    def get_username(self):
        self.username = input("Please enter your username: ")
        return self.username

    def send_broadcast(self):
        while True:
            data = json.dumps({"username": self.username})
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                sock.sendto(data.encode(), (self.broadcast_ip, 6000))
            time.sleep(8)

    def main(self):
        self.username = self.get_username()
        print(f"Welcome, {self.username}!")
        self.broadcast_ip = "127.0.0.1"  # Prompt for broadcast IP
        self.send_broadcast()
        print("Broadcasting your presence...")  # Informative message

    def receive_broadcasts(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.bind(("0.0.0.0", 6000))  # Listen on port 6000
            while True:
                data, address = sock.recvfrom(1024)
                try:
                    # Parse JSON data
                    self.peer_info = json.loads(data.decode())
                    self.username = self.peer_info.get("username")
                    print(self.peer_info)
                except json.JSONDecodeError:
                    print(f"Received invalid broadcast data: {data}")


if __name__ == "__main__":
    announcer = ServiceAnnouncer()
    announcer.main()