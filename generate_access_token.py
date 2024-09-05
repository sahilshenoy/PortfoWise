from kiteconnect import KiteConnect
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

api_key = os.getenv("API_KEY")
api_secret = os.getenv("API_SECRET")
access_token_file = "access_token.txt"

kite = KiteConnect(api_key=api_key)

# Function to save access token to file
def save_access_token(token):
    with open(access_token_file, "w") as f:
        f.write(token)

# Function to load access token from file
def load_access_token():
    if os.path.exists(access_token_file):
        with open(access_token_file, "r") as f:
            return f.read().strip()
    return None

# Try to load access token
access_token = load_access_token()

if not access_token:
    # If access token is not available, generate it manually
    print(f"Visit this URL to get the request token: {kite.login_url()}")
    request_token = input("Enter the request token: ")

    # Generate access token using request token and API secret

    data = kite.generate_session(request_token, api_secret=api_secret)
    access_token = data["access_token"]
    save_access_token(access_token)
    print("Access token generated and saved successfully.")
else:
    print("Access token loaded from file.")

# Set the access token in the KiteConnect instance
kite.set_access_token(access_token)

# Now you can use the KiteConnect instance to make API calls
