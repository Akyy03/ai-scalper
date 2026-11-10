export interface SystemHealth {
  python_api: 'online' | 'offline' | 'degraded';
  postgres_db: 'connected' | 'disconnected';
  n8n_scheduler: 'active' | 'inactive';
  ollama_agent: 'ready' | 'busy' | 'unreachable';
}

export interface PortfolioBalance {
  total_equity: number;
  available_cash: number;
  daily_pnl: number;
  daily_pnl_percentage: number;
}

export interface TradeSignal {
  id: string;
  symbol: string;
  price: number;
  ema_9: number;
  ema_21: number;
  rsi_14: number;
  atr_14: number;
  risk_signal: 'BUY' | 'SELL' | 'HOLD';
  risk_reason: string;
  stop_loss: number | null;
  take_profit: number | null;
  shares: number | null;
  market_analyst_ai: string;
  strategy_ai: string;
  executed: boolean;
  created_at: string;
}

export interface SignalsResponse {
  signals: TradeSignal[];
  balance?: PortfolioBalance;
  health?: SystemHealth;
}

export type AssetClass = 'us_equity' | 'crypto';

export interface AssetOption {
  symbol: string;
  name: string;
  asset_class: AssetClass;
  category: 'Stocks' | 'Crypto';
}