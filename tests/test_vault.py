import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from vault import Vault
from crypto import generate_password


def test_vault_setup_and_unlock(tmp_path, monkeypatch):
    # Use a temporary directory so the real vault database is not affected.
    monkeypatch.chdir(tmp_path)

    # Create a new vault.
    vault = Vault()

    # Set up the vault with a master password.
    assert vault.setup("TestMasterPassword123!")

    # The correct master password should unlock the vault.
    assert vault.unlock("TestMasterPassword123!")

def test_wrong_master_password(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    # Create a new vault.
    vault = Vault()

    # Set up the vault with a master password.
    vault.setup("TestMasterPassword123!")

    # The wrong password should not unlock the vault.
    assert not vault.unlock("WrongPassword123!")

def test_vault_crud(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    # Create and unlock a new vault.
    vault = Vault()
    vault.setup("TestMasterPassword123!")
    assert vault.unlock("TestMasterPassword123!")

    # Add a credential.
    assert vault.add_entry(
        "Discord",
        "Test",
        "Password12!!"
    )

    # Find the credential we just added.
    entry = vault.find_entry("Discord")
    assert entry is not None

    entry_id = entry[0]

    # Update the credential
    assert vault.update_entry(
        entry_id,
        "GitHub",
        "Tester2",
        "NewPassword??"
    )

    # Verify the updated information.
    updated = vault.find_entry_by_id(entry_id)
    assert updated[2] == "Tester2"

    # Delete the credential.
    assert vault.delete_entry(entry_id)

    # Verify the credential is gone.
    assert vault.find_entry_by_id("GitHub") is None

def test_lock_clears_key(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    # Create and unlock a new vault.
    vault = Vault()
    vault.setup("TestMasterPassword123!")
    assert vault.unlock("TestMasterPassword123!")

    # The vault should have an encryption key while unlocked.
    assert vault.key is not None

    # Lock the vault.
    vault.lock()

    # The Encryption key should be cleared.
    assert vault.key is None

def test_generated_password():
    password = generate_password(24)

    # The generated password should have the requested length.
    assert len(password) == 24

    # The password should only contain characters form the generator's character set.
    allowed_characters = set(
        "abcdefghijklmnopqrstuvwxyz"
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        "0123456789"
        "!@#$%^&*()_+"
    )

    assert set(password) <= (allowed_characters)
