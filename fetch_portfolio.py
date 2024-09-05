import yfinance as yf
from kiteconnect import KiteConnect
from save_portfolio_to_db import save_portfolio_data
from fetch_historical_data import fetch_historical_data, save_historical_data
from save_portfolio_to_db import Portfolio, session
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Retrieve the API key from the environment variable
api_key = os.getenv("API_KEY")

# Load the saved access token
with open("access_token.txt", "r") as f:
    access_token = f.read().strip()

# Initialize KiteConnect with API key
kite = KiteConnect(api_key=api_key)

# Set the access token
kite.set_access_token(access_token)

# Fetch portfolio data from Kite
def fetch_portfolio():
    portfolio = kite.holdings()
    for item in portfolio:
        symbol = item['tradingsymbol']
        quantity = item['quantity']
        average_price = item['average_price']
        
        
        # Save to the database
        save_portfolio_data(symbol, quantity, average_price)
        
        # Fetch and save historical data
        try:
            hist_data = fetch_historical_data(f'{symbol}.NS')
            save_historical_data(symbol, hist_data)
        except Exception as e:
            print(f"Error fetching historical data for {symbol}: {e}")

# Calculate total portfolio value
def calculate_portfolio_value():
    portfolio = session.query(Portfolio).all()
    total_value = 0
    for stock in portfolio:
        try:
            current_price = kite.ltp(f"NSE:{stock.symbol}")['NSE:'+stock.symbol]['last_price']
            stock_value = stock.quantity * current_price
            total_value += stock_value
        except Exception as e:
            print(f"Error fetching price for {stock.symbol}: {e}")
    return total_value

# Calculate portfolio performance
def calculate_portfolio_performance():
    portfolio = session.query(Portfolio).all()
    performance = {}
    for stock in portfolio:
        try:
            current_price = kite.ltp(f"NSE:{stock.symbol}")['NSE:'+stock.symbol]['last_price']
            initial_price = stock.average_price
            change = (current_price - initial_price) / initial_price * 100
            performance[stock.symbol] = round(change, 2)
        except Exception as e:
            print(f"Error calculating performance for {stock.symbol}: {e}")
    return performance

import time
import requests

def fetch_with_retries(url, retries=3, delay=5):
    for i in range(retries):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Request failed with status {response.status_code}")
        except Exception as e:
            print(f"Exception during request: {e}")

        print(f"Retrying in {delay} seconds...")
        time.sleep(delay)
    return None

# Run the script
if __name__ == "__main__":
    fetch_portfolio()
    total_value = calculate_portfolio_value()
    performance = calculate_portfolio_performance()
    
    print(f"Total Portfolio Value: {total_value}")
    print("Portfolio Performance:")
    for symbol, change in performance.items():
        print(f"{symbol}: {change}%")
    
