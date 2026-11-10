import { Injectable, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { TradeSignal, PortfolioBalance, SystemHealth } from '../models/signal';

@Injectable({
  providedIn: 'root'
})
export class TradingService {
  private http = inject(HttpClient);
  private apiUrl = 'http://localhost:8000';

  signals = signal<TradeSignal[]>([]);
  selectedSignal = signal<TradeSignal | null>(null);
  
  balance = signal<PortfolioBalance>({
    total_equity: 0,
    available_cash: 0,
    daily_pnl: 0,
    daily_pnl_percentage: 0
  });

  health = signal<SystemHealth>({
    python_api: 'online',
    postgres_db: 'connected',
    n8n_scheduler: 'active', // Poți lăsa așa sau redenumi în componenta de health
    ollama_agent: 'ready'
  });

  fetchAccountBalance(): void {
    this.http.get<PortfolioBalance>(`${this.apiUrl}/account`).subscribe({
      next: (res) => {
        if (res.total_equity !== undefined) {
          this.balance.set(res);
        }
      },
      error: (err) => console.error('Eroare preluare date Alpaca:', err)
    });
  }

  fetchTelemetry(): void {
    this.fetchAccountBalance();
    this.http.get<{ signals: TradeSignal[] }>(`${this.apiUrl}/signals?limit=30`).subscribe({
      next: (res) => {
        this.signals.set(res.signals || []);
        if (res.signals && res.signals.length > 0 && !this.selectedSignal()) {
          this.selectedSignal.set(res.signals[0]);
        }
      },
      error: () => {
        this.health.update(h => ({ ...h, python_api: 'offline' }));
      }
    });
  }

  triggerManualRun(symbol: string = 'NVDA', assetClass: string = 'us_equity') {
    return this.http.post(`${this.apiUrl}/run-pipeline`, { 
      symbol: symbol, 
      asset_class: assetClass, 
      execute_trades: true 
    });
  }

  // --- ADĂUGAT: Metoda pentru controlul modului automat (nativ Python) ---
  setAutoMode(config: { enabled: boolean; symbol: string; asset_class: string; execute_trades: boolean }) {
    return this.http.post(`${this.apiUrl}/auto-mode`, config);
  }

  selectTrade(signalItem: TradeSignal): void {
    this.selectedSignal.set(signalItem);
  }
}