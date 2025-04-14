import json
import os
import urllib.request

# URLs to download the data
NFO_URL = "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"
MCX_URL = "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster_MCX.json"

# Directory to store the downloaded data
DATA_DIR = os.path.join(os.path.dirname(__file__), "../data")
os.makedirs(DATA_DIR, exist_ok=True)

# Paths to save the downloaded data
NFO_PATH = os.path.join(DATA_DIR, "OpenAPIScripMaster.json")
MCX_PATH = os.path.join(DATA_DIR, "OpenAPIScripMaster_MCX.json")

def download_master_contract():
    print("🔄 Downloading master contract...")
    urllib.request.urlretrieve(NFO_URL, NFO_PATH)
    urllib.request.urlretrieve(MCX_URL, MCX_PATH)
    print("✅ Master contract downloaded.")

def load_symbol_data():
    # Download the files if they don't exist
    if not os.path.exists(NFO_PATH) or not os.path.exists(MCX_PATH):
        download_master_contract()

    # Read the data from the downloaded files
    with open(NFO_PATH, "r") as f1, open(MCX_PATH, "r") as f2:
        data_nfo = json.load(f1)
        data_mcx = json.load(f2)
        return data_nfo + data_mcx  # Combine both NFO and MCX data

def find_symbol_token(symbol_name):
    symbol_name = symbol_name.upper().strip()  # Normalize the symbol to uppercase and remove spaces
    all_symbols = load_symbol_data()

    # Loop through the symbols and find the matching symbol
    for item in all_symbols:
        # Check if the 'Trading Symbol' key exists and matches the input symbol name
        if "Trading Symbol" in item and item["Trading Symbol"] == symbol_name:
            # Return the 'Token' and 'Exch' fields from the matched item
            return item["Token"], item["Exch"]

    return None, None  # Return None if no matching symbol is found
