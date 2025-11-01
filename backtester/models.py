"""Core data models for the Deribit backtester."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class Candle:
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass
class Position:
    entry_price: float
    entry_time: datetime
    size: float = 1.0
    exit_price: Optional[float] = None
    exit_time: Optional[datetime] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None

    def is_open(self) -> bool:
        return self.exit_price is None


@dataclass
class TradeResult:
    position: Position
    profit: float


@dataclass
class BacktestReport:
    trades: List[TradeResult] = field(default_factory=list)
    final_cash: float = 0.0
    wins: int = 0
    losses: int = 0

    @property
    def total_trades(self) -> int:
        return len(self.trades)

    @property
    def win_rate(self) -> float:
        if not self.trades:
            return 0.0
        return self.wins / len(self.trades)

    @property
    def cumulative_profit(self) -> float:
        return sum(trade.profit for trade in self.trades)
