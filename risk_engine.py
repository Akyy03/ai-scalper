import pandas as pd

def evaluate_signal_and_risk(df: pd.DataFrame, portfolio_value: float = 100000.0, risk_per_trade: float = 0.01) -> dict:
    if len(df) < 21:
        return {'signal': 'HOLD', 'reason': 'Insufficient candles', 'entry_price': 0.0, 'stop_loss': 0.0, 'take_profit': 0.0, 'shares': 0}

    last_row = df.iloc[-1]
    prev_row = df.iloc[-2]

    price = float(last_row['close'])
    ema9 = float(last_row['EMA_9'])
    ema21 = float(last_row['EMA_21'])
    rsi = float(last_row['RSI_14'])
    atr = float(last_row['ATR_14'])

    prev_ema9 = float(prev_row['EMA_9'])
    prev_ema21 = float(prev_row['EMA_21'])

    signal = 'HOLD'
    reason = 'No technical setup'

    # 1-Minute Scalping Logic
    if (prev_ema9 <= prev_ema21 and ema9 > ema21 and rsi > 48) or (price > ema9 and ema9 > ema21 and rsi > 52):
        signal = 'BUY'
        reason = 'Bullish 1M momentum & EMA alignment'
    elif (prev_ema9 >= prev_ema21 and ema9 < ema21 and rsi < 52) or (price < ema9 and ema9 < ema21 and rsi < 48):
        signal = 'SELL'
        reason = 'Bearish 1M momentum & EMA breakdown'

    if signal == 'HOLD':
        return {
            'signal': 'HOLD',
            'reason': 'Market consolidating on 1M timeframe',
            'entry_price': price,
            'stop_loss': 0.0,
            'take_profit': 0.0,
            'shares': 0
        }

    # Dynamic ATR Stop-Loss & Take-Profit
    stop_distance = max(1.5 * atr, price * 0.003)
    if signal == 'BUY':
        stop_loss = round(price - stop_distance, 2)
        take_profit = round(price + (1.5 * stop_distance), 2)
    else:
        stop_loss = round(price + stop_distance, 2)
        take_profit = round(price - (1.5 * stop_distance), 2)

    # Position Sizing
    max_risk_amount = portfolio_value * risk_per_trade
    risk_per_share = abs(price - stop_loss)
    shares_by_risk = int(max_risk_amount / risk_per_share) if risk_per_share > 0 else 1

    max_capital_allowed = portfolio_value * 0.15
    shares_by_capital = int(max_capital_allowed / price)

    shares = max(1, min(shares_by_risk, shares_by_capital))

    return {
        'signal': signal,
        'reason': reason,
        'entry_price': price,
        'stop_loss': stop_loss,
        'take_profit': take_profit,
        'shares': shares
    }
