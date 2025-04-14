# ui/login_ui.py
import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
import json
import os

from auth.auth_utils import hash_password, verify_password

USER_DB = "database/users.json"

def load_users():
    if os.path.exists(USER_DB):
        with open(USER_DB, "r") as f:
            return json.load(f)
    return {}

def show_dashboard(email):
    dashboard = ttk.Window(themename="darkly")
    dashboard.title("Welcome to BlitzHawk")
    dashboard.geometry("400x200")
    ttk.Label(dashboard, text=f"Logged in as {email}", font=("Helvetica", 14)).pack(pady=30)
    ttk.Button(dashboard, text="Logout", command=dashboard.destroy, bootstyle="danger").pack(pady=10)
    dashboard.mainloop()

def show_login_ui():
    root = ttk.Window(themename="darkly")
    root.title("BlitzHawk - Login")
    root.geometry("400x280")

    ttk.Label(root, text="Login to BlitzHawk", font=("Helvetica", 16)).pack(pady=10)

    email_var = tk.StringVar()
    pass_var = tk.StringVar()

    ttk.Label(root, text="Email").pack(pady=(10, 0))
    email_entry = ttk.Entry(root, textvariable=email_var, width=30)
    email_entry.pack()

    ttk.Label(root, text="Password").pack(pady=(10, 0))
    pass_entry = ttk.Entry(root, textvariable=pass_var, show="*", width=30)
    pass_entry.pack()

    def login_user():
        email = email_var.get()
        password = pass_var.get()

        if not email or not password:
            messagebox.showerror("Error", "Please fill all fields.")
            return

        users = load_users()
        if email not in users:
            messagebox.showerror("Error", "User does not exist.")
            return

        if verify_password(password, users[email]["password"]):
            messagebox.showinfo("Success", f"Welcome, {email}!")
            root.destroy()
            show_dashboard(email)
        else:
            messagebox.showerror("Error", "Incorrect password.")

    ttk.Button(root, text="Login", command=login_user, width=25, bootstyle="primary").pack(pady=20)

    root.mainloop()
