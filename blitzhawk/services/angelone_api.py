import requests
from datetime import datetime
import json

# Constants
BASE_URL = "https://api.angelbroking.com"
LTP_URL = f"{BASE_URL}/webapi/ltp"
TOKEN_URL = f"{BASE_URL}/webapi/v1/login"
API_KEY = "your_api_key"
CLIENT_CODE = "your_client_code"
SECRET_KEY = "your_secret_key"
ACCESS_TOKEN = "your_access_token"
EXPIRED_TOKEN = "expired_token"

# Authentication Headers
def get_auth_headers():
    headers = {
        'X-API-KEY': API_KEY,
        'X-CLIENT-CODE': CLIENT_CODE,
        'X-SECRET-KEY': SECRET_KEY,
        'Authorization': f"Bearer {ACCESS_TOKEN}",
    }
    return headers

# Refresh Token
def refresh_token():
    payload = {
        "clientCode": CLIENT_CODE,
        "secretKey": SECRET_KEY
    }
    try:
        response = requests.post(TOKEN_URL, json=payload)
        data = response.json()
        if response.status_code == 200 and data.get("status") == "success":
            new_token = data.get("data", {}).get("accessToken")
            if new_token:
                global ACCESS_TOKEN
                ACCESS_TOKEN = new_token
                return ACCESS_TOKEN
            else:
                return None
    except Exception as e:
        print(f"[ERROR] Error refreshing token: {e}")
    return None

# Get LTP
def get_ltp(symboltoken, exchange):
    payload = {
        "symboltoken": symboltoken,
        "exchange": exchange
    }
    try:
        response = requests.post(LTP_URL, json=payload, headers=get_auth_headers(), timeout=5)
        data = response.json()
        if data.get("status") == True:
            return float(data["data"]["ltp"])
        else:
            raise Exception(f"LTP Error: {data}")
    except Exception as e:
        print(f"[ERROR] Error placing order: {str(e)}")
        return None
