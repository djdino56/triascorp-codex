"""Backtesting engine for Deribit spot candles."""
from __future__ import annotations

import math
from typing import Iterable, List

from .config import BacktestConfig
from .models import BacktestReport, Candle, Position, TradeResult
from .strategy import crossover, simple_moving_average


class Backtester:
    """Run a moving-average crossover backtest on Deribit candles."""

    def __init__(self, config: BacktestConfig):
        self.config = config
        self.config.validate()

    def run(self, candles: Iterable[Candle]) -> BacktestReport:
        cash = self.config.initial_cash
        open_positions: List[Position] = []
        trades: List[TradeResult] = []

        candles_list = list(candles)
        closing_prices = [candle.close for candle in candles_list]
        if not closing_prices:
            return BacktestReport(trades=[], final_cash=cash, wins=0, losses=0)

        short_ma = simple_moving_average(closing_prices, self.config.short_window)
        long_ma = simple_moving_average(closing_prices, self.config.long_window)

        for index, candle in enumerate(candles_list):
            # Update stops and exit positions.
            for position in list(open_positions):
                target_profit = position.take_profit
                stop_price = position.stop_loss
                current_price = candle.close

                take_hit = target_profit is not None and current_price >= target_profit
                stop_hit = stop_price is not None and current_price <= stop_price
                if take_hit or stop_hit or index == len(candles_list) - 1:
                    # close position at current price
                    position.exit_price = current_price
                    position.exit_time = candle.timestamp
                    open_positions.remove(position)
                    profit = (position.exit_price - position.entry_price) * position.size
                    trades.append(TradeResult(position=position, profit=profit))
                    cash += profit

            # Evaluate new entries (skip until we have both MAs for current candle)
            if index == 0 or math.isnan(short_ma[index]) or math.isnan(long_ma[index]):
                continue

            previous_index = index - 1
            if math.isnan(short_ma[previous_index]) or math.isnan(long_ma[previous_index]):
                continue

            if len(open_positions) >= self.config.max_open_positions:
                continue

            if crossover(
                previous_short=short_ma[previous_index],
                previous_long=long_ma[previous_index],
                current_short=short_ma[index],
                current_long=long_ma[index],
            ):
                entry_price = candle.close
                position = Position(
                    entry_price=entry_price,
                    entry_time=candle.timestamp,
                    size=1.0,
                    take_profit=entry_price * (1 + self.config.take_profit),
                    stop_loss=entry_price * (1 - self.config.stop_loss),
                )
                open_positions.append(position)

        wins = sum(1 for trade in trades if trade.profit > 0)
        losses = sum(1 for trade in trades if trade.profit <= 0)

        return BacktestReport(trades=trades, final_cash=cash, wins=wins, losses=losses)
