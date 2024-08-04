# Shell_Py
The server-side Python script establishes secure remote command execution, uses a SSH public-private key mechanism for security. The client-side script connects, sends commands, and provides directory interactions with tab-completion suggestions for seamless remote management.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Host](#host)

## Installation

Install the dependencies on both sides, client and the server.

```bash
# Install the requirements
pip install -r requirements.txt
```


Run the generate_keys.py to get the authorized_keys.txt and the private_key.pem.
```bash
# Run the generate_keys.py
python generate_keys.py
```

or, you can run

```bash
# Run the generate_keys.py
python3 generate_keys.py
```

## Usage

After generating,
1. Paste the private_key.pem on the client side in the same directory where the working_client.py is located
2. Paste the authorized_keys.txt on theserver side in the same directory where the working_server.py is located

Now your server and the client is ready to communicate


Start the server
```bash
#run working_server.py
python working_server.py
```

Start the client
```bash
#run working_client.py
python working_client.py
```

In the Client side following will be asked
```bash
Enter the server host: [Host] # Enter the server's IP address where the working_server.py is running
Enter the server port: # Enter the port (default port is 12349)
```
To know more about the [Host](#host)

## Host
If you are running the working_server.py in your local machine

For Windows
```bash
ipconfig | findstr IPv4
```
For Unix based
```bash
ip addr show | awk '/inet /{print $NF, $2}'
```
This commands will give you your local machine's ip address.

Otherwise, if you are running on a cloud server then their public ip address will be used.
