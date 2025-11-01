"""Backtesting toolkit for Deribit spot candles."""

from .backtest import Backtester
from .config import BacktestConfig

__all__ = ["Backtester", "BacktestConfig", "fetch_candles"]


def fetch_candles(*args, **kwargs):
    """Proxy for :func:`backtester.api.fetch_candles` with a lazy import.

    Importing :mod:`requests` can be slow and is unnecessary for unit tests that
    only rely on the backtesting engine, so the import is deferred until the
    function is actually invoked.
    """

    from .api import fetch_candles as _fetch_candles

    return _fetch_candles(*args, **kwargs)
