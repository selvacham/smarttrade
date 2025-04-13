# main.py
import ttkbootstrap as ttk
import tkinter as tk
from ui.login_ui import show_login_ui
from ui.register_ui import show_register_ui

def main():
    root = ttk.Window(themename="darkly")
    root.title("Welcome to BlitzHawk")
    root.geometry("400x250")

    ttk.Label(root, text="Welcome to BlitzHawk", font=("Helvetica", 18)).pack(pady=20)
    ttk.Label(root, text="Select an option below", font=("Helvetica", 12)).pack(pady=10)

    ttk.Button(root, text="Login", command=lambda: [root.destroy(), show_login_ui()], width=25, bootstyle="primary").pack(pady=10)
    ttk.Button(root, text="Register", command=lambda: [root.destroy(), show_register_ui()], width=25, bootstyle="success").pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()
