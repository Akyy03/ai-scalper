import sys
import time
import os
import math
from dotenv import load_dotenv
from market_data import get_stock_bars
from indicators import add_technical_indicators
from risk_engine import evaluate_signal_and_risk
from ai_agents import market_analyst_agent, strategy_agent
from execution_engine import execute_bracket_order
from database import log_trade_signal
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
from alpaca.trading.client import TradingClient
from alpaca.data.historical import StockHistoricalDataClient, CryptoHistoricalDataClient
from alpaca.data.requests import StockBarsRequest, CryptoBarsRequest

load_dotenv()

def run_trading_pipeline(symbol: str, asset_class: str = "us_equity", execute_trades: bool = True):
    print(f"\n==================================================")
    print(f"   AI TRADING PIPELINE (1M SCALPER) - SYMBOL: {symbol}")
    print(f"==================================================")
    
    api_key = os.getenv('ALPACA_API_KEY')
    secret_key = os.getenv('ALPACA_SECRET_KEY')
    portfolio_equity = 100000.0
    
    if api_key and secret_key:
        try:
            tc = TradingClient(api_key, secret_key, paper=True)
            
            # CHECK MARKET HOURS FIRST (Save Hardware Resources)
            if asset_class == "us_equity":
                clock = tc.get_clock()
                if not clock.is_open:
                    print(f"[MARKET CLOSED] US Market is currently CLOSED. Skipping AI pipeline execution to protect resources.")
                    return
            else:
                print(f"[24/7 MARKET] Asset class '{asset_class}' bypasses US market clock check.")
                
            acc = tc.get_account()
            portfolio_equity = float(acc.equity)
            print(f"[ACCOUNT INFO] Dynamic Equity: {portfolio_equity}")
        except Exception as e:
            print(f"[ACCOUNT INFO WARNING] Failed to verify market hours or equity: {e}")

    # 1. Fetch 1-Minute Market Data
    print(f"\n[STEP 1] Fetching live 1M market data for {symbol} ({asset_class}) from Alpaca Data API...")
    timeframe_1m = TimeFrame(1, TimeFrameUnit.Minute)
    df_raw = get_stock_bars(symbol, timeframe_1m, limit=60, asset_class=asset_class)
    
    # 2. Compute Technical Indicators
    print("[STEP 2] Computing technical indicators (EMA9, EMA21, RSI14, ATR14)...")
    df_tech = add_technical_indicators(df_raw)
    last_row = df_tech.iloc[-1]
    
    tech_summary = {
        'close': round(float(last_row['close']), 2),
        'ema_9': round(float(last_row['EMA_9']), 2),
        'ema_21': round(float(last_row['EMA_21']), 2),
        'rsi': round(float(last_row['RSI_14']), 2),
        'atr': round(float(last_row['ATR_14']), 4)
    }
    
    print(f"   -> Price: {tech_summary['close']} | EMA9: {tech_summary['ema_9']} | EMA21: {tech_summary['ema_21']} | RSI: {tech_summary['rsi']} | ATR: {tech_summary['atr']}")
    
    # 3. Evaluate Risk Engine with DYNAMIC Portfolio Value
    print("\n[STEP 3] Evaluating 1M Scalping Risk Engine & Position Sizing...")
    risk_decision = evaluate_signal_and_risk(df_tech, portfolio_value=portfolio_equity)
    print(f"   -> Risk Signal: {risk_decision['signal']} | Reason: {risk_decision['reason']}")
    print(f"   -> Calculated SL: {risk_decision.get('stop_loss')} | TP: {risk_decision.get('take_profit')} | Max Shares: {risk_decision['shares']}")
    
    # 4. Query AI Agents
    print("\n[STEP 4] Querying AI Agents (Ollama Local)...")
    analyst_output = market_analyst_agent(symbol, tech_summary)
    print(f"\n--- Market Analyst Agent ---\n{analyst_output}")
    
    final_strategy = strategy_agent(symbol, analyst_output, risk_decision)
    print(f"\n--- Strategy Agent ---\n{final_strategy}")
    
    # 5. Order Execution Logic
    executed_flag = False
    print("\n[STEP 5] Final Execution Decision...")
    if risk_decision['signal'] in ['BUY', 'SELL'] and "CONFIRM" in final_strategy.upper():
        if execute_trades:
            print(f"   [EXECUTION] Submitting {risk_decision['signal']} order to Alpaca Paper...")
            order_res = execute_bracket_order(
                symbol=symbol,
                qty=risk_decision['shares'],
                side=risk_decision['signal'],
                stop_loss_price=risk_decision['stop_loss'],
                take_profit_price=risk_decision['take_profit']
            )
            print(f"   [ALPACAS RESULT] {order_res}")
            if "[SUCCESS]" in order_res:
                executed_flag = True
        else:
            print(f"   [DRY-RUN SIMULATION] Signal is {risk_decision['signal']}, but execute_trades=False.")
    else:
        print(f"   [NO ACTION] Position maintained on NEUTRAL / HOLD. No order placed.")

    # 6. Database Logging
    print("\n[STEP 6] Logging execution cycle to PostgreSQL database...")
    
    # Prevenim valori nule/exception de la Ollama
    if not analyst_output or "Ollama exception" in str(analyst_output):
        analyst_output = "Ollama agent offline. Technical metrics evaluated deterministically."

    if not final_strategy or "Ollama exception" in str(final_strategy):
        final_strategy = "Risk engine validated via deterministic rules."

    # Safe extraction pentru pret si indici (prevenim NaN sau None la HOLD)
    raw_price = tech_summary.get('close') or tech_summary.get('price') or 0.0
    current_price = 0.0 if (isinstance(raw_price, float) and math.isnan(raw_price)) else raw_price

    db_payload = {
        'symbol': symbol,
        'price': float(current_price),
        'ema_9': float(tech_summary['ema_9']) if tech_summary.get('ema_9') else 0.0,
        'ema_21': float(tech_summary['ema_21']) if tech_summary.get('ema_21') else 0.0,
        'rsi_14': float(tech_summary['rsi']) if tech_summary.get('rsi') else 0.0,
        'atr_14': float(tech_summary['atr']) if tech_summary.get('atr') else 0.0,
        'risk_signal': risk_decision.get('signal', 'HOLD'),
        'risk_reason': risk_decision.get('reason', 'N/A'),
        'stop_loss': float(risk_decision['stop_loss']) if risk_decision.get('stop_loss') else None,
        'take_profit': float(risk_decision['take_profit']) if risk_decision.get('take_profit') else None,
        'shares': float(risk_decision['shares']) if risk_decision.get('shares') else 0.0,
        'market_analyst_ai': str(analyst_output),
        'strategy_ai': str(final_strategy),
        'executed': executed_flag
    }

    try:
        log_trade_signal(db_payload)
        print("   -> Logged successfully to 'trading_signals' table.")
    except Exception as e:
        print(f"[DB ERROR] Failed to log signal: {e}")

if __name__ == '__main__':
    run_trading_pipeline(symbol='NVDA', execute_trades=True)