import type { BacktestReport } from '@/types/backtest';

const sampleReport: BacktestReport = {
  trades: [
    {
      profit: 125.5,
      position: {
        entryPrice: 40000,
        exitPrice: 41250,
        entryTime: '2024-01-01T00:00:00Z',
        exitTime: '2024-01-03T00:00:00Z',
        size: 1,
        takeProfit: 40800,
        stopLoss: 39200
      }
    }
  ],
  finalCash: 2625.5,
  wins: 1,
  losses: 0
};

export function ResultsTable() {
  const { trades } = sampleReport;

  return (
    <div className="card">
      <h2>Latest Results</h2>
      <table className="table-placeholder">
        <thead>
          <tr>
            <th>Entry</th>
            <th>Exit</th>
            <th>Profit</th>
          </tr>
        </thead>
        <tbody>
          {trades.map((trade, index) => (
            <tr key={index}>
              <td>
                <div>{trade.position.entryTime}</div>
                <span style={{ fontSize: '0.75rem', color: 'rgba(148, 163, 184, 0.9)' }}>
                  @ {trade.position.entryPrice?.toLocaleString()}
                </span>
              </td>
              <td>
                <div>{trade.position.exitTime}</div>
                <span style={{ fontSize: '0.75rem', color: 'rgba(148, 163, 184, 0.9)' }}>
                  @ {trade.position.exitPrice?.toLocaleString()}
                </span>
              </td>
              <td style={{ color: trade.profit >= 0 ? '#4ade80' : '#f87171' }}>
                {trade.profit.toFixed(2)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
