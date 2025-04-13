from ttkbootstrap import Window
from ttkbootstrap.constants import *
from tkinter import messagebox
from tkinter import StringVar
import ttkbootstrap as ttk

# Replace with your actual auth logic
from services.auth import register_user, login_user

# Launch manual UI after login
from manual_order_ui import launch_manual_order_ui

def launch_login_register_ui():
    app = Window(themename="darkly")
    app.title("BlitzHawk - Login/Register")
    app.geometry("400x500")

    email_var = StringVar()
    password_var = StringVar()
    confirm_password_var = StringVar()
    is_login_mode = True

    def toggle_mode():
        nonlocal is_login_mode
        is_login_mode = not is_login_mode
        mode_btn.config(text="Switch to Register" if is_login_mode else "Switch to Login")
        confirm_label.pack_forget()
        confirm_entry.pack_forget()
        submit_btn.config(text="Login" if is_login_mode else "Register")
        if not is_login_mode:
            confirm_label.pack(anchor="w", pady=(10, 0))
            confirm_entry.pack(fill="x", pady=5)

    def submit():
        email = email_var.get().strip()
        password = password_var.get().strip()
        confirm = confirm_password_var.get().strip()

        if not email or not password:
            messagebox.showwarning("Missing Data", "Please enter email and password.")
            return

        if not is_login_mode and password != confirm:
            messagebox.showerror("Password Mismatch", "Passwords do not match.")
            return

        if is_login_mode:
            if login_user(email, password):
                messagebox.showinfo("Login Successful", "Welcome!")
                app.destroy()
                launch_manual_order_ui()
            else:
                messagebox.showerror("Login Failed", "Invalid credentials.")
        else:
            if register_user(email, password):
                messagebox.showinfo("Registration Successful", "You can now login.")
                toggle_mode()
            else:
                messagebox.showerror("Registration Failed", "User already exists or error occurred.")

    # Title
    ttk.Label(app, text="BlitzHawk Login", font=("Segoe UI", 18, "bold")).pack(pady=20)

    frm = ttk.Frame(app, padding=20)
    frm.pack(fill="x")

    ttk.Label(frm, text="Email").pack(anchor="w")
    ttk.Entry(frm, textvariable=email_var).pack(fill="x", pady=5)

    ttk.Label(frm, text="Password").pack(anchor="w", pady=(10, 0))
    ttk.Entry(frm, textvariable=password_var, show="*").pack(fill="x", pady=5)

    confirm_label = ttk.Label(frm, text="Confirm Password")
    confirm_entry = ttk.Entry(frm, textvariable=confirm_password_var, show="*")

    submit_btn = ttk.Button(frm, text="Login", command=submit, bootstyle="success")
    submit_btn.pack(pady=20)

    mode_btn = ttk.Button(frm, text="Switch to Register", command=toggle_mode, bootstyle="info")
    mode_btn.pack()

    app.mainloop()

# Entry point
if __name__ == "__main__":
    launch_login_register_ui()
