"""
Binance exchange integration module.

This module provides complete Binance exchange integration including:
- BinanceRunner: High-level API for data ingestion
- BinanceWS: WebSocket connection handler
- Processors: Kline/candle data processing
- Normalizers: Binance data normalization
- API: Historical data fetching
"""

from .runner import BinanceRunner
from .ws.ws import BinanceWS
from .processors.kline import KlineData, KlineBinance

__all__ = [
    "BinanceRunner",
    "BinanceWS",
    "KlineBinance",
    "KlineData",
]