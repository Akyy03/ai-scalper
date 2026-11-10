import { Component, OnInit, OnDestroy, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TradingService } from './service/trading';
import { AssetOption } from './models/signal';
import { ActivatedRoute, Router } from '@angular/router';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App implements OnInit, OnDestroy {
  public tradingService = inject(TradingService);
  private route = inject(ActivatedRoute);
  private router = inject(Router);

  private refreshInterval: any;

  public availableAssets: AssetOption[] = [
    { symbol: 'NVDA', name: 'NVIDIA Corp.', asset_class: 'us_equity', category: 'Stocks' },
    { symbol: 'AAPL', name: 'Apple Inc.', asset_class: 'us_equity', category: 'Stocks' },
    { symbol: 'TSLA', name: 'Tesla Inc.', asset_class: 'us_equity', category: 'Stocks' },
    { symbol: 'BTC/USD', name: 'Bitcoin', asset_class: 'crypto', category: 'Crypto' },
    { symbol: 'ETH/USD', name: 'Ethereum', asset_class: 'crypto', category: 'Crypto' },
    { symbol: 'SOL/USD', name: 'Solana', asset_class: 'crypto', category: 'Crypto' }
  ];

  // Activul selectat curent (implicit NVDA)
  public selectedAsset = signal<AssetOption>(this.availableAssets[0]);

  ngOnInit(): void {
    // Citim simbolul din URL dacă există la refresh
    this.route.queryParams.subscribe(params => {
      const urlSymbol = params['symbol'];
      const urlAssetClass = params['asset_class'];

      if (urlSymbol) {
        const found = this.availableAssets.find(
          a => a.symbol === urlSymbol && (!urlAssetClass || a.asset_class === urlAssetClass)
        );
        if (found) {
          this.selectedAsset.set(found);
        }
      }
    });

    this.tradingService.fetchTelemetry();
    // Polling silențios din 5 în 5 secunde
    this.refreshInterval = setInterval(() => {
      this.tradingService.fetchTelemetry();
    }, 5000);
  }

  ngOnDestroy(): void {
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval);
    }
  }

  // Schimbă activul selectat din UI și actualizează URL-ul
  onSelectAsset(asset: AssetOption): void {
    this.selectedAsset.set(asset);

    // Sincronizăm parametrii din URL (fără reîncărcarea paginii)
    this.router.navigate([], {
      relativeTo: this.route,
      queryParams: { 
        symbol: asset.symbol, 
        asset_class: asset.asset_class 
      },
      queryParamsHandling: 'merge'
    });
  }

  // Rularea manuală folosește acum activul selectat dinamic
  onManualTrigger(): void {
    const current = this.selectedAsset();
    this.tradingService.triggerManualRun(current.symbol, current.asset_class).subscribe(() => {
      this.tradingService.fetchTelemetry();
    });
  }

  public isAutoMode = signal<boolean>(false);

  toggleAutoMode(): void {
    const newState = !this.isAutoMode();
    this.isAutoMode.set(newState);
    const current = this.selectedAsset();

    this.tradingService.setAutoMode({
      enabled: newState,
      symbol: current.symbol,
      asset_class: current.asset_class,
      execute_trades: false
    }).subscribe({
      next: (res) => console.log('[AUTO-MODE] Updated:', res),
      error: (err) => console.error('[AUTO-MODE ERROR]', err)
    });
  }

}