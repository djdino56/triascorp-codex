'use client';

import { useState } from 'react';

import { CandlesChart } from '@/components/candles-chart';
import { ParametersForm } from '@/components/parameters-form';
import { ResultsTable } from '@/components/results-table';
import type { BacktestConfig, BacktestPhase, BacktestReport, Candle } from '@/types/backtest';

const defaultConfig: BacktestConfig = {
  instrumentName: 'BTC_USDC',
  interval: '60',
  start: '',
  end: '',
  initialCash: 2500,
  maxOpenPositions: 2,
  takeProfit: 0.04,
  stopLoss: 0.02,
  shortWindow: 9,
  longWindow: 21
};

export function Dashboard() {
  const [phase, setPhase] = useState<BacktestPhase>('idle');
  const [lastConfig, setLastConfig] = useState<BacktestConfig>(defaultConfig);
  const [candles, setCandles] = useState<Candle[]>([]);
  const [report, setReport] = useState<BacktestReport | null>(null);
  const [error, setError] = useState<string | null>(null);

  return (
    <section style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      <header style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        <h1 style={{ fontSize: '2.5rem', margin: 0 }}>Backtesting Control Center</h1>
        <p style={{ color: 'rgba(226, 232, 240, 0.8)', maxWidth: '48rem' }}>
          Configure Deribit spot strategies, trigger new simulations, and inspect performance
          summaries. We first retrieve historical candles and only start the simulation when market
          data is available.
        </p>
      </header>

      <div className="card-grid">
        <ParametersForm
          defaultValues={lastConfig}
          phase={phase}
          error={error}
          onConfigChange={setLastConfig}
          onPhaseChange={setPhase}
          onErrorChange={setError}
          onCandlesChange={setCandles}
          onReportChange={setReport}
        />
        <div className="card">
          <h2>Strategy Metrics</h2>
          <div className="placeholder">
            <strong>Performance Snapshot</strong>
            <span>
              Once the Python API exposes aggregate metrics, surface them here (total trades, win
              rate, drawdown, etc.).
            </span>
          </div>
        </div>
      </div>

      <div className="card">
        <h2>Candle Preview</h2>
        <CandlesChart candles={candles} phase={phase} error={error} />
      </div>

      <ResultsTable report={report} phase={phase} />
    </section>
  );
}
