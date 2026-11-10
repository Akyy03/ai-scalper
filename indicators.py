import pandas as pd
import pandas_ta as ta
from market_data import get_stock_bars
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit

def add_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    data = df.copy()
    
    # Calculate EMA 9 and EMA 21
    data['EMA_9'] = ta.ema(data['close'], length=9)
    data['EMA_21'] = ta.ema(data['close'], length=21)
    
    # Calculate RSI 14
    data['RSI_14'] = ta.rsi(data['close'], length=14)
    
    # Calculate ATR 14
    data['ATR_14'] = ta.atr(data['high'], data['low'], data['close'], length=14)
    
    return data

if __name__ == '__main__':
    symbol = 'NVDA'
    print(f'Calculating technical indicators for {symbol}...')
    timeframe_5m = TimeFrame(5, TimeFrameUnit.Minute)
    df_raw = get_stock_bars(symbol, timeframe_5m, limit=50)
    df_indicators = add_technical_indicators(df_raw)
    print(df_indicators[['close', 'EMA_9', 'EMA_21', 'RSI_14', 'ATR_14']].tail(5))
