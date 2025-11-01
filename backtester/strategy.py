"""Simple indicator helpers used by the backtester."""
from __future__ import annotations

from collections import deque
from typing import Deque, Iterable, List


def simple_moving_average(values: Iterable[float], window: int) -> List[float]:
    """Calculate a simple moving average for *values* using the provided window."""

    if window <= 0:
        raise ValueError("window must be greater than zero")

    averages: List[float] = []
    acc: Deque[float] = deque(maxlen=window)
    total = 0.0
    for value in values:
        if len(acc) == window:
            total -= acc[0]
        acc.append(value)
        total += value
        if len(acc) == window:
            averages.append(total / window)
        else:
            averages.append(float("nan"))
    return averages


def crossover(previous_short: float, previous_long: float, current_short: float, current_long: float) -> bool:
    """Return ``True`` if a bullish crossover occurred between the last two candles."""

    return previous_short <= previous_long and current_short > current_long
