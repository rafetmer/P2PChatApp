import socket
import json
import time


class ServiceAnnouncer:
    def __init__(self):
        self.peer_info = None
        self.username = None
        self.broadcast_ip = "192.168.1.255"
        self.address = None

    def get_broadcast_address(self):
        ip_address = socket.gethostbyname(socket.gethostname())
        ip_octets = ip_address.split(".")
        ip_octets[-1] = '255'
        self.broadcast_ip = ".".join(ip_octets)
        print(self.broadcast_ip)
        return self.broadcast_ip

    def get_username(self):
        self.username = input("Please enter your username: ")
        return self.username

    def send_broadcast(self):
        while True:
            data = json.dumps({"username": self.username})
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
                sock.sendto(data.encode(), (self.broadcast_ip, 6000))
            time.sleep(8)

    def main(self):
        self.username = self.get_username()
        print(f"Welcome, {self.username}!")
        self.send_broadcast()

    def receive_broadcasts(self):
        while True:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.bind((self.broadcast_ip, 6000))

                data, self.address = sock.recvfrom(1024)
                try:
                    self.peer_info = json.loads(data.decode())
                    self.username = self.peer_info.get("username")
                    # print({"username": self.username})
                except json.JSONDecodeError:
                    print(f"Received invalid broadcast data: {data}")


if __name__ == "__main__":
    announcer = ServiceAnnouncer()
    announcer.main()
