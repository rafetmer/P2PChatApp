from RMY_service_announcer import ServiceAnnouncer
from RMY_peer_discovery import PeerDiscovery
from RMY_chat import action, chat_responder
from RMY_server import main as server_main
import threading
import time


def main():
    announcer = ServiceAnnouncer()
    discoverer = PeerDiscovery()

    announcer.username = input("Enter your username: ")
    print(f"Welcome, {announcer.username}!")
    username = announcer.username

    server_thread = threading.Thread(target=server_main)
    discovery_thread = threading.Thread(target=discoverer.main)
    broadcast_thread = threading.Thread(target=announcer.send_broadcast)
    action_thread = threading.Thread(target=action, args=(username,))
    chat_responder_thread = threading.Thread(target=chat_responder)
    chat_responder_thread.daemon = True


    server_thread.start()
    discovery_thread.start()
    broadcast_thread.start()
    print("Waiting for updated peer list...")
    time.sleep(3)
    action_thread.start()
    chat_responder_thread.start()



if __name__ == "__main__":
    main()