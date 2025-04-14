import time
import requests
from datetime import datetime
import sys
import os
# Allow imports from parent directories
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Assuming you already have access to `get_current_price` method and necessary data
from services.angelone_api import get_current_price
from config.settings import SL, TARGET

def check_sl_target_hit():
    current_price = get_current_price()  # Get the latest price from the API

    if current_price <= SL:
        log(f"[ALERT] SL hit! Current Price: {current_price} | Stop Loss: {SL}")
        return "SL"
    
    if current_price >= TARGET:
        log(f"[ALERT] Target hit! Current Price: {current_price} | Target: {TARGET}")
        return "TARGET"

    return None

def log(message):
    # Assuming the function logs to the log box in your UI (from tkinter)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_box.config(state="normal")
    log_box.insert(tk.END, f"{timestamp} - {message}\n")
    log_box.see(tk.END)
    log_box.config(state="disabled")

def monitor_price():
    while True:
        result = check_sl_target_hit()
        if result:
            # Optionally, trigger a message box to show SL/Target hit to the user
            if result == "SL":
                messagebox.showwarning("Stop Loss Triggered", "Stop Loss has been hit!")
            elif result == "TARGET":
                messagebox.showinfo("Target Triggered", "Target has been reached!")
            break  # Optionally exit the loop or you could handle re-checking here
        time.sleep(5)  # Check every 5 seconds (can be adjusted)
