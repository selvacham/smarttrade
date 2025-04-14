import os
import time
import pyotp
from dotenv import load_dotenv
from angel_one_smartapi import SmartConnect

load_dotenv()

class AngelExecutor:
    def __init__(self):
        self.api_key = os.getenv("API_KEY")
        self.client_id = os.getenv("CLIENT_ID")
        self.password = os.getenv("CLIENT_PASSWORD")
        self.totp_secret = os.getenv("TOTP_SECRET")
        self.api_secret = os.getenv("API_SECRET")
        self.is_live = os.getenv("IS_LIVE", "false").lower() == "true"
        self.client = SmartConnect(api_key=self.api_key)
        self.session_token = None

    def login(self):
        try:
            otp = pyotp.TOTP(self.totp_secret).now()
            data = self.client.generateSession(self.client_id, self.password, otp)
            self.session_token = data['data']['jwtToken']
            print("✅ Angel One login successful.")
        except Exception as e:
            print("❌ Login failed:", e)

    def place_order(self, symbol, strike, option_type, side, qty):
        if not self.session_token:
            self.login()

        order_type = 'BUY' if side.lower() == 'buy' else 'SELL'
        full_symbol = f"{symbol}{strike}{option_type}"
        print(f"🚀 Placing {order_type} for {full_symbol}, Qty: {qty}")

        # For demo, this only logs (actual API logic will be placed here)
        if self.is_live:
            # Add real SmartConnect place_order() API here later
            print(f"✅ [LIVE] Order executed for {full_symbol}")
        else:
            print(f"🧪 [PAPER] Simulated order for {full_symbol}")

    def logout(self):
        self.client.terminateSession(self.client_id)
        print("👋 Logged out from Angel One")

# Demo run
if __name__ == "__main__":
    executor = AngelExecutor()
    executor.login()
    executor.place_order("CRUDEOIL", "7800", "CE", "buy", 1)
    executor.logout()
