import os
from dotenv import load_dotenv
from alpaca.trading.client import TradingClient

load_dotenv()

api_key = os.getenv('ALPACA_API_KEY_ID')
secret_key = os.getenv('ALPACA_SECRET_KEY')

trading_client = TradingClient(api_key, secret_key, paper=True)

account = trading_client.get_account()
print(f'Status Cont Alpaca: {account.status}')
print(f'Buying Power (Capital Virtual): ')
