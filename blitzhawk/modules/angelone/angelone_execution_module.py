# angel_execution_module.py

import requests
import json
import datetime

class AngelOneExecutor:
    def __init__(self, api_key, client_code, access_token, is_paper_trade=True):
        self.api_key = api_key
        self.client_code = client_code
        self.access_token = access_token
        self.is_paper_trade = is_paper_trade
        self.base_url = "https://apiconnect.angelbroking.com/rest/secure/angelbroking/order/v1/placeOrder"

        self.headers = {
            "Content-Type": "application/json",
            "X-PrivateKey": self.api_key,
            "X-SourceID": "WEB",
            "X-ClientLocalIP": "127.0.0.1",
            "X-ClientPublicIP": "127.0.0.1",
            "X-MACAddress": "00:00:00:00:00:00",
            "X-UserType": "USER",
            "X-AccessToken": self.access_token,
            "X-ClientCode": self.client_code
        }

    def get_current_market_price(self, symbol):
        # Placeholder: You need an API or function to fetch live market price for Crude Oil.
        # For now, I'll return a mock value. Replace with actual API for real-time price.
        if symbol == "CRUDEOIL":
            return 4300.0  # Example market price for Crude Oil
        else:
            return 0.0

    def get_strike_price(self, symbol, is_call_option=True):
        # Get current market price
        current_price = self.get_current_market_price(symbol)

        if current_price == 0.0:
            print("Invalid symbol or no market data available.")
            return None

        # Calculate nearest ATM strike price
        strike_price = round(current_price / 100) * 100  # Round to nearest 100 for crude oil options

        if is_call_option:
            # Buy Call Option (CE)
            return f"{symbol}{strike_price}CE"
        else:
            # Buy Put Option (PE)
            return f"{symbol}{strike_price}PE"

    def place_order(self, symbol, quantity, transaction_type, order_type="MARKET", variety="NORMAL", product_type="INTRADAY", price=0.0, trigger_price=0.0, is_call_option=True):
        # Get the dynamic strike price based on the symbol (e.g., CRUDEOIL) and whether it's a call or put option
        strike_symbol = self.get_strike_price(symbol, is_call_option)

        if not strike_symbol:
            return {"status": "error", "message": "Failed to get strike price"}

        order_data = {
            "variety": variety,
            "tradingsymbol": strike_symbol,
            "symboltoken": self.get_symbol_token(strike_symbol),
            "transactiontype": transaction_type.upper(),
            "exchange": "NFO",
            "ordertype": order_type,
            "producttype": product_type,
            "duration": "DAY",
            "price": price,
            "squareoff": "0",
            "stoploss": "0",
            "quantity": quantity,
            "triggerprice": trigger_price
        }

        if self.is_paper_trade:
            print("[PAPER TRADE] Order:", json.dumps(order_data, indent=2))
            return {"status": "success", "message": "Paper trade simulated", "order": order_data}
        else:
            print("[LIVE TRADE] Placing order...")
            response = requests.post(self.base_url, headers=self.headers, json=order_data)
            return response.json()

    def get_symbol_token(self, symbol):
        # TODO: Lookup the symbol token from a static file or API if needed
        dummy_tokens = {
            "CRUDEOIL4300CE": "70315",
            "CRUDEOIL4300PE": "70316"
        }
        return dummy_tokens.get(symbol.upper(), "70315")


# Example usage
if __name__ == "__main__":
    executor = AngelOneExecutor(
        api_key="your_api_key",
        client_code="your_client_code",
        access_token="your_access_token",
        is_paper_trade=True  # change to False for live orders
    )

    # Test order with dynamic strike price selection
    response = executor.place_order(
        symbol="CRUDEOIL",  # For example, Crude Oil
        quantity=1,
        transaction_type="BUY",
        is_call_option=True  # Can switch to False for Put option
    )
    print("Order Response:", response)
