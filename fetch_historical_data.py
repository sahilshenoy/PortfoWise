import yfinance as yf
from datetime import datetime
from save_portfolio_to_db import HistoricalPrice, session

# Fetch historical stock prices
def fetch_historical_data(symbol):
    stock = yf.Ticker(symbol)
    hist = stock.history(period="1y")  # Fetch last 1 year data
    print(hist)  # Print fetched data for debugging
    return hist[['Close']].reset_index()

# Save historical stock prices to the database
def save_historical_data(symbol, hist_data):
    for index, row in hist_data.iterrows():
        date = row['Date'].date()
        price = row['Close']
        historical_price_entry = HistoricalPrice(symbol=symbol, date=date, price=price)
        session.add(historical_price_entry)
    session.commit()

# Fetch dividend data for the stock
def fetch_dividend_info(symbol):
    stock = yf.Ticker(symbol)
    dividends = stock.dividends  # Fetch dividend information
    return dividends

# Fetch earnings information using the income statement
def fetch_earnings_info(symbol):
    stock = yf.Ticker(symbol)
    income_statement = stock.income_stmt  # Fetch net income from the income statement
    return income_statement

# Example usage:
if __name__ == "__main__":
    symbol = "HDFCBANK.NS"  # Use NSE ticker symbol for Indian stocks
    
    # Fetch historical data
    historical_data = fetch_historical_data(symbol)
    print("Historical Data:")
    print(historical_data)

    # Fetch dividend data
    dividends = fetch_dividend_info(symbol)
    print("Dividends:")
    print(dividends)

    # Fetch earnings (using income statement)
    earnings = fetch_earnings_info(symbol)
    print("Income Statement (Net Income):")
    print(earnings)
