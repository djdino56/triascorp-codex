"""Command line interface for the Deribit backtester."""
from __future__ import annotations

import argparse
import json
import logging
from datetime import datetime
from typing import Any, Dict

from .api import fetch_candles
from .backtest import Backtester
from .config import BacktestConfig

LOGGER = logging.getLogger(__name__)


ISO_FMT = "%Y-%m-%dT%H:%M:%S"


def parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.strptime(value, ISO_FMT)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"Invalid datetime '{value}'. Expected format YYYY-MM-DDTHH:MM:SS"
        ) from exc


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Deribit spot backtester")
    parser.add_argument("instrument", help="Deribit instrument name, e.g. BTC_USDC")
    parser.add_argument("resolution", help="Candle resolution (1, 5, 60, etc.)")
    parser.add_argument("start", nargs="?", type=parse_datetime, help="Start timestamp UTC")
    parser.add_argument("end", nargs="?", type=parse_datetime, help="End timestamp UTC")
    parser.add_argument("--initial-cash", type=float, default=1000.0, help="Initial balance")
    parser.add_argument(
        "--max-open-positions",
        type=int,
        default=1,
        help="Maximum number of simultaneous long positions",
    )
    parser.add_argument("--take-profit", type=float, default=0.03, help="Take profit target as decimal")
    parser.add_argument("--stop-loss", type=float, default=0.02, help="Stop loss as decimal")
    parser.add_argument("--short-window", type=int, default=9, help="Fast moving average window")
    parser.add_argument("--long-window", type=int, default=21, help="Slow moving average window")
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging")
    parser.add_argument(
        "--export-trades",
        type=str,
        default=None,
        help="Optional path to write executed trades as JSON",
    )
    return parser


def run_from_args(args: argparse.Namespace) -> Dict[str, Any]:
    config = BacktestConfig(
        instrument_name=args.instrument,
        interval=args.resolution,
        start=args.start,
        end=args.end,
        initial_cash=args.initial_cash,
        max_open_positions=args.max_open_positions,
        take_profit=args.take_profit,
        stop_loss=args.stop_loss,
        short_window=args.short_window,
        long_window=args.long_window,
    )

    backtester = Backtester(config)
    candles = fetch_candles(
        instrument_name=config.instrument_name,
        resolution=config.interval,
        start=config.start,
        end=config.end,
    )

    report = backtester.run(candles)
    summary = {
        "instrument": config.instrument_name,
        "interval": config.interval,
        "total_trades": report.total_trades,
        "wins": report.wins,
        "losses": report.losses,
        "win_rate": report.win_rate,
        "cumulative_profit": report.cumulative_profit,
        "final_cash": report.final_cash,
    }

    if args.export_trades:
        with open(args.export_trades, "w", encoding="utf-8") as handle:
            json.dump(
                [
                    {
                        "entry_time": trade.position.entry_time.isoformat(),
                        "entry_price": trade.position.entry_price,
                        "exit_time": trade.position.exit_time.isoformat()
                        if trade.position.exit_time
                        else None,
                        "exit_price": trade.position.exit_price,
                        "profit": trade.profit,
                    }
                    for trade in report.trades
                ],
                handle,
                indent=2,
            )

    return summary


def main(argv: list[str] | None = None) -> None:
    parser = create_parser()
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    summary = run_from_args(args)
    for key, value in summary.items():
        LOGGER.info("%s: %s", key, value)


if __name__ == "__main__":
    main()
