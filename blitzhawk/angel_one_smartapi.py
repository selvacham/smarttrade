import requests
import json

class AngelOneSmartAPI:
    def __init__(self, api_key, client_code, password, two_factor_password):
        self.api_key = api_key
        self.client_code = client_code
        self.password = password
        self.two_factor_password = two_factor_password
        self.base_url = "https://api.angleone.com"
        self.token = None

    def login(self):
        login_url = f"{self.base_url}/v1/login"
        payload = {
            "api_key": self.api_key,
            "client_code": self.client_code,
            "password": self.password,
            "two_factor_password": self.two_factor_password
        }
        response = requests.post(login_url, json=payload)
        if response.status_code == 200:
            self.token = response.json()["token"]
            return True
        return False

    def place_order(self, symbol, quantity, price, order_type):
        order_url = f"{self.base_url}/v1/place_order"
        headers = {"Authorization": f"Bearer {self.token}"}
        order_data = {
            "symbol": symbol,
            "quantity": quantity,
            "price": price,
            "order_type": order_type
        }
        response = requests.post(order_url, json=order_data, headers=headers)
        return response.json()

    def get_balance(self):
        balance_url = f"{self.base_url}/v1/balance"
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(balance_url, headers=headers)
        return response.json()
