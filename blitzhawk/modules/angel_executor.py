from SmartApi.smartConnect import SmartConnect
import pyotp
import os
from dotenv import load_dotenv

load_dotenv()

class AngelExecutor:
    def __init__(self):
        self.api_key = os.getenv("ANGEL_API_KEY")
        self.client_code = os.getenv("ANGEL_CLIENT_CODE")
        self.pin = os.getenv("ANGEL_PIN")
        self.totp_secret = os.getenv("ANGEL_TOTP_SECRET")
        self.smartapi = SmartConnect(api_key=self.api_key)

    def generate_token(self):
        totp = pyotp.TOTP(self.totp_secret).now()
        data = self.smartapi.generateSession(self.client_code, self.pin, totp)
        return data

    def place_order(self, symbol, strike_price, side, quantity, product_type="INTRADAY"):
        order_type = "BUY" if side == "CE" else "SELL"
        order = self.smartapi.placeOrder({
            "variety": "NORMAL",
            "tradingsymbol": symbol,
            "symboltoken": "UNIQUE_TOKEN",  # Will map from instrument
            "transactiontype": order_type,
            "exchange": "NFO",
            "ordertype": "MARKET",
            "producttype": product_type,
            "duration": "DAY",
            "price": 0,
            "quantity": quantity
        })
        return order
