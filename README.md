# SecureVault

SecureVault is a local password manager built with Python and Tkinter. It securely stores account credentials in a local SQLite database and encrypts stored passwords using Fernet encryption.

## Features

- Master password protected vault
- Fernet encryption for stored credentials
- PBKDF2-HMAC-SHA256 key derivation
- Secure password generation using Python's `secrets` module
- Add, view, edit, and delete credentials
- Lock and unlock the vault
- SQLite database for local storage
- Automated tests using pytest

## Technologies

- Python
- Tkinter
- SQLite
- Cryptography
- Pytest

## Security

SecureVault uses several security mechanisms to protect stored credentials:

- Master passwords are converted into encryption keys using PBKDF2-HMAC-SHA256.
- Each vault uses a randomly generated 16-byte salt.
- PBKDF2 uses 600,000 iterations to make password-based key derivation more resistant to brute-force attacks.
- Stored credentials are encrypted using Fernet symmetric encryption.
- Password generation uses Python's cryptographically secure `secrets` module.
- The vault encryption key is cleared from the active vault object when the vault is locked.

## Installation

Clone the repository:

    git clone https://github.com/colbywardnc/SecureVault.git
    cd SecureVault

Create and activate a virtual environment:

### Windows

    python -m venv .venv
    .venv\Scripts\activate

Install the required dependencies:

    pip install -r requirements.txt

## Usage

Run the application:

    python main.py

On the first run, SecureVault will create a local SQLite database and initialize the vault.

Enter your master password to unlock the vault. Once unlocked, you can add, view, edit, and delete stored credentials.

## Testing

SecureVault includes automated tests using pytest.

Run the test suite with:

    pytest

The test suite covers:

- Vault setup and unlocking
- Incorrect master password rejection
- Credential creation, retrieval, updating, and deletion
- Vault locking
- Secure password generation

## Limitations

SecureVault is a portfolio and educational project and has not been independently audited for security.

Future improvements may include:

- Automatic vault timeout and locking
- Credential search
- Clipboard integration with automatic clearing
- Improved input validation
- Master password changing
- Additional security hardening