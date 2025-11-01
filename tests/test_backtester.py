from datetime import datetime, timedelta

from backtester.backtest import Backtester
from backtester.config import BacktestConfig
from backtester.models import Candle


def make_candles(start: datetime, closes: list[float]) -> list[Candle]:
    candles = []
    current = start
    for close in closes:
        candles.append(
            Candle(
                timestamp=current,
                open=close,
                high=close,
                low=close,
                close=close,
                volume=1.0,
            )
        )
        current += timedelta(minutes=1)
    return candles


def test_backtester_executes_trade_and_updates_cash():
    config = BacktestConfig(
        instrument_name="TEST_USD",
        interval="1",
        initial_cash=1000.0,
        max_open_positions=1,
        take_profit=0.02,
        stop_loss=0.05,
        short_window=3,
        long_window=5,
    )

    backtester = Backtester(config)
    candles = make_candles(
        start=datetime(2024, 1, 1),
        closes=[14, 13, 12, 11, 10, 11, 12, 13, 14, 15],
    )

    report = backtester.run(candles)

    assert report.total_trades == 1
    trade = report.trades[0]
    assert trade.profit > 0
    assert report.final_cash > config.initial_cash
