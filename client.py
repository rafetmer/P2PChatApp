from service_announcer import ServiceAnnouncer
from peer_discovery import PeerDiscovery
from chat_initiator import action, chat_responder
from server import main as server_main
import threading
import time


def main():
    announcer = ServiceAnnouncer()
    discoverer = PeerDiscovery()

    # Get username before starting threads (Req. 2.1.0-A)
    announcer.username = input("Enter your username: ")
    print(f"Welcome, {announcer.username}!")
    username = announcer.username



    server_thread = threading.Thread(target=server_main)
    discovery_thread = threading.Thread(target=discoverer.main)
    broadcast_thread = threading.Thread(target=announcer.send_broadcast)
    action_thread = threading.Thread(target=action, args=(username,))

    responder_thread = threading.Thread(target=chat_responder)
    server_thread.start()
    #responder_thread.start()
    discovery_thread.start()
    broadcast_thread.start()
    print("Waiting for updated peer list...")
    time.sleep(8)
    action_thread.start()






    #discovery_thread.join()
    #broadcast_thread.join()
    #action_thread.join()

    # Wait for the send_broadcast thread to finish (optional)
    # broadcast_thread.join()  # Uncomment this line if you want action() to wait for broadcast

if __name__ == "__main__":
    main()