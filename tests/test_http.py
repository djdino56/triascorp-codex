from __future__ import annotations

from datetime import datetime, timedelta
from http import HTTPStatus
from typing import Any, Dict

import pytest

from backtester import http
from backtester.models import BacktestReport, Candle, Position, TradeResult


def _make_candle(offset_minutes: int = 0, close: float = 100.0) -> Candle:
    base = datetime(2024, 1, 1, 0, 0, 0)
    timestamp = base + timedelta(minutes=offset_minutes)
    return Candle(
        timestamp=timestamp,
        open=close - 1,
        high=close + 1,
        low=close - 2,
        close=close,
        volume=10.0,
    )


def test_get_candles_success(monkeypatch: pytest.MonkeyPatch) -> None:
    candles = [_make_candle(), _make_candle(offset_minutes=5, close=110.0)]

    def fake_fetch(**kwargs: Dict[str, Any]) -> list[Candle]:
        assert kwargs["instrument_name"] == "BTC_USDC"
        assert kwargs["resolution"] == "60"
        assert kwargs["start"] is None
        assert kwargs["end"] is None
        return candles

    monkeypatch.setattr(http, "fetch_candles", fake_fetch)

    status, payload = http.get_candles_response({"instrument_name": "BTC_USDC", "resolution": "60"})

    assert status is HTTPStatus.OK
    assert len(payload["candles"]) == 2
    assert payload["candles"][0]["timestamp"] == candles[0].timestamp.isoformat()
    assert payload["candles"][1]["close"] == pytest.approx(110.0)


def test_run_backtest_uses_posted_candles(monkeypatch: pytest.MonkeyPatch) -> None:
    candles = [_make_candle(), _make_candle(offset_minutes=1, close=105.0)]
    candle_payload = [
        {
            "timestamp": candle.timestamp.isoformat(),
            "open": candle.open,
            "high": candle.high,
            "low": candle.low,
            "close": candle.close,
            "volume": candle.volume,
        }
        for candle in candles
    ]

    def fail_fetch(**_kwargs: Dict[str, Any]) -> list[Candle]:
        pytest.fail("fetch_candles should not be called when candles are supplied")

    class DummyBacktester:
        last_instance: "DummyBacktester" | None = None

        def __init__(self, config: http.BacktestConfig):
            self.config = config
            self.candles = []
            DummyBacktester.last_instance = self

        def run(self, received_candles: list[Candle]) -> BacktestReport:
            self.candles = received_candles
            position = Position(entry_price=received_candles[0].close, entry_time=received_candles[0].timestamp)
            trade = TradeResult(position=position, profit=12.5)
            return BacktestReport(trades=[trade], final_cash=1012.5, wins=1, losses=0)

    monkeypatch.setattr(http, "fetch_candles", fail_fetch)
    monkeypatch.setattr(http, "Backtester", DummyBacktester)

    status, payload = http.run_backtest_response(
        {
            "config": {
                "instrumentName": "BTC_USDC",
                "interval": "60",
                "initialCash": 1000.0,
                "maxOpenPositions": 1,
                "takeProfit": 0.03,
                "stopLoss": 0.02,
                "shortWindow": 9,
                "longWindow": 21,
            },
            "candles": candle_payload,
        }
    )

    assert status is HTTPStatus.OK
    data = payload["report"]
    assert data["finalCash"] == pytest.approx(1012.5)
    assert data["wins"] == 1
    assert data["trades"][0]["position"]["entryPrice"] == pytest.approx(candles[0].close)

    dummy = DummyBacktester.last_instance
    assert dummy is not None
    assert dummy.config.instrument_name == "BTC_USDC"
    assert len(dummy.candles) == len(candles)
    assert all(isinstance(item, Candle) for item in dummy.candles)


def test_run_backtest_fetches_when_candles_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    fetched = [_make_candle(), _make_candle(offset_minutes=1, close=120.0)]
    called: Dict[str, Any] = {}

    def fake_fetch(**kwargs: Dict[str, Any]) -> list[Candle]:
        called.update(kwargs)
        return fetched

    class DummyBacktester:
        def __init__(self, config: http.BacktestConfig):
            self.config = config

        def run(self, received_candles: list[Candle]) -> BacktestReport:
            assert received_candles == fetched
            position = Position(entry_price=received_candles[0].close, entry_time=received_candles[0].timestamp)
            trade = TradeResult(position=position, profit=5.0)
            return BacktestReport(trades=[trade], final_cash=1005.0, wins=1, losses=0)

    monkeypatch.setattr(http, "fetch_candles", fake_fetch)
    monkeypatch.setattr(http, "Backtester", DummyBacktester)

    status, body = http.run_backtest_response(
        {
            "config": {
                "instrumentName": "ETH_USDC",
                "interval": "5",
                "start": "2024-01-01T00:00:00",
                "end": "2024-01-01T01:00:00",
                "initialCash": 2000.0,
                "maxOpenPositions": 2,
                "takeProfit": 0.05,
                "stopLoss": 0.02,
                "shortWindow": 5,
                "longWindow": 15,
            }
        }
    )

    assert status is HTTPStatus.OK
    report = body["report"]
    assert report["losses"] == 0
    assert called["instrument_name"] == "ETH_USDC"
    assert called["resolution"] == "5"
    assert called["start"] == datetime(2024, 1, 1, 0, 0)
    assert called["end"] == datetime(2024, 1, 1, 1, 0)
