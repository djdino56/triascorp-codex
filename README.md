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
