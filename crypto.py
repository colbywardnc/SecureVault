from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
import base64
import os

def generate_key():
    # Generate a secure random encryption key.
    return Fernet.generate_key()

def generate_salt():
    # Generate a random 16-byte salt for the master password
    return os.urandom(16)

def derive_key(password, salt):
    # Convert the master password into bytes
    password = password.encode()

    # Create a key derivation function.
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=600000,
    )

    # Derive the encryption key from the password
    key = kdf.derive(password)

    # Convert the key into the format Fernet expects
    return base64.urlsafe_b64encode(key)

def encrypt_data(data, key):
    # Encrypt the provided data using the encryption key.
    fernet = Fernet(key)
    return fernet.encrypt(data.encode())

def decrypt_data(data, key):
    # Decrypt the provided data using the encryption key.
    fernet = Fernet(key)
    return fernet.decrypt(data).decode()

