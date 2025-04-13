from ttkbootstrap import Window, Style
from ttkbootstrap.constants import *
from tkinter import messagebox, scrolledtext
from tkinter import StringVar
import ttkbootstrap as ttk
import time
from threading import Thread

# Mocked functions (replace with real ones)
from services.angelone_api import place_order, get_ltp, refresh_token
from services.monitor import monitor_prices
from services.symbol_lookup import find_symbol_token

tracked_orders = []
TOKEN_EXPIRATION_TIME = 3600
last_token_time = time.time()

def is_token_expired():
    global last_token_time
    current_time = time.time()
    if current_time - last_token_time > TOKEN_EXPIRATION_TIME:
        last_token_time = current_time
        return True
    return False

def log(message, log_box):
    log_box.config(state="normal")
    log_box.insert("end", message + "\n")
    log_box.see("end")
    log_box.config(state="disabled")

def add_to_tracking(symbol, symboltoken, exchange, action, entry_price, qty, sl_points, target_points, log_box):
    sl_price = entry_price - sl_points if action == "BUY" else entry_price + sl_points
    target_price = entry_price + target_points if action == "BUY" else entry_price - target_points

    tracked_orders.append({
        "symbol": symbol,
        "symboltoken": symboltoken,
        "exchange": exchange,
        "action": action,
        "entry": entry_price,
        "sl": sl_price,
        "target": target_price,
        "qty": qty
    })
    log(f"[TRACKING] {symbol} Entry={entry_price} SL={sl_price} Target={target_price}", log_box)

def launch_manual_order_ui():
    root = Window(themename="darkly")
    root.title("BlitzHawk - Manual Order")
    root.geometry("480x720")

    # Variables
    instrument_var = StringVar(value="NIFTY")
    symbol_var = StringVar()
    action_var = StringVar(value="BUY")
    qty_var = StringVar()
    sl_var = StringVar()
    target_var = StringVar()
    mode_var = StringVar(value="LIVE")
    ltp_var = StringVar(value="LTP: --")

    def update_ltp(event=None):
        symbol = symbol_var.get().strip().upper()
        if not symbol:
            return
        symboltoken, exchange = find_symbol_token(symbol)
        if not symboltoken:
            ltp_var.set("LTP: Symbol not found")
            return
        ltp = get_ltp(symboltoken, exchange)
        if ltp:
            ltp_var.set(f"LTP: {ltp}")
        else:
            ltp_var.set("LTP: Error")

    def handle_place_order():
        tradingsymbol = symbol_var.get().strip().upper()
        action = action_var.get()
        qty = qty_var.get()
        sl_value = sl_var.get()
        target_value = target_var.get()
        mode = mode_var.get().strip().upper()

        log(f"[DEBUG] Mode: {mode}", log_box)

        if not tradingsymbol or not qty:
            messagebox.showwarning("Missing Data", "Please fill in all fields.")
            return

        try:
            qty = int(qty)
            sl_value = float(sl_value or 0)
            target_value = float(target_value or 0)
        except ValueError:
            messagebox.showerror("Invalid Input", "Quantity, SL and Target must be numbers.")
            return

        symboltoken, exchange = find_symbol_token(tradingsymbol)
        if not symboltoken:
            messagebox.showerror("Symbol Error", "Symbol not found.")
            return

        if mode == "PAPER":
            log(f"[PAPER] {action} {tradingsymbol} x{qty} | SL={sl_value}, Target={target_value}", log_box)
            messagebox.showinfo("Paper Mode", "Simulated order placed.")
            return

        try:
            if is_token_expired():
                log("[INFO] Token expired. Refreshing...", log_box)
                new_token = refresh_token()
                if not new_token:
                    messagebox.showerror("Token Refresh Failed", "Couldn't refresh token.")
                    return

            response = place_order(tradingsymbol, symboltoken, action, exchange, qty, is_paper=False)
            log(f"[LIVE ORDER] {action} {tradingsymbol} -> {response.get('message', 'Done')}", log_box)

            if response.get("status") == "success":
                if sl_value and target_value:
                    entry = get_ltp(symboltoken, exchange)
                    add_to_tracking(tradingsymbol, symboltoken, exchange, action, entry, qty, sl_value, target_value, log_box)
                    Thread(target=monitor_prices, args=(log_box,), daemon=True).start()
            else:
                messagebox.showerror("Order Error", response.get("message", "Unknown error"))

        except Exception as e:
            log(f"[ERROR] {e}", log_box)
            messagebox.showerror("Exception", str(e))

    # Header
    ttk.Label(root, text="Manual Order Execution", font=("Segoe UI", 16, "bold")).pack(pady=10)

    # Instrument & Symbol Section
    frm = ttk.Frame(root, padding=10)
    frm.pack(fill="x")
    ttk.Label(frm, text="Instrument").pack(anchor="w")
    ttk.Combobox(frm, textvariable=instrument_var, values=["NIFTY", "BANKNIFTY", "CRUDEOIL"]).pack(fill="x", pady=5)

    ttk.Label(frm, text="Trading Symbol").pack(anchor="w")
    symbol_entry = ttk.Entry(frm, textvariable=symbol_var)
    symbol_entry.pack(fill="x", pady=5)
    symbol_entry.bind("<KeyRelease>", update_ltp)

    ttk.Label(frm, textvariable=ltp_var, font=("Segoe UI", 10)).pack(anchor="w", pady=5)

    # Action & Quantity
    ttk.Label(frm, text="Action").pack(anchor="w", pady=(10, 0))
    ttk.Combobox(frm, textvariable=action_var, values=["BUY", "SELL"]).pack(fill="x", pady=5)

    ttk.Label(frm, text="Quantity").pack(anchor="w")
    ttk.Entry(frm, textvariable=qty_var).pack(fill="x", pady=5)

    # SL & Target
    ttk.Label(frm, text="Stop Loss (pts)").pack(anchor="w", pady=(10, 0))
    ttk.Entry(frm, textvariable=sl_var).pack(fill="x", pady=5)

    ttk.Label(frm, text="Target (pts)").pack(anchor="w")
    ttk.Entry(frm, textvariable=target_var).pack(fill="x", pady=5)

    # Mode
    ttk.Label(frm, text="Mode").pack(anchor="w", pady=(10, 0))
    ttk.Combobox(frm, textvariable=mode_var, values=["LIVE", "PAPER"]).pack(fill="x", pady=5)

    # Submit Button
    ttk.Button(frm, text="Place Order", command=handle_place_order, bootstyle="success").pack(pady=15)

    # Logs
    ttk.Label(root, text="Execution Log", font=("Segoe UI", 12, "bold")).pack(pady=5)
    log_box = scrolledtext.ScrolledText(root, height=12, wrap="word", state="disabled", bg="#222", fg="#00ffcc", insertbackground="#00ffcc")
    log_box.pack(fill="both", expand=True, padx=10, pady=10)

    root.mainloop()
