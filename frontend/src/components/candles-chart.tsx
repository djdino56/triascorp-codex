import type { BacktestPhase, Candle } from '@/types/backtest';

interface CandlesChartProps {
  candles: Candle[];
  phase: BacktestPhase;
  error: string | null;
}

function formatTimestamp(value: string): string {
  try {
    const date = new Date(value);
    return date.toLocaleString();
  } catch (error) {
    return value;
  }
}

export function CandlesChart({ candles, phase, error }: CandlesChartProps) {
  if (error) {
    return (
      <div className="placeholder" role="status">
        <strong>Unable to render chart</strong>
        <span>{error}</span>
      </div>
    );
  }

  if (phase === 'fetchingCandles') {
    return (
      <div className="placeholder" role="status">
        <strong>Loading candles…</strong>
        <span>Fetching market data before starting the backtest.</span>
      </div>
    );
  }

  if (!candles.length) {
    return (
      <div className="placeholder" role="status">
        <strong>No candle data yet</strong>
        <span>Submit the form to load historical candles and render the preview.</span>
      </div>
    );
  }

  const closingPrices = candles.map((candle) => candle.close);
  const timestamps = candles.map((candle) => new Date(candle.timestamp).getTime());

  const minPrice = Math.min(...closingPrices);
  const maxPrice = Math.max(...closingPrices);
  const minTime = Math.min(...timestamps);
  const maxTime = Math.max(...timestamps);

  const padding = 24;
  const width = 600;
  const height = 260;
  const spanPrice = maxPrice - minPrice || 1;
  const spanTime = maxTime - minTime || 1;

  const points = candles
    .map((candle) => {
      const time = new Date(candle.timestamp).getTime();
      const x = padding + ((time - minTime) / spanTime) * (width - padding * 2);
      const y =
        height -
        padding -
        ((candle.close - minPrice) / spanPrice) * (height - padding * 2);

      return `${x},${y}`;
    })
    .join(' ');

  const first = candles[0];
  const last = candles[candles.length - 1];

  return (
    <div className="chart-container">
      <svg
        className="chart"
        viewBox={`0 0 ${width} ${height}`}
        role="img"
        aria-label="Closing price over time"
      >
        <defs>
          <linearGradient id="chartFill" x1="0" x2="0" y1="0" y2="1">
            <stop offset="0%" stopColor="rgba(14, 165, 233, 0.35)" />
            <stop offset="100%" stopColor="rgba(14, 165, 233, 0.05)" />
          </linearGradient>
        </defs>
        <polyline
          fill="none"
          stroke="rgba(14, 165, 233, 0.85)"
          strokeWidth={2.5}
          strokeLinejoin="round"
          strokeLinecap="round"
          points={points}
        />
        <polyline
          fill="url(#chartFill)"
          stroke="none"
          points={`${padding},${height - padding} ${points} ${width - padding},${height - padding}`}
        />
        <g className="chart-axis">
          <text x={padding} y={height - 4}>{minPrice.toFixed(2)}</text>
          <text x={width - padding} y={height - 4} textAnchor="end">
            {maxPrice.toFixed(2)}
          </text>
        </g>
      </svg>
      <div className="chart-meta">
        <div>
          <span className="chart-meta-label">First candle</span>
          <span className="chart-meta-value">{formatTimestamp(first.timestamp)}</span>
        </div>
        <div>
          <span className="chart-meta-label">Last candle</span>
          <span className="chart-meta-value">{formatTimestamp(last.timestamp)}</span>
        </div>
        <div>
          <span className="chart-meta-label">Latest close</span>
          <span className="chart-meta-value">{last.close.toFixed(2)}</span>
        </div>
      </div>
    </div>
  );
}
