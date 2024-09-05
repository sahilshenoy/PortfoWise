from kiteconnect import KiteConnect
import os

# Load the saved access token
with open("access_token.txt", "r") as f:
    access_token = f.read().strip()

# Replace with your actual API key
api_key = os.getenv("API_KEY")

# Initialize KiteConnect with API key
kite = KiteConnect(api_key=api_key)

# Set the access token
kite.set_access_token(access_token)

# Function to fetch real-time stock data
def fetch_stock_data(symbol):
    data = kite.ltp(f"NSE:{symbol}")
    return data

# Fetch data for a specific stock (e.g., Reliance)
if __name__ == "__main__":
    symbol = "RELIANCE"
    stock_data = fetch_stock_data(symbol)
    print(f"Real-time data for {symbol}: {stock_data}")
