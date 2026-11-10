import uvicorn
import threading
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from alpaca.trading.client import TradingClient
from alpaca.data.historical import StockHistoricalDataClient, CryptoHistoricalDataClient
from alpaca.data.requests import StockBarsRequest, CryptoBarsRequest
from alpaca.data.timeframe import TimeFrame
import psycopg2
from psycopg2.extras import RealDictCursor
from apscheduler.schedulers.background import BackgroundScheduler

from main import run_trading_pipeline
from database import init_db

app = FastAPI(
    title="AI Algorithmic Trading API",
    description="REST API with mutex lock for sequential processing of symbols.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

scheduler = BackgroundScheduler()

active_job_config = {
    "symbol": "BTC/USD",
    "asset_class": "crypto",
    "execute_trades": False
}

def scheduled_pipeline_job():
    if not active_job_config.get("enabled", False):
        return  # Dacă auto-mode este oprit, nu facem nimic

    print(f"[AUTO-SCHEDULER] Running automated pipeline for {active_job_config['symbol']}...")
    with pipeline_lock:
        try:
            run_trading_pipeline(
                symbol=active_job_config["symbol"],
                asset_class=active_job_config["asset_class"],
                execute_trades=active_job_config["execute_trades"]
            )
            print(f"[AUTO-SCHEDULER] Successfully processed {active_job_config['symbol']}.")
        except Exception as e:
            print(f"[AUTO-SCHEDULER ERROR] Failed to run pipeline: {e}")

pipeline_lock = threading.Lock()

@app.on_event("startup")
def startup_event():
    try:
        init_db()
        print("[DATABASE] Schema initialized / validated on startup.")
        
        if not scheduler.running:
            scheduler.add_job(
                scheduled_pipeline_job, 
                'interval', 
                minutes=1, 
                id='auto_trading_job',
                replace_existing=True
            )
            scheduler.start()
            print("[SCHEDULER] Background scheduler started with 1-minute interval.")
            
    except Exception as e:
        print(f"[DATABASE ERROR] Failed to initialize DB schema on startup: {e}")

@app.on_event("shutdown")
def shutdown_event():
    if scheduler.running:
        scheduler.shutdown()
        print("[SCHEDULER] Background scheduler shut down.")

class TradeRequest(BaseModel):
    symbol: str = "NVDA"
    asset_class: str = "us_equity"
    execute_trades: bool = False


@app.get("/")
def read_root():
    return {"status": "ONLINE", "system": "AI Stock Trader Engine v1.0"}


@app.get("/account")
def get_account_summary():
    """Aduce datele reale despre balanță și PnL direct din Alpaca Trading Client."""
    try:
        api_key = os.getenv("ALPACA_API_KEY")
        secret_key = os.getenv("ALPACA_SECRET_KEY")
        
        if not api_key or not secret_key:
            raise ValueError("Alpaca API credentials missing in environment.")

        trading_client = TradingClient(api_key, secret_key, paper=True)
        acc = trading_client.get_account()
        
        equity = float(acc.equity)
        last_equity = float(acc.last_equity)
        cash = float(acc.cash)
        pnl = equity - last_equity
        pnl_pct = (pnl / last_equity * 100) if last_equity > 0 else 0.0

        return {
            "total_equity": round(equity, 2),
            "available_cash": round(cash, 2),
            "daily_pnl": round(pnl, 2),
            "daily_pnl_percentage": round(pnl_pct, 2)
        }
    except Exception as e:
        print(f"[API ERROR] Failed to fetch Alpaca account: {e}")
        return {
            "total_equity": 0.0,
            "available_cash": 0.0,
            "daily_pnl": 0.0,
            "daily_pnl_percentage": 0.0,
            "error": str(e)
        }


@app.get("/signals")
def get_signals(limit: int = 30):
    """Interoghează ultimele semnale procesate din baza de date PostgreSQL."""
    try:
        db_host = os.getenv("POSTGRES_HOST", "trading-postgres")
        conn = psycopg2.connect(
            dbname=os.getenv("POSTGRES_DB", "trading_db"),
            user=os.getenv("POSTGRES_USER", "trader"),
            password=os.getenv("POSTGRES_PASSWORD", "TradingPassword2026!"),
            host=db_host,
            port=os.getenv("POSTGRES_PORT", "5432")
        )
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            "SELECT * FROM trading_signals ORDER BY id DESC LIMIT %s;", 
            (limit,)
        )
        records = cursor.fetchall()
        cursor.close()
        conn.close()

        for r in records:
            if 'created_at' in r and r['created_at']:
                r['created_at'] = str(r['created_at'])

        return {"signals": records}
    except Exception as e:
        print(f"[API ERROR] Failed to query signals from DB: {e}")
        return {"signals": [], "error": str(e)}


@app.post("/run-pipeline")
def trigger_pipeline(request: TradeRequest):
    print(f"\n[API TRIGGER] Queued request for symbol: {request.symbol} ({request.asset_class})")
    
    with pipeline_lock:
        try:
            print(f"[LOCK ACQUIRED] Processing symbol: {request.symbol} [{request.asset_class}]")
            run_trading_pipeline(
                symbol=request.symbol, 
                asset_class=request.asset_class, 
                execute_trades=request.execute_trades
            )
            return {
                "status": "COMPLETED",
                "symbol": request.symbol,
                "asset_class": request.asset_class,
                "execute_trades": request.execute_trades,
                "message": f"Successfully processed trading pipeline for {request.symbol}."
            }
        except Exception as e:
            print(f"[PIPELINE ERROR] Execution failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))

class AutoModeRequest(BaseModel):
    enabled: bool
    symbol: str
    asset_class: str
    execute_trades: bool = False

@app.post("/auto-mode")
def set_auto_mode(config: AutoModeRequest):
    """Actualizează configurația pentru rularea automată din minut în minut."""
    global active_job_config
    active_job_config = {
        "enabled": config.enabled,
        "symbol": config.symbol,
        "asset_class": config.asset_class,
        "execute_trades": config.execute_trades
    }
    print(f"[AUTO-MODE UPDATED] Config changed: {active_job_config}")
    return {"status": "SUCCESS", "active_config": active_job_config}

@app.get("/auto-mode")
def get_auto_mode():
    """Returnează starea curentă a modului automat."""
    return active_job_config

if __name__ == '__main__':
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)