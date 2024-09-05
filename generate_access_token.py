from kiteconnect import KiteConnect
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

api_key = os.getenv("API_KEY")
api_secret = os.getenv("API_SECRET")

kite = KiteConnect(api_key=api_key)

# Get the request token by manually visiting the following URL and logging in:
print(f"Visit this URL to get the request token: {kite.login_url()}")

# After logging in and authorizing, you'll get a request token in the URL. Use it here:
request_token = input("Enter the request token: ")

# Generate the access token using the request token and API secret
data = kite.generate_session(request_token, api_secret=api_secret)
access_token = data["access_token"]

# Save the access token to a file
with open("access_token.txt", "w") as f:
    f.write(access_token)
