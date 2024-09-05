from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from fetch_news import fetch_stock_news
import time
import yfinance as yf
from save_portfolio_to_db import Portfolio, session
import random
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# AWS SES setup
ses_client = boto3.client('ses', region_name='us-east-1')

app = Flask(__name__)

def send_email(subject, body):
    sender = "PortfoWise@padhovit.com"
    recipient = "sahilshenoy3@gmail.com"
    charset = "UTF-8"
    
    try:
        response = ses_client.send_email(
            Destination={
                'ToAddresses': [recipient],
            },
            Message={
                'Body': {
                    'Text': {
                        'Charset': charset,
                        'Data': body,
                    },
                },
                'Subject': {
                    'Charset': charset,
                    'Data': subject,
                },
            },
            Source=sender,
        )
    except ClientError as e:
        print(f"Error sending email: {e.response['Error']['Message']}")
    else:
        print(f"Email sent! Message ID: {response['MessageId']}")

# Analyzes news sentiment (dummy implementation for now)
def analyze_news_sentiment(news_data):
    return random.choice(["positive", "negative"])

# Fetches Net Income from income statement
def fetch_net_income(symbol):
    stock = yf.Ticker(symbol)
    income_statement = stock.income_stmt  # Fetch Net Income
    if income_statement is not None:
        return income_statement.loc['Net Income'] if 'Net Income' in income_statement else None
    return None

# Suggests rebalancing actions based on news and earnings
def suggest_rebalance(stock_symbol):
    news_data = fetch_stock_news(stock_symbol)
    sentiment = analyze_news_sentiment(news_data)
    
    net_income = fetch_net_income(f"{stock_symbol}.NS")
    
    if sentiment == "negative" and net_income is None:
        return f"Consider reducing exposure to {stock_symbol} due to negative sentiment and lack of recent earnings growth."
    elif sentiment == "positive" and net_income is not None:
        return f"Consider increasing exposure to {stock_symbol} based on positive news and strong earnings."
    else:
        return f"Hold position in {stock_symbol}."

# Performs portfolio rebalancing and sends suggestions via email
def rebalance_portfolio():
    portfolio = session.query(Portfolio).all()
    suggestions = []
    
    for stock in portfolio:
        suggestion = suggest_rebalance(stock.symbol)
        suggestions.append(suggestion)

    body = "\n".join(suggestions)
    
    send_email("Monthly Portfolio Rebalancing Suggestions", body)
    
    return suggestions

# Scheduler setup for monthly email
def setup_scheduler():
    scheduler = BackgroundScheduler()
    
    # Schedule rebalance_portfolio to run on the first day of every month
    scheduler.add_job(rebalance_portfolio, 'cron', day=1, hour=0, minute=0)
    
    # Start the scheduler
    scheduler.start()


if __name__ == "__main__":
    setup_scheduler()  # Set up the monthly email task
    app.run(debug=True)
