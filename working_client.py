import base64
import readline
import socket
import subprocess
import os
import paramiko
from paramiko import RSAKey

PRIVATE_KEY_FILE = "private_key.pem"


class ServerDirectoryCompleter:
    def __init__(self, client_socket, private_key):
        self.client_socket = client_socket
        self.private_key = private_key
        self.directories = []

    def complete(self, text, state):
        current_input = readline.get_line_buffer().lstrip()

        if current_input.startswith("cd "):
            # For 'cd' commands, suggest directories from the server
            if not self.directories:
                self.update_directories()

            completions = [directory for directory in self.directories if directory.startswith(text)]
            return completions[state]

    def update_directories(self):
        self.client_socket.send("get_directories".encode('utf-8'))
        directories = self.client_socket.recv(4096).decode('utf-8').split('\n')
        self.directories = [directory for directory in directories if directory]  # Remove empty strings


def get_server_directory(client_socket):
    client_socket.send("getcwd".encode('utf-8'))
    server_directory = client_socket.recv(4096).decode('utf-8')
    return server_directory


def send_command(client_socket, private_key):
    completer = ServerDirectoryCompleter(client_socket, private_key)
    readline.set_completer(completer.complete)
    readline.parse_and_bind("tab: complete")

    try:
        while True:
            user_input = input('Enter command to execute on the server (or \'exit\' to quit, \'close\' to close the server): ')

            if not user_input:
                continue  # Ignore empty input

            if user_input.lower() == "exit":
                break  # Exit the loop if the user entered the exit command

            client_socket.send(user_input.encode('utf-8'))

            if user_input.lower() == "close":
                print("Closing the server as requested.")
                break  # Exit the loop to close the server

            result = client_socket.recv(4096).decode('utf-8')

            if user_input.lower().startswith("cd "):
                print(result)
                completer.update_directories()  # Request the server to update directories
                continue

            if user_input.lower() == "getcwd":
                current_server_directory = get_server_directory(client_socket)
                print(f"Server directory: {current_server_directory}")
                continue  # Skip the command execution for "getcwd"

            print(result)

    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        pass
    finally:
        client_socket.close()


def generate_key_pair():
    private_key = RSAKey.generate(2048)
    with open(PRIVATE_KEY_FILE, "wb") as private_key_file:
        private_key.write_private_key_file(private_key_file)

    return private_key


def main():
    server_host = input("Enter the server host: ")
    server_port = int(input("Enter the server port: "))  # Use the same port as in the server script

    private_key = None

    try:
        with open(PRIVATE_KEY_FILE, "rb") as private_key_file:
            private_key = RSAKey(filename=PRIVATE_KEY_FILE)

    except FileNotFoundError:
        print("Generating a new RSA key pair.")
        private_key = generate_key_pair()

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_host, server_port))

    try:
        
        public_key_data = private_key.get_base64().encode('utf-8')
        #print(f"Sending public key data:\n{public_key_data.decode('utf-8')}")


        client_socket.send(public_key_data)

        auth_response = client_socket.recv(1024).decode('utf-8')
        print(auth_response)
        if auth_response == "SSH_AUTH_SUCCESS":
            print("Server authentication successful.")
            send_command(client_socket, private_key)
        else:
            print("Server authentication failed. Closing connection.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()

if __name__ == "__main__":
    main()
