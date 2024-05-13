import socket
import json

# this will be the JSON chat responder
def receive_broadcasts():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("127.0.0.1", 6001))
        sock.listen()
        conn, addr = sock.accept()
        with conn:
            print("Connected by", addr)
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                print(data.decode())
                conn.sendall(data)
        print("Connection closed")

if __name__ == "__main__":
    receive_broadcasts()