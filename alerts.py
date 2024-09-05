import yfinance as yf
import boto3
from save_portfolio_to_db import Portfolio, session
from kiteconnect import KiteConnect
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

# Initialize AWS SES client
ses_client = boto3.client('ses', region_name='us-east-1')

def send_email(subject, body):
    response = ses_client.send_email(
        Source='PortfoWise@padhovit.com',
        Destination={
            'ToAddresses': ['sahilshenoy3@gmail.com'],
        },
        Message={
            'Subject': {
                'Data': subject,
            },
            'Body': {
                'Text': {
                    'Data': body,
                },
            },
        }
    )
    print("Email sent! Message ID:", response['MessageId'])


def get_historical_data_yfinance(symbol):
    stock = yf.Ticker(symbol)
    hist = stock.history(period="1y")
    return hist

def check_alerts():
    portfolio = session.query(Portfolio).all()
    alerts = []

    for stock in portfolio:
        current_price = kite.ltp(f"NSE:{stock.symbol}")['NSE:'+stock.symbol]['last_price']

        # 52-Week High/Low Alert using yfinance
        hist_data = get_historical_data_yfinance(f'{stock.symbol}.NS')
        high_52_week = hist_data['Close'].max()
        low_52_week = hist_data['Close'].min()
        if current_price >= high_52_week:
            alerts.append(f"Alert: {stock.symbol} has reached its 52-week high at {current_price}")
        elif current_price <= low_52_week:
            alerts.append(f"Alert: {stock.symbol} has reached its 52-week low at {current_price}")

        # Price Drop Alert 
        peak_price = hist_data['Close'].max()
        if current_price <= peak_price * 0.70:
            alerts.append(f"Alert: {stock.symbol} has dropped 10% from its peak price to {current_price}")
        
        
    if alerts:
        body = "\n".join(alerts)
        send_email("Stock Alerts", body)
        print("Alerts sent via email.")
    else:
        print("No alerts triggered.")

if __name__ == "__main__":
    check_alerts()
