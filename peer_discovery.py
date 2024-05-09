import socket
import json
import time


# Function to parse JSON message
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


def offline_status(neighbor_list):
    current_time = time.time()
    for ip_address in neighbor_list:
        if current_time - neighbor_list[ip_address]["last_seen"] > 10:
            neighbor_list[ip_address]["online_status"] = "Away"
            print(f"{neighbor_list[ip_address]['username']} is away.")
        else:
            neighbor_list[ip_address]["online_status"] = "Online"
            print(f"{neighbor_list[ip_address]['username']} is online.")
    return neighbor_list


# Function to update or add entry in the dictionary
def update_neighbor_info(ip_address, username, neighbor_list):
    if ip_address in neighbor_list:
        neighbor_list[ip_address]["last_seen"] = time.time()  # Update last seen time
        print(f"{username} is still online./n")
    else:
        neighbor_list[ip_address] = {"username": username, "last_seen": time.time(), "online_status": "Online"}
        print(f"{username} is online!/n")


def receive_broadcasts():
    # Initialize empty dictionary for neighbor information
    neighbor_list = {}

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        sock.bind(("172.20.10.9", 6000))  # Listen on port 6000

        data, address = sock.recvfrom(1024)
        try:
            # Parse JSON data
            peer_info = json.loads(data.decode())
            username = peer_info.get("username")

            # Update or add neighbor information based on IP address
            if address[0] in neighbor_list:
                neighbor_list[address[0]]["username"] = username
            else:
                neighbor_list[address[0]] = {"username": username}

            # Write the neighbor_list dictionary to a local text file
        except json.JSONDecodeError:
            print(f"Received invalid broadcast data: {data}")
        return data, address[0]


def main():
    # Initialize empty dictionary for neighbor information
    neighbor_list = {}

    while True:
        # Receive data from UDP broadcast
        offline_status(neighbor_list)
        data, address = receive_broadcasts()
        username = parse_message(data)
        ip_address = parse_ip(address)
        print(username, ip_address)

        if username and ip_address:
            print(f"Received broadcast from {username} at {ip_address}")
            # Update or add neighbor information based on IP address
            update_neighbor_info(ip_address, username, neighbor_list)
            print(neighbor_list)

            # Check online status based on last_seen (replace 10 with desired timeout)
            current_time = time.time()
            if current_time - neighbor_list[ip_address]["last_seen"] > 10:
                neighbor_list[ip_address]["online_status"] = "Away"
                print(f"{username} is away.")
            else:
                neighbor_list[ip_address]["online_status"] = "Online"

            # Write the neighbor_list dictionary to a local text file
            with open('neighbor_list.txt', 'a') as file:
                file.write(json.dumps(neighbor_list)+"\n")

            # Write the neighbor_list dictionary to a local text file
if __name__ == "__main__":
    main()