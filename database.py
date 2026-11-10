import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    # Folosește host-ul definit în Docker compose/env (trading-db), altfel fallback pe localhost
    db_host = os.getenv('POSTGRES_HOST', 'trading-db')
    return psycopg2.connect(
        host=db_host,
        port=5432,
        dbname=os.getenv('POSTGRES_DB', 'trading_db'),
        user=os.getenv('POSTGRES_USER', 'trader'),
        password=os.getenv('POSTGRES_PASSWORD', 'TradingPassword2026!')
    )

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Tabela actualizata: suporta actiuni si crypto (shares si preturi cu zecimale flexibile)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trading_signals (
            id SERIAL PRIMARY KEY,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            symbol VARCHAR(20) NOT NULL,
            price NUMERIC(14, 4),
            ema_9 NUMERIC(14, 4),
            ema_21 NUMERIC(14, 4),
            rsi_14 NUMERIC(10, 2),
            atr_14 NUMERIC(12, 4),
            risk_signal VARCHAR(10),
            risk_reason TEXT,
            stop_loss NUMERIC(14, 4),
            take_profit NUMERIC(14, 4),
            shares NUMERIC(12, 6),
            market_analyst_ai TEXT,
            strategy_ai TEXT,
            executed BOOLEAN DEFAULT FALSE
        );
    ''')
    
    conn.commit()
    cursor.close()
    conn.close()
    print("PostgreSQL database tables initialized successfully.")

def log_trade_signal(data: dict):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = '''
        INSERT INTO trading_signals 
        (symbol, price, ema_9, ema_21, rsi_14, atr_14, risk_signal, risk_reason, stop_loss, take_profit, shares, market_analyst_ai, strategy_ai, executed)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    '''
    
    cursor.execute(query, (
        data['symbol'],
        data['price'],
        data['ema_9'],
        data['ema_21'],
        data['rsi_14'],
        data['atr_14'],
        data['risk_signal'],
        data['risk_reason'],
        data['stop_loss'],
        data['take_profit'],
        data['shares'],
        data['market_analyst_ai'],
        data['strategy_ai'],
        data['executed']
    ))
    
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == '__main__':
    init_db()