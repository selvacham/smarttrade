# ui/register_ui.py
import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
from auth.auth_utils import hash_password
import json
import os

USER_DB = "database/users.json"

def save_user(email, password):
    if not os.path.exists("database"):
        os.makedirs("database")

    users = {}
    if os.path.exists(USER_DB):
        with open(USER_DB, "r") as f:
            users = json.load(f)

    if email in users:
        return False, "User already exists"

    users[email] = {"password": hash_password(password)}
    with open(USER_DB, "w") as f:
        json.dump(users, f, indent=4)
    return True, "User registered successfully"

def show_register_ui():
    root = ttk.Window(themename="darkly")
    root.title("BlitzHawk - Register")
    root.geometry("400x320")

    ttk.Label(root, text="Register for BlitzHawk", font=("Helvetica", 16)).pack(pady=10)

    email_var = tk.StringVar()
    pass_var = tk.StringVar()
    confirm_var = tk.StringVar()

    ttk.Label(root, text="Email").pack(pady=(10, 0))
    email_entry = ttk.Entry(root, textvariable=email_var, width=30)
    email_entry.pack()

    ttk.Label(root, text="Password").pack(pady=(10, 0))
    pass_entry = ttk.Entry(root, textvariable=pass_var, show="*", width=30)
    pass_entry.pack()

    ttk.Label(root, text="Confirm Password").pack(pady=(10, 0))
    confirm_entry = ttk.Entry(root, textvariable=confirm_var, show="*", width=30)
    confirm_entry.pack()

    def register_user():
        email = email_var.get()
        password = pass_var.get()
        confirm = confirm_var.get()

        if not email or not password or not confirm:
            messagebox.showerror("Error", "Please fill all fields.")
            return

        if password != confirm:
            messagebox.showerror("Error", "Passwords do not match.")
            return

        success, msg = save_user(email, password)
        if success:
            messagebox.showinfo("Success", msg)
            root.destroy()  # or go to login_ui
        else:
            messagebox.showerror("Error", msg)

    ttk.Button(root, text="Register", command=register_user, width=25, bootstyle="success").pack(pady=20)

    root.mainloop()
