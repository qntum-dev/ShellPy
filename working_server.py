import base64
import socket
import os
import subprocess
from paramiko import RSAKey
import logging

# Set up the logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

AUTHORIZED_KEYS_FILE = "authorized_keys.txt"


def start_server():
    host = '0.0.0.0'  # Listen on all available interfaces
    port = 12349  # Choose a port number

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)  # Listen for one incoming connection

    logger.info(f"Server listening on {host}:{port}")

    try:
        while True:
            client_socket, client_address = server_socket.accept()
            logger.info(f"Connection from {client_address}")

            try:
                authorized_keys = load_authorized_keys()

                if not authorized_keys:
                    logger.error("No authorized keys found. Server cannot authenticate clients.")
                    break

                key = authenticate_client(client_socket, authorized_keys)
                if key:
                    handle_authenticated_client(client_socket, key)

            except Exception as e:
                logger.error(f"Error: {e}")
            finally:
                client_socket.close()

    except KeyboardInterrupt:
        logger.info("Server interrupted. Continuing to run.")
    finally:
        server_socket.close()

def load_authorized_keys():
    try:
        with open(AUTHORIZED_KEYS_FILE, "r") as file:
            return [line.strip() for line in file.readlines()]
    except FileNotFoundError:
        return []


def authenticate_client(client_socket, authorized_keys):
   

    public_key_data = client_socket.recv(4096)

    try:
        received_key_base64 = public_key_data.decode('utf-8', errors='ignore').strip()
        # logger.info(f"Received public key data: {public_key_data}")

    except Exception as e:
        # logger.error(f"Error decoding or extracting key: {e}")
        client_socket.send(b"SSH_AUTH_FAILURE")
        return None

    authorized_keys_base64 = [key.strip() for key in authorized_keys]  # Strip leading/trailing whitespaces
    # logger.info(f"Authorized keys: {authorized_keys_base64}")

    for key_str in authorized_keys_base64:
        key = RSAKey(data=base64.b64decode(key_str))
        if key_str == received_key_base64:
            logger.info("Client authenticated successfully.")
            client_socket.send(b"SSH_AUTH_SUCCESS")
            return key

    logger.info("Client authentication failed. Key is not authorized")
    client_socket.send(b"SSH_AUTH_FAILURE")
    return None


def handle_authenticated_client(client_socket, key):
    current_directory = "C:/"

    try:
        while True:
            try:
                data = client_socket.recv(1024).decode('utf-8')
                if not data:
                    # No data received, indicating that the connection has been closed
                    logger.info("Connection closed by the client.")
                    break

                # logger.info(f"Received command: {data}")

                if data.lower() == "getcwd":
                    client_socket.send(os.getcwd().encode('utf-8'))
                elif data.lower() == "get_directories":
                    directories = "\n".join(os.listdir(current_directory))
                    client_socket.send(directories.encode('utf-8'))
                elif data.lower() == "exit":
                    break
                elif data.lower() == "close":
                    logger.info("Closing the server as requested.")
                    break  # Terminate the loop to close the client socket
                elif data.startswith("cd "):
                    # Change the current working directory
                    new_dir = os.path.normpath(os.path.join(current_directory, data[3:]))
                    try:
                        os.chdir(new_dir)
                        current_directory = os.getcwd()
                        response = f"Changed directory to {current_directory}"
                    except FileNotFoundError:
                        response = f"Directory not found: {new_dir}"
                    client_socket.send(response.encode('utf-8'))
                else:
                    try:
                        # Use the provided key for subprocess execution
                        with subprocess.Popen(
                                data, shell=True, cwd=current_directory,
                                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as process:
                            output, error = process.communicate()
                            response = f"Output:\n{output}\nError:\n{error}"
                    except Exception as e:
                        response = f"Error executing command: {e}"

                    client_socket.send(response.encode('utf-8'))

            except KeyboardInterrupt:
                logger.info("KeyboardInterrupt received. Ignoring and continuing.")
                client_socket.send(b"KeyboardInterrupt. Ignoring and continuing.")
                continue  # Ignore KeyboardInterrupt and continue the loop

    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        client_socket.close()

if __name__ == "__main__":
    start_server()
