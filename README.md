# Deribit Spot Backtester

This project provides a small Python application that downloads candlestick data from the [Deribit TradingView API](https://docs.deribit.com/#public-get_tradingview_chart_data) and backtests a simple moving-average crossover strategy for spot markets.

## Features

- Fetch historical candles for any Deribit spot instrument.
- Configure the candle interval, date range, risk management (take profit & stop loss), and maximum open positions.
- Run a moving average crossover backtest with configurable window sizes.
- Optional trade export to JSON for further analysis.

## Installation

Create a virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

```bash
python -m backtester.cli BTC_USDC 60 2024-01-01T00:00:00 2024-01-07T00:00:00 \
    --initial-cash 2500 \
    --max-open-positions 2 \
    --take-profit 0.04 \
    --stop-loss 0.02 \
    --short-window 9 \
    --long-window 21 \
    --export-trades trades.json
```

The script prints a summary containing:

- Total trades
- Wins and losses
- Win rate
- Cumulative profit
- Final cash balance

Dates are expected in `YYYY-MM-DDTHH:MM:SS` format and interpreted as UTC.

## Running Tests

```bash
pytest
```

## Frontend Development

The repository now includes a TypeScript-based Next.js dashboard in `frontend/` for orchestrating
backtests.

```bash
cd frontend
npm install
npm run dev
```

Key scripts:

- `npm run dev`: start the development server with hot reloading.
- `npm run build`: create an optimized production build.
- `npm run start`: serve the production build.
- `npm run lint`: run ESLint using the same conventions as the backend repository.
- `npm run format`: format the codebase with Prettier (configured with Black-compatible width).

## Running Backend and Frontend Together

1. Start the Python backend (expose REST endpoints under `http://localhost:8000/api`). A small
   standard-library server is bundled with the project:

   ```bash
   python -m backtester.http
   ```

   The server listens on `127.0.0.1:8000` by default. Update the target or port in
   `frontend/next.config.js` if your API lives elsewhere.

2. In another terminal, launch the Next.js frontend:

   ```bash
   cd frontend
   npm run dev
   ```

During development, frontend requests to `/api/*` are transparently proxied to the Python service via
Next.js `rewrites`, letting you call backend REST endpoints without CORS headaches. If you need to run
the frontend against a remote backend (for example in production or when the proxy is unavailable),
set `NEXT_PUBLIC_API_BASE_URL` before starting Next.js and requests will be issued directly against
that host:

```bash
NEXT_PUBLIC_API_BASE_URL="http://localhost:8000" npm run dev
```

## HTTP API

The `backtester.http` module serves two JSON endpoints that the frontend consumes via the Next.js
proxy:

- `GET /api/candles`: accepts query parameters `instrument_name`, `resolution`, and optional `start`
  / `end` ISO-8601 timestamps. Returns a JSON payload containing an array of OHLCV candles.
- `POST /api/backtest`: accepts a JSON body with `config` (matching the frontend form fields) and
  an optional `candles` array. If candles are omitted the backend will fetch them before executing
  the strategy and returning a report with trades, win/loss counts, and balances.
