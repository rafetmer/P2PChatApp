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
        print(neighbor_list)


def receive_broadcasts():
    # Initialize empty dictionary for neighbor information
    neighbor_list = {}

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("0.0.0.0", 6000))  # Listen on port 6000
        while True:
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
                with open('neighbor_list.txt', 'w') as file:
                    file.write(json.dumps(neighbor_list))

            except json.JSONDecodeError:
                print(f"Received invalid broadcast data: {data}")


def main():
    # Initialize empty dictionary for neighbor information
    neighbor_list = {}

    while True:
        # Receive data from UDP broadcast
        data, address = receive_broadcasts()
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

            # Write the neighbor_list dictionary to a local text file
if __name__ == "__main__":
    main()


