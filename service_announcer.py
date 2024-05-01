import socket
import json
import time


# Service announcer function
def service_announcer(username, broadcast_ip, broadcast_port):
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    # Periodically send broadcast messages
    while True:
        # Construct JSON message containing username and IP address
        message = json.dumps({"username": username})

        # Send the broadcast message
        sock.sendto(message.encode('utf-8'), (broadcast_ip, broadcast_port))

        print("Broadcasted presence:", message)

        # Sleep for 8 seconds before sending the next broadcast
        time.sleep(8)


# Main function
if __name__ == "__main__":
    # Prompt user for their username
    username = input("Enter your username: ")

    # Specify the broadcast IP address and port
    broadcast_ip = "255.255.255.255"  # Broadcast address
    broadcast_port = 6000  # Broadcast port

    # Start the service announcer
    service_announcer(username, broadcast_ip, broadcast_port)
