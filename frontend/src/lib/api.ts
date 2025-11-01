import type {
  BacktestConfig,
  BacktestRequestBody,
  BacktestResponseBody,
  Candle
} from '@/types/backtest';

export interface CandlesRequest {
  instrumentName: string;
  interval: string;
  start?: string | null;
  end?: string | null;
}

export interface CandlesResponse {
  candles: Candle[];
}

function toQueryParams({ instrumentName, interval, start, end }: CandlesRequest): string {
  const params = new URLSearchParams({
    instrument_name: instrumentName,
    resolution: interval
  });

  if (start) {
    params.set('start', start);
  }
  if (end) {
    params.set('end', end);
  }

  return params.toString();
}

function normalizeCandles(payload: unknown): Candle[] {
  if (!payload) {
    return [];
  }

  if (Array.isArray(payload)) {
    return payload as Candle[];
  }

  if (typeof payload === 'object') {
    const candidate = payload as Record<string, unknown>;
    const maybeCandles = candidate.candles;
    if (Array.isArray(maybeCandles)) {
      return maybeCandles as Candle[];
    }
  }

  return [];
}

export async function fetchCandlesForConfig(config: BacktestConfig): Promise<Candle[]> {
  const query = toQueryParams({
    instrumentName: config.instrumentName,
    interval: config.interval,
    start: config.start,
    end: config.end
  });

  const response = await fetch(`/api/candles?${query}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch candles (${response.status})`);
  }

  const data = await response.json();
  return normalizeCandles(data).map((candle) => ({
    ...candle,
    open: Number(candle.open),
    high: Number(candle.high),
    low: Number(candle.low),
    close: Number(candle.close),
    volume: Number(candle.volume)
  }));
}

export async function runBacktest(
  payload: BacktestRequestBody
): Promise<BacktestResponseBody> {
  const response = await fetch('/api/backtest', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    throw new Error(`Backtest failed (${response.status})`);
  }

  return (await response.json()) as BacktestResponseBody;
}
