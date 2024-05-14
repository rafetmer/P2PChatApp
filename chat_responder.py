import socket
import json
import random
import pyDes


def status_updater(message, sender, receiver):
    with open("log.json", "r+") as file:
        json_data = json.load(file)    # Load the existing JSON data
        for message_data in json_data["chat_log"]:
            if message_data["sender"] == sender and message_data["receiver"] == receiver and message_data["message"] == message:
                message_data["status"] = "SENT"  # Update the status to "SENT"
        file.seek(0)  # Move the file pointer to the beginning of the file
        json.dump(json_data, file, indent=4)  # Write the updated data back to the file
        file.truncate()  # Remove any remaining old data


def chat_responder():
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(("127.0.0.1", 6001))
            sock.listen()
            try:
                data, address = sock.accept()
                print(f"Connected to:, {address}")
                message = json.loads(data.recv(1024).decode())
                if "key" in message:   # Initiator's public key is received
                    print("The public key received from peer.")
                    initiator_key = message["public_key"]

                    # Generate a pair of private and public keys for the responder
                    p = 23  # A prime number
                    g = 5   # A primitive root modulo p
                    b = random.randint(1, p-1)  # The private key
                    responder_key = (g**b) % p  # The public key
                    sock.send(json.dumps({"public_key": responder_key}).encode())
                    shared_secret_key = (initiator_key**b) % p               # Compute the shared secret key
                    # Receive the encrypted message from the initiator
                    encrypted_message = json.loads(data.recv(1024).decode())["encrypted_message"]
                    status_updater(encrypted_message, "peer", "You")  # Update the status of the message #TODO: Fix this

                    # Decrypt the message using the shared secret key
                    des = pyDes.des(shared_secret_key, pyDes.CBC, "\0\0\0\0\0\0\0\0", pad=None, padmode=pyDes.PAD_PKCS5)
                    decrypted_message = des.decrypt(encrypted_message)

                    print(f"Decrypted message: {decrypted_message}")

                elif "unencrypted_message" in message:
                    print(f"Received message: {message['unencrypted_message']}") # Print the unencrypted message
                    status_updater(message['unencrypted_message'], "You", "peer")  # Update the status of the message   #TODO: Fİx this
                else:
                    print("Invalid message received.")
            except socket.timeout:
                print("Timeout occurred while waiting for a connection.")


def main():
    chat_responder()


if __name__ == "__main__":
    main()