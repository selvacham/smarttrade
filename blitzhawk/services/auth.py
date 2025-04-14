import json
import os
import hashlib

# Path to store user data
USER_DB_FILE = "db/users.json"

# Ensure the db directory exists
os.makedirs(os.path.dirname(USER_DB_FILE), exist_ok=True)

# Utility function to hash passwords
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# Register a new user
def register_user(email: str, password: str) -> dict:
    users = load_users()
    
    if email in users:
        return {"success": False, "message": "User already exists."}

    users[email] = {
        "email": email,
        "password": hash_password(password),
    }

    save_users(users)
    return {"success": True, "message": "User registered successfully."}

# Login an existing user
def login_user(email: str, password: str) -> dict:
    users = load_users()

    if email not in users:
        return {"success": False, "message": "User not found."}

    if users[email]["password"] != hash_password(password):
        return {"success": False, "message": "Incorrect password."}

    return {"success": True, "message": "Login successful."}

# Load users from JSON file
def load_users() -> dict:
    if not os.path.exists(USER_DB_FILE):
        return {}
    with open(USER_DB_FILE, "r") as f:
        return json.load(f)

# Save users to JSON file
def save_users(users: dict):
    with open(USER_DB_FILE, "w") as f:
        json.dump(users, f, indent=4)
