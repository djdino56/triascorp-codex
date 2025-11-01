import type { BacktestPhase, BacktestReport } from '@/types/backtest';

interface ResultsTableProps {
  report: BacktestReport | null;
  phase: BacktestPhase;
}

function formatNumber(value: number, digits = 2): string {
  return Number.isFinite(value) ? value.toFixed(digits) : '-';
}

export function ResultsTable({ report, phase }: ResultsTableProps) {
  if (phase === 'runningBacktest') {
    return (
      <div className="card" role="status">
        <h2>Latest Results</h2>
        <div className="placeholder">
          <strong>Running backtest…</strong>
          <span>We will populate the table as soon as the simulation returns.</span>
        </div>
      </div>
    );
  }

  if (!report || !report.trades.length) {
    return (
      <div className="card">
        <h2>Latest Results</h2>
        <div className="placeholder">
          <strong>No trades yet</strong>
          <span>Once a backtest completes, trade details will appear here.</span>
        </div>
      </div>
    );
  }

  const totalTrades = report.trades.length;
  const winRate = totalTrades ? (report.wins / totalTrades) * 100 : 0;
  const cumulativeProfit = report.trades.reduce((sum, trade) => sum + trade.profit, 0);

  return (
    <div className="card">
      <h2>Latest Results</h2>
      <div className="results-summary">
        <div>
          <span className="results-label">Trades</span>
          <strong>{totalTrades}</strong>
        </div>
        <div>
          <span className="results-label">Wins / Losses</span>
          <strong>
            {report.wins} / {report.losses}
          </strong>
        </div>
        <div>
          <span className="results-label">Win rate</span>
          <strong>{formatNumber(winRate)}%</strong>
        </div>
        <div>
          <span className="results-label">Final cash</span>
          <strong>{formatNumber(report.finalCash)}</strong>
        </div>
        <div>
          <span className="results-label">Cumulative P&L</span>
          <strong className={cumulativeProfit >= 0 ? 'profit' : 'loss'}>
            {formatNumber(cumulativeProfit)}
          </strong>
        </div>
      </div>
      <table className="table">
        <thead>
          <tr>
            <th>Entry</th>
            <th>Exit</th>
            <th>Profit</th>
          </tr>
        </thead>
        <tbody>
          {report.trades.map((trade, index) => (
            <tr key={`${trade.position.entryTime}-${index}`}>
              <td>
                <div>{trade.position.entryTime}</div>
                <span className="table-meta">@ {trade.position.entryPrice.toLocaleString()}</span>
              </td>
              <td>
                <div>{trade.position.exitTime ?? 'Open'}</div>
                <span className="table-meta">
                  {trade.position.exitPrice ? `@ ${trade.position.exitPrice.toLocaleString()}` : '—'}
                </span>
              </td>
              <td className={trade.profit >= 0 ? 'profit' : 'loss'}>{formatNumber(trade.profit)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
