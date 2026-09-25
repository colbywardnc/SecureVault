import sqlite3

class Vault:
    def __init__(self):
        # Store the saved credentials in the vault.
        self.connection = sqlite3.connect('securevault.db')

        # Create the credentials table if it does not already exist.
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service TEXT NOT NULL,
                username TEXT NOT NULL,
                password TEXT NOT NULL
            )
        """)

        self.connection.commit()

    def add_entry(self, service, username, password):
        # Adds the credential to the database.
        self.connection.execute(
            "INSERT INTO entries (service, username, password) VALUES (?, ?, ?)",
            (service, username, password)
        )

        # Save the change to the database.
        self.connection.commit()

    def find_entry(self, service):
        # Search through the database for the requested service.
        cursor = self.connection.execute(
            "SELECT id, service, username, password FROM entries WHERE service = ?",
            (service,)
        )

        # Get the first matching entry.
        entry = cursor.fetchone()

        return entry

