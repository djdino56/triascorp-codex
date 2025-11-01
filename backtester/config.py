"""Configuration dataclasses for the Deribit backtester."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class BacktestConfig:
    """Runtime configuration for a backtest.

    Attributes:
        instrument_name: Deribit instrument identifier (e.g. ``BTC_USDC``).
        interval: Candlestick resolution, matching Deribit API options (e.g. ``1``, ``60``).
        start: Inclusive UTC datetime for the candle query.
        end: Exclusive UTC datetime for the candle query.
        initial_cash: Starting account balance in quote currency.
        max_open_positions: Maximum number of simultaneous long positions.
        take_profit: Target profit (as a decimal, e.g. ``0.05`` for 5%).
        stop_loss: Stop loss (as a decimal, e.g. ``0.02`` for 2%).
        short_window: Window size for the fast moving average.
        long_window: Window size for the slow moving average.
    """

    instrument_name: str = "BTC_USDC"
    interval: str = "60"
    start: Optional[datetime] = None
    end: Optional[datetime] = None
    initial_cash: float = 1000.0
    max_open_positions: int = 1
    take_profit: float = 0.03
    stop_loss: float = 0.02
    short_window: int = 9
    long_window: int = 21

    def validate(self) -> None:
        if self.short_window <= 0 or self.long_window <= 0:
            raise ValueError("Moving average windows must be positive integers")
        if self.short_window >= self.long_window:
            raise ValueError("short_window must be less than long_window")
        if self.max_open_positions <= 0:
            raise ValueError("max_open_positions must be greater than zero")
        if not 0 < self.take_profit:
            raise ValueError("take_profit must be positive")
        if not 0 < self.stop_loss:
            raise ValueError("stop_loss must be positive")
        if self.start and self.end and self.start >= self.end:
            raise ValueError("start must be before end")
