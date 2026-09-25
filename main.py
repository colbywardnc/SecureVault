import tkinter as tk
from vault import Vault
from crypto import generate_password

# Create the vault object.
vault = Vault()

# Create the main application window.
window = tk.Tk()
window.title("SecureVault")
window.geometry("400x300")

# Create the frame that will hold the credential list.
entries_frame = tk.Frame(window)

# Store the vault interface widgets so they can be hidden when locked.
vault_widgets = []

# Create a label for the master password.
password_label = tk.Label(window, text="Master Password:")
password_label.pack(pady=10)

# Create the master password input field.
password_entry = tk.Entry(window, show="*")
password_entry.pack(pady=5)

# Create a label to display the unlock result.
result_label = tk.Label(window, text="")
result_label.pack(pady=5)

# Try to unlock the vault with the entered master password.
def unlock_vault():
    password = password_entry.get()

    if vault.unlock(password):
        show_vault()
    else:
        result_label.config(text="Incorrect password")

# Show the form for adding a new credential.
def show_add_credential():
    add_window = tk.Toplevel(window)
    add_window.title("Add Credential")
    add_window.geometry("350x300")

    # Create the service input.
    service_label = tk.Label(add_window, text="Service:")
    service_label.pack(pady=5)

    service_entry = tk.Entry(add_window)
    service_entry.pack(pady=5)

    # Create the username input.
    username_label = tk.Label(add_window, text="Username:")
    username_label.pack(pady=5)

    username_entry = tk.Entry(add_window)
    username_entry.pack(pady=5)

    # Create the password input.
    password_label = tk.Label(add_window, text="Password:")
    password_label.pack(pady=5)

    password_entry = tk.Entry(add_window, show="*")
    password_entry.pack(pady=5)

    # Generate a secure password and place it in the password field.
    def generate_new_password():
        password = generate_password()
        password_entry.delete(0, tk.END)
        password_entry.insert(0, password)

    # Create a button for generating a password.
    generate_button = tk.Button(
        add_window,
        text="Generate Password",
        command=generate_new_password
    )
    generate_button.pack(pady=5)

    # Save the new credential to the vault.
    def save_credential():
        service = service_entry.get()
        username = username_entry.get()
        password = password_entry.get()

        vault.add_entry(service, username, password)
        refresh_entries()
        add_window.destroy()

    # Create the save button.
    save_button = tk.Button(
        add_window,
        text="Save Credential",
        command=save_credential
    )
    save_button.pack(pady=10)

# Show the details of a saved credential.
def view_credential(entry_id):
    entry = vault.find_entry_by_id(entry_id)

    if entry is None:
        return

    # Create a separate window for the credential details.
    view_window = tk.Toplevel(window)
    view_window.title("Credential")
    view_window.geometry("350x250")

    # Display the service name.
    service_label = tk.Label(
        view_window,
        text=f"Service: {entry[1]}"
    )
    service_label.pack(pady=10)

    # Display the username.
    username_label = tk.Label(
        view_window,
        text=f"Username: {entry[2]}"
    )
    username_label.pack(pady=10)

    # Display the password as hidden characters.
    password_label = tk.Label(
        view_window,
        text="Password: ********"
    )
    password_label.pack(pady=10)

    # Show the password when requested.
    def show_password():
        password_label.config(text=f"Password: {entry[3]}")

    # Create a button to reveal the password.
    show_password_button = tk.Button(
        view_window,
        text="Show Password",
        command=show_password
    )
    show_password_button.pack(pady=5)

    # Show the form for editing an existing credential.
    def edit_credential():
        edit_window = tk.Toplevel(view_window)
        edit_window.title("Edit Credential")
        edit_window.geometry("350x300")

        # Create a service input.
        service_label = tk.Label(edit_window, text="Service:")
        service_label.pack(pady=5)

        service_entry = tk.Entry(edit_window)
        service_entry.pack(pady=5)

        service_entry.insert(0, entry[1])

        # Create a username input.
        username_label = tk.Label(edit_window, text="Username:")
        username_label.pack(pady=5)

        username_entry = tk.Entry(edit_window)
        username_entry.pack(pady=5)

        username_entry.insert(0, entry[2])

        # Create a password input.
        password_label = tk.Label(edit_window, text="Password:")
        password_label.pack(pady=5)

        password_entry = tk.Entry(edit_window, show="*")
        password_entry.pack(pady=5)

        password_entry.insert(0, entry[3])

        # Save the edited credential.
        def save_changes():
            service = service_entry.get()
            username = username_entry.get()
            password = password_entry.get()

            vault.update_entry(entry_id, service, username, password)

            # Close the edit window.
            edit_window.destroy()

            # Close the old credential window.
            view_window.destroy()
            view_credential(entry_id)

            # Refresh the credential list.
            refresh_entries()

        # Create the save button.
        save_button = tk.Button(
            edit_window,
            text="Save Changes",
            command=save_changes
        )
        save_button.pack(pady=10)

    # Ask for the master password before deleting a credential.
    def confirm_delete():
        delete_window = tk.Toplevel(view_window)
        delete_window.title("Confirm Delete")
        delete_window.geometry("300x180")

        # Ask the user to enter the master password.
        master_label = tk.Label(
            delete_window,
            text="Enter the Master Password:"
        )
        master_label.pack(pady=10)

        master_entry = tk.Entry(
            delete_window,
            show="*"
        )
        master_entry.pack(pady=5)

        # Display an error if the master password is incorrect.
        error_label = tk.Label(delete_window, text="")
        error_label.pack(pady=5)

        # Verify the password and delete the credential.
        def delete_credential():
            master_password = master_entry.get()

            if vault.verify_master_password(master_password):
                vault.delete_entry(entry_id)
                delete_window.destroy()
                view_window.destroy()
                refresh_entries()
            else:
                error_label.config(text="Incorrect master password")

        # Create the delete confirmation button.
        delete_button = tk.Button(
            delete_window,
            text="Delete Credential",
            command=delete_credential
        )
        delete_button.pack(pady=10)

    # Create a button to start the deletion process.
    delete_button = tk.Button(
        view_window,
        text="Delete Credential",
        command=confirm_delete
    )
    delete_button.pack(pady=5)

    # Create a button to edit the credential.
    edit_button = tk.Button(
        view_window,
        text="Edit Credential",
        command=edit_credential
    )
    edit_button.pack(pady=5)


# Refresh the list of saved credentials.
def refresh_entries():
    for widget in entries_frame.winfo_children():
        widget.destroy()

    entries = vault.list_entries()

    for entry in entries:
        entry_button = tk.Button(
            entries_frame,
            text=f"{entry[0]} - {entry[1]} - {entry[2]}",
            command=lambda entry_id=entry[0]: view_credential(entry_id)
        )
        entry_button.pack(pady=2)

# Lock the vault and return to the login screen.
def lock_vault():
    vault.lock()

    # Remove the vault interface.
    entries_frame.pack_forget()

    for widget in vault_widgets:
        widget.pack_forget()

    # Show the login screen again.
    password_label.pack(pady=10)
    password_entry.pack(pady=5)
    unlock_button.pack(pady=10)
    result_label.pack(pady=5)

# Show the vault interface after a successful unlock.
def show_vault():
    # Clear the previous vault widget references.
    vault_widgets.clear()

    password_label.pack_forget()
    password_entry.pack_forget()
    unlock_button.pack_forget()
    result_label.pack_forget()

    vault_label = tk.Label(window, text="SecureVault")
    vault_label.pack(pady=20)

    vault_widgets.append(vault_label)

    # Show the credential list frame.
    entries_frame.pack(pady=5)

    # Display the saved credentials.
    refresh_entries()

    # Create a button for adding new credentials.
    add_button = tk.Button(
        window,
        text="Add Credential",
        command=show_add_credential
    )
    add_button.pack(pady=10)

    vault_widgets.append(add_button)

    # Create a button for locking the vault.
    lock_button = tk.Button(
        window,
        text="Lock Vault",
        command=lock_vault
    )
    lock_button.pack(pady=10)

    vault_widgets.append(lock_button)


# Create the unlock button.
unlock_button = tk.Button(window, text="Unlock", command=unlock_vault)
unlock_button.pack(pady=10)

# Start the application.
window.mainloop()