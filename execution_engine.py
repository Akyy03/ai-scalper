import os
from pathlib import Path
from dotenv import load_dotenv
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, StopLossRequest, TakeProfitRequest
from alpaca.trading.enums import OrderSide, TimeInForce

# Explicitly resolve .env path from current project root
env_path = Path(__file__).resolve().parent / '.env'
load_dotenv(dotenv_path=env_path)

def execute_bracket_order(symbol: str, qty: int, side: str, stop_loss_price: float, take_profit_price: float):
    api_key = os.getenv('ALPACA_API_KEY')
    secret_key = os.getenv('ALPACA_SECRET_KEY')
    
    if not api_key or not secret_key:
        return f"[EXECUTION ERROR] Missing API Credentials! Environment file not found or empty at: {env_path}"

    trading_client = TradingClient(api_key, secret_key, paper=True)

    try:
        account = trading_client.get_account()
        buying_power = float(account.buying_power)
        
        # SELL Verification: Skip cleanly if no long positions held
        if side.upper() == 'SELL':
            positions = trading_client.get_all_positions()
            held_qty = sum(int(p.qty) for p in positions if p.symbol == symbol)
            if held_qty <= 0:
                return f"[SKIPPED] Cannot SELL {symbol}: No open long positions held in account."
            qty = min(qty, held_qty)

        # BUY Verification: Adjust quantity based on available cash
        if side.upper() == 'BUY':
            order_cost = qty * stop_loss_price
            if order_cost > buying_power:
                qty = max(1, int((buying_power * 0.95) / stop_loss_price))

        order_side = OrderSide.BUY if side.upper() == 'BUY' else OrderSide.SELL

        req = MarketOrderRequest(
            symbol=symbol,
            qty=qty,
            side=order_side,
            time_in_force=TimeInForce.GTC,
            take_profit=TakeProfitRequest(limit_price=take_profit_price),
            stop_loss=StopLossRequest(stop_price=stop_loss_price)
        )

        order = trading_client.submit_order(order_data=req)
        return f"[SUCCESS] Bracket Order submitted for {symbol}: ID {order.id} | Qty: {qty}"

    except Exception as e:
        return f"[EXECUTION ERROR] {str(e)}"
