import socket
import json
import time

# Function to parse JSON message
def parse_message(message):
    try:
        data = json.loads(message.decode())
        return data.get("username"), data.get("ip_address")
    except json.JSONDecodeError:
        print("Error parsing JSON message")
        return None, None

# Function to update or add entry in the dictionary
def update_neighbor_info(ip_address, username, neighbor_list):
    if ip_address in neighbor_list:
        neighbor_list[ip_address]["last_seen"] = time.time()  # Update last seen time
        print(f"{username} is still online.")
    else:
        neighbor_list[ip_address] = {"username": username, "last_seen": time.time(), "online_status": "Online"}
        print(f"{username} is online!")

def main():
    # Define UDP socket and listen on port 6000, using network interface address
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", 6000))

    # Initialize empty dictionary for neighbor information
    neighbor_list = {}  

    while True:
        # Receive data from UDP broadcast
        data, address = sock.recvfrom(1024) # Buffer size for receiving message
        print(data)

        # Parse the received message
        username, ip_address = parse_message(data)
        print(username)

        if username and ip_address:
            # Update or add neighbor information based on IP address
            update_neighbor_info(ip_address, username, neighbor_list)

            # Check online status based on last_seen (replace 10 with desired timeout)
            current_time = time.time()
            if current_time - neighbor_list[ip_address]["last_seen"] > 10:
                neighbor_list[ip_address]["online_status"] = "Away"
                print(f"{username} is away.")
            else:
                neighbor_list[ip_address]["online_status"] = "Online"

            # Share the neighbor list (implementation depends on your application)
            # You could use a separate function to handle sharing with Chat Receiver

if __name__ == "__main__":
    main()

def receive_broadcasts():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind(("0.0.0.0", 6000))  # Listen on port 6000
        while True:
            data, address = sock.recvfrom(1024)
            try:
                # Parse JSON data
                peer_info = json.loads(data.decode())
                username = peer_info.get("username")
                print(peer_info)
            except json.JSONDecodeError:
                print(f"Received invalid broadcast data: {data}")