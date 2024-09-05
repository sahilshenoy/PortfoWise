import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Retrieve the News API key from the environment variable
news_api_key = os.getenv("NEWS_API_KEY")

def fetch_stock_news(stock_symbol):
    url = f"https://newsapi.org/v2/everything?q={stock_symbol}&apiKey={news_api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        news_data = response.json().get('articles', [])
        return news_data
    else:
        print(f"Error fetching news for {stock_symbol}: {response.status_code}")
        return []

if __name__ == "__main__":
    symbol = "HDFCBANK"  # Example symbol
    news = fetch_stock_news(symbol)
    print(news)  # Test fetching news
