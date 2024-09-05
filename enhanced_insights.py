import requests
import random
from dotenv import load_dotenv
import os
import yfinance as yf
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestClassifier

# Load environment variables from .env file
load_dotenv()

# NewsAPI setup
news_api_key = os.getenv('NEWS_API_KEY')

# Function to fetch stock-related news
def fetch_stock_news(stock_symbol):
    url = f'https://newsapi.org/v2/everything?q={stock_symbol}+finance+stock&apiKey={news_api_key}&language=en'
    response = requests.get(url)
    
    if response.status_code == 200:
        news_data = response.json().get('articles', [])
        return [{"title": article["title"], "url": article["url"]} for article in news_data[:5]]
    else:
        return [{"title": "No relevant news found", "url": "#"}]

# Fetch key financial metrics
def fetch_financial_metrics(stock_symbol):
    stock_symbol = f"{stock_symbol}.NS"
    stock = yf.Ticker(stock_symbol)
    info = stock.info
    
    financial_metrics = {
        'P/E Ratio': info.get('trailingPE', 'N/A'),
        'Price/Book Ratio': info.get('priceToBook', 'N/A'),
        'Dividend Yield': info.get('dividendYield', 'N/A'),
        'Revenue Growth': info.get('revenueGrowth', 'N/A'),
        'Earnings Growth': info.get('earningsGrowth', 'N/A')
    }
    
    return financial_metrics

# Historical returns for 5 years
def fetch_historical_returns(stock_symbol):
    stock = yf.Ticker(f"{stock_symbol}.NS")
    hist = stock.history(period="5y")

    if hist.empty or len(hist['Close']) == 0:
        return 0  # Default value if no data is available
    
    return (hist['Close'][-1] - hist['Close'][0]) / hist['Close'][0] * 100

# Apply ML model for prediction
def apply_ml_model(stock_symbol):
    stock = yf.Ticker(f"{stock_symbol}.NS")
    hist = stock.history(period="5y")
    
    if hist.empty or len(hist['Close']) == 0:
        return "Hold"  # Default if no data

    # Prepare the data for a basic ML model
    X = np.array(range(len(hist['Close']))).reshape(-1, 1)
    y = hist['Close'].values

    if len(X) < 2:  # Not enough data to fit a model
        return "Hold"

    # Linear Regression for future price prediction
    model = LinearRegression()
    model.fit(X, y)

    # Create classification labels: 1 = Buy, 0 = Hold, -1 = Sell
    price_diff = np.diff(y)
    labels = np.zeros_like(price_diff)
    labels[price_diff > 0] = 1
    labels[price_diff < 0] = -1

    # Adjust dataset for classification
    X_adjusted = X[1:]

    clf = RandomForestClassifier()
    clf.fit(X_adjusted, labels)

    recommendation = clf.predict([[len(hist['Close']) + 1]])

    if recommendation == 1:
        return "Buy"
    elif recommendation == -1:
        return "Sell"
    else:
        return "Hold"

# Combine all insights
def fetch_insights(stock_symbol):
    financial_metrics = fetch_financial_metrics(stock_symbol)
    historical_returns = fetch_historical_returns(stock_symbol)
    news = fetch_stock_news(stock_symbol)
    prediction = apply_ml_model(stock_symbol)

    return {
        "financial_metrics": financial_metrics,
        "historical_returns": historical_returns,
        "prediction": prediction,
        "news": news
    }
