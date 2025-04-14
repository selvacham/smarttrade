import tkinter as tk
from tkinter import messagebox, scrolledtext
from tkinter import ttk
import time
from threading import Thread

import sys
import os
# Allow imports from parent directories
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.symbol_lookup import find_symbol_token
from services.angelone_api import place_order, refresh_token
from services.angelone_api import get_ltp

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
    log_box.insert(tk.END, message + "\n")
    log_box.see(tk.END)
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

def monitor_prices(log_box):
    while True:
        for order in tracked_orders[:]:
            try:
                ltp = get_ltp(order["symboltoken"], order["exchange"])
                if not ltp:
                    continue

                if (order["action"] == "BUY" and (ltp <= order["sl"] or ltp >= order["target"])) or \
                   (order["action"] == "SELL" and (ltp >= order["sl"] or ltp <= order["target"])): 
                    log(f"[EXIT TRIGGERED 🚨] {order['symbol']} at {ltp}", log_box)
                    exit_action = "SELL" if order["action"] == "BUY" else "BUY"
                    response = place_order(
                        tradingsymbol=order["symbol"],
                        symboltoken=order["symboltoken"],
                        transactiontype=exit_action,
                        exchange=order["exchange"],
                        quantity=order["qty"],
                        is_paper=False
                    )
                    log(f"[AUTO EXIT ✅] {exit_action} {order['symbol']} -> {response.get('message', 'Done')}", log_box)
                    tracked_orders.remove(order)
            except Exception as e:
                log(f"[MONITOR ERROR ⚠️] {e}", log_box)
        time.sleep(3)

def launch_manual_order_ui():
    root = tk.Tk()
    root.title("BlitzHawk - Angel One Manual Execution")
    root.geometry("460x600")
    root.resizable(True, True)

    style = ttk.Style()
    style.configure("TButton", padding=10, relief="flat", background="#3498db", font=("Helvetica", 12, "bold"), width=20)
    style.configure("TLabel", background="#34495e", foreground="#ecf0f1", font=("Helvetica", 10))
    style.configure("TEntry", padding=5, font=("Helvetica", 12), relief="flat")
    style.configure("TOptionMenu", font=("Helvetica", 12))
    style.map("TButton", background=[("active", "#2980b9"), ("pressed", "#1abc9c")])

    canvas = tk.Canvas(root)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")

    frame = tk.Frame(canvas, bg="#34495e", bd=10, relief="solid", padx=10, pady=10)
    canvas.create_window((0, 0), window=frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    def update_scrollregion(event=None):
        canvas.config(scrollregion=canvas.bbox("all"))

    def on_mouse_wheel(event):
        canvas.yview_scroll(-1*(event.delta // 120), "units")

    def on_canvas_click(event):
        canvas.scan_mark(event.x, event.y)

    def on_canvas_drag(event):
        canvas.scan_dragto(event.x, event.y, gain=1)

    canvas.bind_all("<MouseWheel>", on_mouse_wheel)
    canvas.bind("<Button-1>", on_canvas_click)
    canvas.bind("<B1-Motion>", on_canvas_drag)
    frame.bind("<Configure>", update_scrollregion)

    def disable_button():
        place_order_button.config(state="disabled")

    def enable_button():
        place_order_button.config(state="normal")

    def handle_place_order():
        instrument = instrument_var.get()
        tradingsymbol = symbol_entry.get().strip().upper()
        action = action_var.get()
        qty = qty_entry.get().strip()
        sl_value = sl_entry.get().strip()
        target_value = target_entry.get().strip()
        mode = mode_var.get().strip().upper()

        log(f"[DEBUG] Mode selected: {mode}", log_box)

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
            messagebox.showerror("Lookup Failed", "Symbol not found in master contract.")
            return

        if mode == "PAPER":
            log(f"[PAPER TRADE 📝] {action} {tradingsymbol} x{qty} | SL={sl_value}, Target={target_value}", log_box)
            messagebox.showinfo("Paper Trade", "Paper trade simulated.")
            return

        try:
            disable_button()  # Disable the button while processing

            if is_token_expired():
                log("[DEBUG] Token expired, refreshing...", log_box)
                new_token = refresh_token()
                if not new_token:
                    messagebox.showerror("Token Refresh Failed", "Unable to refresh token.")
                    return
                log(f"[DEBUG] New AUTH_TOKEN: {new_token}", log_box)

            response = place_order(
                tradingsymbol=tradingsymbol,
                symboltoken=symboltoken,
                transactiontype=action,
                exchange=exchange,
                quantity=qty,
                is_paper=False
            )

            log(f"[DEBUG] API Response: {response}", log_box)

            if response.get("status") == "success":
                log(f"[LIVE ORDER ✅] {action} {tradingsymbol} x{qty} | SL={sl_value}, Target={target_value}", log_box)
                messagebox.showinfo("Live Order", response.get("message", "Live order placed successfully."))
                if sl_value and target_value:
                    entry_price = get_ltp(symboltoken, exchange)
                    add_to_tracking(tradingsymbol, symboltoken, exchange, action, entry_price, qty, sl_value, target_value, log_box)
                    Thread(target=monitor_prices, args=(log_box,), daemon=True).start()
            else:
                log(f"[LIVE ERROR ❌] {action} {tradingsymbol} -> {response.get('message')}", log_box)
                messagebox.showerror("Order Failed", response.get("message", "Unknown Error"))
        except Exception as e:
            log(f"[EXCEPTION ⚠️] {e}", log_box)
            messagebox.showerror("Exception", str(e))
        finally:
            enable_button()  # Re-enable the button after processing

    # --- UI Components ---
    ttk.Label(frame, text="🛠 Manual Order Execution", style="TLabel").pack(pady=10)

    frame_instrument = tk.Frame(frame, bg="#1abc9c", relief="flat", bd=5, padx=10, pady=10)
    frame_instrument.pack(fill="x", pady=10)
    ttk.Label(frame_instrument, text="--- Instrument & Symbol ---", style="TLabel").pack(pady=5)
    ttk.Label(frame_instrument, text="Instrument", style="TLabel").pack()
    instrument_var = tk.StringVar(value="NIFTY")
    ttk.OptionMenu(frame_instrument, instrument_var, "NIFTY", "BANKNIFTY", "CRUDEOIL").pack(pady=5)

    ttk.Label(frame_instrument, text="Trading Symbol", style="TLabel").pack(pady=5)
    symbol_entry = ttk.Entry(frame_instrument, width=30)
    symbol_entry.pack(pady=5)

    # 🟢 LTP Display
    ltp_var = tk.StringVar(value="LTP: --")
    ltp_label = ttk.Label(frame_instrument, textvariable=ltp_var, style="TLabel")
    ltp_label.pack(pady=5)

    # 🟢 Update LTP function
    def update_ltp(event=None):
        symbol = symbol_entry.get().strip().upper()
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
            ltp_var.set("LTP: Error fetching price")

    symbol_entry.bind("<KeyRelease>", update_ltp)

    # 🟢 Action (BUY/SELL) and Quantity Inputs
    frame_action_qty = tk.Frame(frame, bg="#1abc9c", relief="flat", bd=5, padx=10, pady=10)
    frame_action_qty.pack(fill="x", pady=10)

    ttk.Label(frame_action_qty, text="Action & Quantity", style="TLabel").pack(pady=5)
    action_var = tk.StringVar(value="BUY")
    ttk.OptionMenu(frame_action_qty, action_var, "BUY", "SELL").pack(pady=5)

    ttk.Label(frame_action_qty, text="Quantity", style="TLabel").pack(pady=5)
    qty_entry = ttk.Entry(frame_action_qty, width=30)
    qty_entry.pack(pady=5)

    # 🟢 SL/Target Inputs
    frame_sl_target = tk.Frame(frame, bg="#1abc9c", relief="flat", bd=5, padx=10, pady=10)
    frame_sl_target.pack(fill="x", pady=10)

    ttk.Label(frame_sl_target, text="SL/Target", style="TLabel").pack(pady=5)
    ttk.Label(frame_sl_target, text="Stop Loss (points)", style="TLabel").pack()
    sl_entry = ttk.Entry(frame_sl_target, width=30)
    sl_entry.pack(pady=5)

    ttk.Label(frame_sl_target, text="Target (points)", style="TLabel").pack()
    target_entry = ttk.Entry(frame_sl_target, width=30)
    target_entry.pack(pady=5)

    # 🟢 Mode Selection (Paper/Live)
    mode_var = tk.StringVar(value="LIVE")
    frame_mode = tk.Frame(frame, bg="#1abc9c", relief="flat", bd=5, padx=10, pady=10)
    frame_mode.pack(fill="x", pady=10)

    ttk.Label(frame_mode, text="Order Mode", style="TLabel").pack(pady=5)
    ttk.OptionMenu(frame_mode, mode_var, "LIVE", "PAPER").pack(pady=5)

    # 🟢 Place Order Button
    place_order_button = ttk.Button(frame, text="Place Order", command=handle_place_order)
    place_order_button.pack(pady=10)

    # 🟢 Logs Panel
    log_box = scrolledtext.ScrolledText(frame, height=15, wrap=tk.WORD, state="disabled")
    log_box.pack(fill="both", expand=True)

    root.mainloop()
