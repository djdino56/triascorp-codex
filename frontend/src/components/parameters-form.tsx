'use client';

import { FormEvent } from 'react';
import type { BacktestConfig } from '@/types/backtest';

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

export function ParametersForm() {
  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    const payload = Object.fromEntries(formData.entries());
    console.info('Backtest request', payload);
    // TODO: connect to API via fetch('/api/backtest', { method: 'POST', body: JSON.stringify(...) })
  };

  return (
    <form className="card" onSubmit={handleSubmit}>
      <h2>Configure Backtest</h2>
      <div className="placeholder" style={{ alignItems: 'stretch' }}>
        <span>Wire up inputs here to let users customise the simulation.</span>
        <span>For now the defaults below mirror the Python CLI settings.</span>
      </div>
      <div style={{ display: 'grid', gap: '1rem', marginTop: '1.5rem' }}>
        {Object.entries(defaultConfig).map(([key, value]) => (
          <label key={key} style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            <span style={{ fontSize: '0.85rem', color: 'rgba(226, 232, 240, 0.9)' }}>
              {key.replace(/[A-Z]/g, (match) => ` ${match.toLowerCase()}`)}
            </span>
            <input
              name={key}
              defaultValue={value as string | number}
              style={{
                borderRadius: '8px',
                border: '1px solid rgba(148, 163, 184, 0.4)',
                padding: '0.5rem 0.75rem',
                background: 'rgba(15, 23, 42, 0.65)',
                color: 'inherit'
              }}
            />
          </label>
        ))}
      </div>
      <button
        type="submit"
        style={{
          marginTop: '1.5rem',
          padding: '0.75rem 1.25rem',
          borderRadius: '10px',
          border: 'none',
          background: 'linear-gradient(135deg, #0ea5e9, #6366f1)',
          color: 'white',
          fontWeight: 600,
          cursor: 'pointer'
        }}
      >
        Run Backtest
      </button>
    </form>
  );
}
