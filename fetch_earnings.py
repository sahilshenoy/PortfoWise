import yfinance as yf

def fetch_earnings(symbol):
    stock = yf.Ticker(symbol)
    earnings = stock.earnings  # Fetch earnings data
    return earnings

