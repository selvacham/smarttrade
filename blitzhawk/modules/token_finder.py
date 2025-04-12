import pandas as pd
import os
import requests
from datetime import datetime, timedelta

INSTRUMENT_URL = "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"
CACHE_FILE = "data/instruments.csv"

class TokenFinder:
    def __init__(self):
        if not os.path.exists(CACHE_FILE) or self.is_cache_old():
            self.download_and_cache_instruments()
        self.df = pd.read_csv(CACHE_FILE)

    def is_cache_old(self):
        try:
            mod_time = os.path.getmtime(CACHE_FILE)
            mod_date = datetime.fromtimestamp(mod_time)
            return datetime.now() - mod_date > timedelta(days=1)
        except:
            return True

    def download_and_cache_instruments(self):
        print("Downloading latest instruments file...")
        response = requests.get(INSTRUMENT_URL)
        data = response.json()
        df = pd.DataFrame(data)
        os.makedirs("data", exist_ok=True)
        df.to_csv(CACHE_FILE, index=False)

    def get_token(self, tradingsymbol, exchange="NFO"):
        try:
            match = self.df[
                (self.df["symbol"] == tradingsymbol) &
                (self.df["exchange"] == exchange)
            ]
            return match.iloc[0]["token"]
        except IndexError:
            return None
