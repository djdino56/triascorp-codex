"""Deribit REST API helpers."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Iterable, List

import requests

from .models import Candle

LOGGER = logging.getLogger(__name__)

DERIBIT_API_URL = "https://www.deribit.com/api/v2/public/get_tradingview_chart_data"


def _to_datetime(timestamp_ms: int) -> datetime:
    return datetime.utcfromtimestamp(timestamp_ms / 1000)


def fetch_candles(
    instrument_name: str,
    resolution: str,
    start: datetime | None = None,
    end: datetime | None = None,
) -> List[Candle]:
    """Fetch candles from the Deribit TradingView chart API.

    Args:
        instrument_name: Spot instrument identifier.
        resolution: Candle resolution (Deribit-compatible string).
        start: Optional inclusive UTC datetime for the first candle.
        end: Optional exclusive UTC datetime for the final candle.

    Returns:
        A list of :class:`Candle` instances ordered by timestamp.
    """

    params = {
        "instrument_name": instrument_name,
        "resolution": resolution,
    }
    if start is not None:
        params["start_timestamp"] = int(start.timestamp() * 1000)
    if end is not None:
        params["end_timestamp"] = int(end.timestamp() * 1000)

    LOGGER.debug("Fetching candles with params %s", params)
    response = requests.get(DERIBIT_API_URL, params=params, timeout=10)
    response.raise_for_status()
    payload = response.json()
    if payload.get("result") is None:
        raise ValueError(f"Unexpected API response: {payload}")

    result = payload["result"]
    timestamps = result.get("ticks") or []

    def safe_iter(values: Iterable | None) -> Iterable:
        return values or []

    candles: List[Candle] = []
    for ts, o, h, l, c, v in zip(
        timestamps,
        safe_iter(result.get("open")),
        safe_iter(result.get("high")),
        safe_iter(result.get("low")),
        safe_iter(result.get("close")),
        safe_iter(result.get("volume")),
    ):
        candle = Candle(
            timestamp=_to_datetime(ts),
            open=float(o),
            high=float(h),
            low=float(l),
            close=float(c),
            volume=float(v),
        )
        candles.append(candle)

    return candles
