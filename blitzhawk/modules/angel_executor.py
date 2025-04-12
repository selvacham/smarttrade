import os
from smartapi import SmartConnect
from dotenv import load_dotenv
from modules.token_finder import TokenFinder

load_dotenv()

class AngelExecutor:
    def __init__(self):
        self.api = SmartConnect(api_key=os.getenv("ANGEL_API_KEY"))
        self.client_code = os.getenv("ANGEL_CLIENT_CODE")
        self.password = os.getenv("ANGEL_PASSWORD")
        self.totp = os.getenv("ANGEL_TOTP")
        self.token_finder = TokenFinder()

    def login(self):
        try:
            data = self.api.generateSession(self.client_code, self.password, self.totp)
            self.auth_token = data['data']['jwtToken']
            self.refresh_token = data['data']['refreshToken']
            print("Angel One Login Successful.")
            return True
        except Exception as e:
            print("Login Failed:", e)
            return False

    def place_order(self, symbol: str, quantity: int, transaction_type: str, order_type: str = "MARKET"):
        print(f"Placing order for {symbol} - {transaction_type}")
        token = self.token_finder.get_token(symbol)

        if not token:
            print(f"Token not found for {symbol}")
            return False

        order_params = {
            "variety": "NORMAL",
            "tradingsymbol": symbol,
            "symboltoken": str(token),
            "transactiontype": transaction_type,
            "exchange": "NFO",
            "ordertype": order_type,
            "producttype": "INTRADAY",
            "duration": "DAY",
            "price": "0",
            "quantity": quantity
        }

        try:
            order_id = self.api.placeOrder(order_params)
            print(f"Order placed successfully. ID: {order_id}")
            return order_id
        except Exception as e:
            print("Order Failed:", e)
            return False
