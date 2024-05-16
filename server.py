import json
import random
import pyDes
import threading
from peer_discovery import PeerDiscovery
from service_announcer import ServiceAnnouncer
from socket import *
from chat_initiator import action, chat_responder
# rest of your code

def main():
    chat_responder()


    announcer = ServiceAnnouncer()
    announcer.receive_broadcasts()




if __name__ == "__main__":
    main()