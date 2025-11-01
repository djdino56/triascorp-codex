import { ChartPlaceholder } from '@/components/chart-placeholder';
import { ParametersForm } from '@/components/parameters-form';
import { ResultsTable } from '@/components/results-table';

export default function DashboardPage() {
  return (
    <section style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      <header style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        <h1 style={{ fontSize: '2.5rem', margin: 0 }}>Backtesting Control Center</h1>
        <p style={{ color: 'rgba(226, 232, 240, 0.8)', maxWidth: '48rem' }}>
          Configure Deribit spot strategies, trigger new simulations, and inspect performance
          summaries. The widgets below are wired for integrating live metrics once the backend
          REST endpoints are available.
        </p>
      </header>

      <div className="card-grid">
        <ParametersForm />
        <div className="card">
          <h2>Strategy Metrics</h2>
          <div className="placeholder">
            <strong>Performance Snapshot</strong>
            <span>
              Surface aggregated metrics such as total trades, win rate, and final balance pulled
              from the Python engine.
            </span>
          </div>
        </div>
      </div>

      <div className="card">
        <ChartPlaceholder />
      </div>

      <ResultsTable />
    </section>
  );
}
