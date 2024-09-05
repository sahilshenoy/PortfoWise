from save_portfolio_to_db import Portfolio, session
from fetch_historical_data import fetch_historical_data, fetch_dividend_info, fetch_earnings_info, save_historical_data
import boto3
from datetime import datetime

# AWS SES Configuration for sending email alerts
ses_client = boto3.client('ses', region_name='your-region')

# Function to send emails
def send_email(subject, body):
    response = ses_client.send_email(
        Source='PortfoWise-LT@padhovit.com',
        Destination={'ToAddresses': ['sahilshenoy3@gmail.com', 'sanjith.shenoy@gmail.com']},
        Message={
            'Subject': {'Data': subject},
            'Body': {'Text': {'Data': body}}
        }
    )
    return response

# Function to check long-term price alerts using saved historical data
def check_long_term_price_alerts():
    portfolio = session.query(Portfolio).all()
    alerts = []
    
    for stock in portfolio:
        # Fetch historical data from Yahoo Finance
        historical_data = fetch_historical_data(stock.symbol)
        save_historical_data(stock.symbol, historical_data)

        # Get the current price and average price over the past year
        current_price = historical_data['Close'].iloc[-1]  # Most recent closing price
        avg_price = historical_data['Close'].mean()  # Average closing price over the past year
        
        # Set a threshold for long-term price increase or decrease (e.g., 20%)
        if current_price >= avg_price * 1.2:
            alerts.append(f"{stock.symbol} has increased by 20% or more over the last year!")
        elif current_price <= avg_price * 0.8:
            alerts.append(f"{stock.symbol} has decreased by 20% or more over the last year!")
    
    return alerts

# Function to check dividend announcements using YFinance
def check_dividend_alerts():
    portfolio = session.query(Portfolio).all()
    alerts = []
    
    for stock in portfolio:
        dividends = fetch_dividend_info(stock.symbol)
        if not dividends.empty and dividends[-1] > 0:  # Check if there are recent dividends
            alerts.append(f"{stock.symbol} has announced a dividend of {dividends[-1]}")
    
    return alerts

# Function to check earnings reports using net income from the income statement
def check_earnings_alerts():
    portfolio = session.query(Portfolio).all()
    alerts = []
    
    for stock in portfolio:
        income_stmt = fetch_earnings_info(stock.symbol)
        if not income_stmt.empty:
            latest_earnings = income_stmt.iloc[-1]
            alerts.append(f"{stock.symbol} net income: {latest_earnings['Net Income']}")
    
    return alerts

if __name__ == "__main__":
    # Price, dividend, and earnings alerts
    price_alerts = check_long_term_price_alerts()
    dividend_alerts = check_dividend_alerts()
    earnings_alerts = check_earnings_alerts()

    alerts = price_alerts + dividend_alerts + earnings_alerts
    if alerts:
        body = "\n".join(alerts)
        send_email("Long-Term Stock Alerts", body)
        print("Alerts sent.")
    else:
        print("No alerts triggered.")
