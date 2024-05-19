import socket
import json
import time


def parse_message(message):
    try:
        data = json.loads(message.decode())
        return data.get("username")
    except json.JSONDecodeError:
        print("Error parsing JSON message")
        return None


def parse_ip(ip_address):
    try:
        ip_dict = {"ip_address": ip_address}
        data = ip_dict
        return data.get("ip_address")
    except json.JSONDecodeError:
        print("Error parsing JSON message")
        return None


def update_status_and_info(ip_address, username, neighbor_list):
    if ip_address in neighbor_list:
        neighbor_list[ip_address]["last_seen"] = time.time()
        with open('neighbor_list.txt', 'a') as file:
            file.write(json.dumps(neighbor_list) + "\n")
    else:
        neighbor_list[ip_address] = {"username": username, "last_seen": time.time(), "online_status": "Online"}
        # print(f"{username} is online")

    current_time = time.time()
    for ip in neighbor_list:
        if current_time - neighbor_list[ip]["last_seen"] > 10:
            neighbor_list[ip]["online_status"] = "Away"
        else:
            neighbor_list[ip]["online_status"] = "Online"

    with open("neighbor_list.txt", "w") as file:
        file.write(json.dumps(neighbor_list) + "\n")
    return neighbor_list


class PeerDiscovery:

    def __init__(self):
        self.broadcast_address = "192.168.1.255"

    def get_broadcast_address(self):
        ip_address = socket.gethostbyname(socket.gethostname())
        ip_octets = ip_address.split(".")
        ip_octets[-1] = '255'
        self.broadcast_address = ".".join(ip_octets)
        return self.broadcast_address

    def receive_broadcasts(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            sock.bind((self.broadcast_address, 6000))
            data, address = sock.recvfrom(1024)
            return data, address[0]

    def main(self):
        neighbor_list = {}
        open('neighbor_list.txt', 'w').close()  # Clear the neighbor_list.txt file

        while True:
            data, address = self.receive_broadcasts()
            username = parse_message(data)
            ip_address = parse_ip(address)

            if username and ip_address:
                neighbor_list = update_status_and_info(ip_address, username, neighbor_list)
            else:
                print("Invalid data received")


if __name__ == "__main__":
    discoverer = PeerDiscovery()
    discoverer.main()
