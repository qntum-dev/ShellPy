import os
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

PRIVATE_KEY_FILE = "private_key.pem"
AUTHORIZED_KEYS_FILE = "authorized_keys.txt"

def generate_key_pair():
    # Generate an RSA key pair
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    # Save the private key to a file
    with open(PRIVATE_KEY_FILE, "wb") as private_key_file:
        private_key_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        )
        private_key_file.write(private_key_bytes)

    # Get the corresponding public key
    public_key = private_key.public_key()
    public_key_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.OpenSSH,
        format=serialization.PublicFormat.OpenSSH,
    )
    
    # Print the base64 representation of the public key
    public_key_base64 = public_key_bytes.decode("utf-8").strip()
    print(f"Base64 representation of the public key:\n{public_key_base64}")

    return private_key, public_key_base64

def main():
    private_key, public_key_base64 = generate_key_pair()

    # Save the base64 representation of the public key to the authorized_keys.txt file
    with open(AUTHORIZED_KEYS_FILE, "w") as authorized_keys_file:
        authorized_keys_file.write(public_key_base64)

    print(f"Private key saved to {PRIVATE_KEY_FILE}")
    print(f"Base64 representation of the public key saved to {AUTHORIZED_KEYS_FILE}")

if __name__ == "__main__":
    main()
