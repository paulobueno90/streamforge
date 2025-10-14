"""
Kraken exchange integration module.

This module provides complete Kraken exchange integration including:
- KrakenRunner: High-level API for data ingestion
- KrakenWS: WebSocket connection handler
- Processors: OHLC data processing
- Normalizers: Kraken data normalization
- API: Historical data fetching
"""

from .runner import KrakenRunner
from .ws.ws import KrakenWS

__all__ = [
    "KrakenRunner",
    "KrakenWS",
]