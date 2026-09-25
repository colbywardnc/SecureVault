import sqlite3
from crypto import generate_salt, derive_key, encrypt_data, decrypt_data

class Vault:
    def __init__(self):
        # The vault starts locked until the user unlocks it
        self.key = None

        # Store the saved credentials in the vault.
        self.connection = sqlite3.connect('securevault.db')

        # Create the credentials table if it does not already exist.
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service TEXT NOT NULL,
                username TEXT NOT NULL,
                encrypted_password BLOB NOT NULL
            )
        """)

        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS vault_metadata (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                salt BLOB NOT NULL,
                verification BLOB
            )
        """)

        # Check whether the vault already has a salt.
        cursor = self.connection.execute(
            "SELECT salt FROM vault_metadata WHERE id = 1"
        )

        if cursor.fetchone() is None:
            # Generate and save a new salt for the vault.
            salt = generate_salt()

            self.connection.execute(
                "INSERT INTO vault_metadata (id, salt) VALUES (1, ?)",
                (salt,)
            )

        self.connection.commit()

    def get_salt(self):
        # Retrieve the vault's stored salt from the database.
        cursor = self.connection.execute(
            "SELECT salt FROM vault_metadata WHERE id = 1"
        )

        # Return the stored salt.
        salt = cursor.fetchone()[0]
        return salt

    def create_key(self, master_password):
        # Get the salt stored for this vault.
        salt = self.get_salt()

        # Create an encryption key from the master password and salt.
        return derive_key(master_password, salt)

    def setup(self, master_password):
        # Do not allow setup if the vault already has a master password.
        if self.has_verification():
            return False

        # Create the encryption key from the new master password.
        key = self.create_key(master_password)

        # Store the key while the vault is unlocked.
        self.key = key

        # Create the verification value for the new vault.
        self.create_verification()

        # Return True to show that the vault was set up successfully.
        return True

    def unlock(self, master_password):
        # Create the encryption key from the master password.
        key = self.create_key(master_password)

        # Check whether the password matches the vault's verification value.
        if not self.verify_password(key):
            return False

        # Store the key while the vault is unlocked.
        self.key = key

        # Return True to show that the vault was unlocked successfully.
        return True

    def verify_master_password(self, master_password):
        # Create a key from the entered master password.
        key = self.create_key(master_password)

        # Check whether the password matches the vault's verification code.
        return self.verify_password(key)

    def lock(self):
        # Remove the encryption key from memory.
        self.key = None

    def create_verification(self):
        # Encrypt a fixed value using the vault's encryption key.
        verification = encrypt_data("SecureVault", self.key)

        # Store the encrypted verification value in the database.
        self.connection.execute(
            "UPDATE vault_metadata SET verification = ? WHERE id = 1",
            (verification,)
        )

        # Save the verification value.
        self.connection.commit()

    def has_verification(self):
        # Check whether a verification value has been stored.
        cursor = self.connection.execute(
            "SELECT verification FROM vault_metadata WHERE id = 1"
        )

        # Return True if a verification value exists.
        return cursor.fetchone()[0] is not None

    def verify_password(self, key):
        # Get the encrypted verification value from the database.
        cursor = self.connection.execute(
            "SELECT verification FROM vault_metadata WHERE id = 1"
        )

        # Get the stored verification value.
        verification = cursor.fetchone()[0]

        try:
            # Try to decrypt the verification using the provided key.
            decrypted = decrypt_data(verification, key)

            # The password is correct if the decrypted value matches.
            return decrypted == "SecureVault"

        except Exception:
            # A wrong key will cause decryption to fail.
            return False



    def add_entry(self, service, username, password):
        # Make sure the vault is unlocked before adding a credential.
        if self.key is None:
            return False

        # Encrypt the password before storing it in the database.
        encrypted_password = encrypt_data(password, self.key)

        # Adds the credential to the database.
        self.connection.execute(
            "INSERT INTO entries (service, username, encrypted_password) VALUES (?, ?, ?)",
            (service, username, encrypted_password)
        )

        # Save the change to the database.
        self.connection.commit()

        # Return True to show that the credential was added successfully.
        return True

    def find_entry(self, service):
        # Make sure the vault is unlocked before retrieving a credential.
        if self.key is None:
            return None

        # Search through the database for the requested service.
        cursor = self.connection.execute(
            "SELECT id, service, username, encrypted_password FROM entries WHERE service = ?",
            (service,)
        )

        # Get the first matching entry.
        entry = cursor.fetchone()

        if entry is None:
            return None

        # Decrypt the stored password using the vault's encryption key.
        password = decrypt_data(entry[3], self.key)

        # Return the credential with the decrypted password.
        return (entry[0], entry[1], entry[2], password)

    def find_entry_by_id(self, entry_id):
        if self.key is None:
            return None

        cursor = self.connection.execute(
            "SELECT id, service, username, encrypted_password "
            "FROM entries WHERE id = ?",
            (entry_id,)
        )

        entry = cursor.fetchone()

        if entry is None:
            return None

        password = decrypt_data(entry[3], self.key)
        return (entry[0], entry[1], entry[2], password)

    def delete_entry(self, entry_id):
        # Make sure the vault is unlocked before deleting a credential.
        if self.key is None:
            return False

        # Delete the credential with the requested ID.
        cursor = self.connection.execute(
            "DELETE FROM entries WHERE id = ?",
            (entry_id,)
        )

        # Save the change to the database.
        self.connection.commit()

        # Return True if a credential was actually deleted.
        return cursor.rowcount > 0

    def list_entries(self):
        # Make sure the vault is unlocked before listing credentials.
        if self.key is None:
            return []

        # Retrieve the ID, service, and username for each credential.
        cursor = self.connection.execute(
            "SELECT id, service, username FROM entries"
        )

        # Return the saved credentials without exposing their passwords.
        return cursor.fetchall()

    def update_entry(self, entry_id, service, username, password):
        # Make sure the vault is unlocked before updating a credential.
        if self.key is None:
            return False

        # Encrypt the new password before storing it.
        encrypted_password = encrypt_data(password, self.key)

        # Update the credential with the new information.
        cursor = self.connection.execute(
            "UPDATE entries SET service = ?, username = ?, encrypted_password = ? "
            "WHERE id = ?",
            (service, username, encrypted_password, entry_id)
        )

        # Save the change to the database.
        self.connection.commit()

        # Return True if a credential was actually updated.
        return cursor.rowcount > 0

