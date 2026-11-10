import os
from pathlib import Path
from dotenv import load_dotenv
from alpaca.data.historical import StockHistoricalDataClient, CryptoHistoricalDataClient
from alpaca.data.requests import StockBarsRequest, CryptoBarsRequest
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
import pandas as pd

env_path = Path(__file__).resolve().parent / '.env'
load_dotenv(dotenv_path=env_path)

def get_stock_bars(symbol: str, timeframe: TimeFrame = TimeFrame(1, TimeFrameUnit.Minute), limit: int = 60, asset_class: str = "us_equity") -> pd.DataFrame:
    api_key = os.getenv('ALPACA_API_KEY')
    secret_key = os.getenv('ALPACA_SECRET_KEY')

    if not api_key or not secret_key:
        raise ValueError(f"Missing Alpaca API credentials in market_data.py! Path checked: {env_path}")

    if asset_class == "crypto":
        data_client = CryptoHistoricalDataClient(api_key, secret_key)
        request_params = CryptoBarsRequest(
            symbol_or_symbols=symbol,
            timeframe=timeframe,
            limit=limit
        )
        bars = data_client.get_crypto_bars(request_params)
    else:
        data_client = StockHistoricalDataClient(api_key, secret_key)
        request_params = StockBarsRequest(
            symbol_or_symbols=symbol,
            timeframe=timeframe,
            limit=limit
        )
        bars = data_client.get_stock_bars(request_params)

    df = bars.df

    if isinstance(df.index, pd.MultiIndex):
        df = df.xs(symbol, level='symbol')

    return df