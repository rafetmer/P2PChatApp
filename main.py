from service_announcer import service_announcer

localhost = '127.0.0.1'
port = 12000

def main():

    if __name__ == "__main__":
        # Prompt user for their username
        username = input("Enter your username: ")

        # Specify the broadcast IP address and port
        broadcast_ip = "255.255.255.255"  # Broadcast address
        broadcast_port = 6000  # Broadcast port

        # Start the service announcer
        service_announcer(username, broadcast_ip, broadcast_port)
