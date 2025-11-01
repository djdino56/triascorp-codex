'use client';

import { ChangeEvent, FormEvent, useEffect, useState } from 'react';

import type { BacktestConfig, BacktestPhase } from '@/types/backtest';

const fieldOrder: Array<keyof BacktestConfig> = [
  'instrumentName',
  'interval',
  'start',
  'end',
  'initialCash',
  'maxOpenPositions',
  'takeProfit',
  'stopLoss',
  'shortWindow',
  'longWindow'
];

const numericFields: Array<keyof BacktestConfig> = [
  'initialCash',
  'maxOpenPositions',
  'takeProfit',
  'stopLoss',
  'shortWindow',
  'longWindow'
];

interface ParametersFormProps {
  defaultValues: BacktestConfig;
  phase: BacktestPhase;
  error: string | null;
  onSubmit: (config: BacktestConfig) => void;
}

function toFormState(config: BacktestConfig): Record<string, string> {
  return fieldOrder.reduce<Record<string, string>>((acc, key) => {
    const value = config[key];
    acc[key] = value === undefined || value === null ? '' : String(value);
    return acc;
  }, {});
}

function parseNumber(value: string, fallback: number): number {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : fallback;
}

export function ParametersForm({ defaultValues, phase, error, onSubmit }: ParametersFormProps) {
  const [formValues, setFormValues] = useState<Record<string, string>>(() => toFormState(defaultValues));

  useEffect(() => {
    setFormValues(toFormState(defaultValues));
  }, [defaultValues]);

  const handleChange = (event: ChangeEvent<HTMLInputElement>) => {
    const { name, value } = event.target;
    setFormValues((previous) => ({ ...previous, [name]: value }));
  };

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    const nextConfig: BacktestConfig = {
      instrumentName: formValues.instrumentName || defaultValues.instrumentName,
      interval: formValues.interval || defaultValues.interval,
      start: formValues.start?.trim() ? formValues.start : undefined,
      end: formValues.end?.trim() ? formValues.end : undefined,
      initialCash: parseNumber(formValues.initialCash, defaultValues.initialCash),
      maxOpenPositions: parseInt(formValues.maxOpenPositions, 10) || defaultValues.maxOpenPositions,
      takeProfit: parseNumber(formValues.takeProfit, defaultValues.takeProfit),
      stopLoss: parseNumber(formValues.stopLoss, defaultValues.stopLoss),
      shortWindow: parseInt(formValues.shortWindow, 10) || defaultValues.shortWindow,
      longWindow: parseInt(formValues.longWindow, 10) || defaultValues.longWindow
    };

    onSubmit(nextConfig);
  };

  const isBusy = phase !== 'idle';
  const buttonLabel =
    phase === 'fetchingCandles'
      ? 'Fetching candles…'
      : phase === 'runningBacktest'
        ? 'Running backtest…'
        : 'Run Backtest';

  return (
    <form className="card" onSubmit={handleSubmit} noValidate>
      <h2>Configure Backtest</h2>
      <div className="placeholder" style={{ alignItems: 'stretch' }}>
        <span>Update the parameters below to customise the simulation.</span>
        <span>We retrieve candles first and run the backtest once data is available.</span>
      </div>
      <div className="form-grid">
        {fieldOrder.map((key) => {
          const label = key.replace(/[A-Z]/g, (match) => ` ${match.toLowerCase()}`);
          const isNumeric = numericFields.includes(key);
          const inputType = isNumeric ? 'number' : key === 'start' || key === 'end' ? 'datetime-local' : 'text';

          return (
            <label key={key} className="form-field">
              <span className="form-label">{label}</span>
              <input
                name={key}
                value={formValues[key] ?? ''}
                type={inputType}
                step={isNumeric ? 'any' : undefined}
                onChange={handleChange}
                disabled={isBusy && key !== 'instrumentName' && key !== 'interval'}
              />
            </label>
          );
        })}
      </div>
      {error && (
        <p role="alert" className="form-error">
          {error}
        </p>
      )}
      <button type="submit" className="primary" disabled={isBusy}>
        {buttonLabel}
      </button>
    </form>
  );
}
