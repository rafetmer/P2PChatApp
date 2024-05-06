import socket
import json
import time

socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def get_username():
    return input("Please enter your username: ")

