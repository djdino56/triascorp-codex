"""Lightweight HTTP server that exposes the backtester as JSON endpoints."""
from __future__ import annotations

import json
import logging
from datetime import datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Dict, Iterable, List, Tuple
from urllib.parse import parse_qs, urlparse

from .api import fetch_candles
from .backtest import Backtester
from .config import BacktestConfig
from .models import BacktestReport, Candle, Position, TradeResult

LOGGER = logging.getLogger(__name__)

CONFIG_FIELD_MAP = {
    "instrumentName": "instrument_name",
    "interval": "interval",
    "start": "start",
    "end": "end",
    "initialCash": "initial_cash",
    "maxOpenPositions": "max_open_positions",
    "takeProfit": "take_profit",
    "stopLoss": "stop_loss",
    "shortWindow": "short_window",
    "longWindow": "long_window",
}


def _parse_datetime(value: str | None) -> datetime | None:
    if value in (None, "", "null"):
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError as exc:  # pragma: no cover - defensive
        raise ValueError(f"Invalid datetime '{value}'. Expected ISO-8601 format.") from exc


def _serialize_datetime(value: datetime | None) -> str | None:
    return value.isoformat() if value is not None else None


def _serialize_candle(candle: Candle) -> Dict[str, Any]:
    return {
        "timestamp": candle.timestamp.isoformat(),
        "open": candle.open,
        "high": candle.high,
        "low": candle.low,
        "close": candle.close,
        "volume": candle.volume,
    }


def _serialize_position(position: Position) -> Dict[str, Any]:
    return {
        "entryPrice": position.entry_price,
        "entryTime": _serialize_datetime(position.entry_time),
        "size": position.size,
        "exitPrice": position.exit_price,
        "exitTime": _serialize_datetime(position.exit_time),
        "stopLoss": position.stop_loss,
        "takeProfit": position.take_profit,
    }


def _serialize_trade(trade: TradeResult) -> Dict[str, Any]:
    return {
        "position": _serialize_position(trade.position),
        "profit": trade.profit,
    }


def _serialize_report(report: BacktestReport) -> Dict[str, Any]:
    return {
        "trades": [_serialize_trade(trade) for trade in report.trades],
        "finalCash": report.final_cash,
        "wins": report.wins,
        "losses": report.losses,
    }


def _config_from_payload(payload: Dict[str, Any]) -> BacktestConfig:
    kwargs: Dict[str, Any] = {}
    for camel, field in CONFIG_FIELD_MAP.items():
        if camel not in payload:
            continue
        value = payload[camel]
        if field in {"start", "end"}:
            value = _parse_datetime(value) if value else None
        kwargs[field] = value
    return BacktestConfig(**kwargs)


def _candles_from_payload(items: Iterable[Dict[str, Any]]) -> List[Candle]:
    candles: List[Candle] = []
    for item in items:
        try:
            timestamp = _parse_datetime(item.get("timestamp"))
            if timestamp is None:
                raise ValueError("timestamp is required")
            candle = Candle(
                timestamp=timestamp,
                open=float(item["open"]),
                high=float(item["high"]),
                low=float(item["low"]),
                close=float(item["close"]),
                volume=float(item["volume"]),
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f"Invalid candle payload: {item}") from exc
        candles.append(candle)
    return candles


def get_candles_response(query: Dict[str, str]) -> Tuple[HTTPStatus, Dict[str, Any]]:
    instrument_name = query.get("instrument_name")
    resolution = query.get("resolution")
    if not instrument_name or not resolution:
        return HTTPStatus.BAD_REQUEST, {"detail": "instrument_name and resolution are required"}

    start = _parse_datetime(query.get("start")) if query.get("start") else None
    end = _parse_datetime(query.get("end")) if query.get("end") else None

    try:
        candles = fetch_candles(
            instrument_name=instrument_name,
            resolution=resolution,
            start=start,
            end=end,
        )
    except Exception as exc:  # noqa: BLE001 - surface network errors cleanly
        LOGGER.exception("Failed to fetch candles", exc_info=exc)
        return HTTPStatus.BAD_GATEWAY, {"detail": str(exc)}

    return HTTPStatus.OK, {"candles": [_serialize_candle(candle) for candle in candles]}


def run_backtest_response(payload: Dict[str, Any]) -> Tuple[HTTPStatus, Dict[str, Any]]:
    config_payload = payload.get("config")
    if not isinstance(config_payload, dict):
        return HTTPStatus.BAD_REQUEST, {"detail": "config is required"}

    try:
        config = _config_from_payload(config_payload)
    except Exception as exc:  # noqa: BLE001 - validation errors bubble up
        return HTTPStatus.UNPROCESSABLE_ENTITY, {"detail": str(exc)}

    try:
        backtester = Backtester(config)
    except ValueError as exc:
        return HTTPStatus.UNPROCESSABLE_ENTITY, {"detail": str(exc)}

    candles_payload = payload.get("candles")
    if candles_payload:
        if not isinstance(candles_payload, list):
            return HTTPStatus.BAD_REQUEST, {"detail": "candles must be an array"}
        try:
            candles = _candles_from_payload(candles_payload)
        except ValueError as exc:
            return HTTPStatus.BAD_REQUEST, {"detail": str(exc)}
    else:
        try:
            candles = fetch_candles(
                instrument_name=config.instrument_name,
                resolution=config.interval,
                start=config.start,
                end=config.end,
            )
        except Exception as exc:  # noqa: BLE001 - surface network errors cleanly
            LOGGER.exception("Failed to fetch candles", exc_info=exc)
            return HTTPStatus.BAD_GATEWAY, {"detail": str(exc)}

    report = backtester.run(candles)
    return HTTPStatus.OK, {"report": _serialize_report(report)}


class BacktesterRequestHandler(BaseHTTPRequestHandler):
    """Serve the JSON API using the standard library HTTP server."""

    def do_GET(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler signature
        parsed = urlparse(self.path)
        if parsed.path != "/api/candles":
            self.send_error(HTTPStatus.NOT_FOUND, "Endpoint not found")
            return

        query = {key: values[0] for key, values in parse_qs(parsed.query, keep_blank_values=True).items()}
        status, body = get_candles_response(query)
        self._send_json(status, body)

    def do_POST(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler signature
        parsed = urlparse(self.path)
        if parsed.path != "/api/backtest":
            self.send_error(HTTPStatus.NOT_FOUND, "Endpoint not found")
            return

        length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(length) if length > 0 else b""
        try:
            payload = json.loads(raw_body.decode("utf-8")) if raw_body else {}
        except json.JSONDecodeError:
            self._send_json(HTTPStatus.BAD_REQUEST, {"detail": "Invalid JSON payload"})
            return

        status, body = run_backtest_response(payload)
        self._send_json(status, body)

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A003 - following base signature
        LOGGER.info("%s - - %s", self.client_address[0], format % args)

    def _send_json(self, status: HTTPStatus, body: Dict[str, Any]) -> None:
        data = json.dumps(body).encode("utf-8")
        self.send_response(status.value)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def serve(host: str = "127.0.0.1", port: int = 8000) -> None:
    """Start the threaded HTTP server."""

    server = ThreadingHTTPServer((host, port), BacktesterRequestHandler)
    LOGGER.info("Starting HTTP server on http://%s:%s", host, port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:  # pragma: no cover - manual shutdown
        LOGGER.info("Shutting down server")
    finally:
        server.server_close()


if __name__ == "__main__":  # pragma: no cover - manual execution
    logging.basicConfig(level=logging.INFO)
    serve()
