"""
StreamForge Ingestion Module.

This module contains exchange-specific implementations for data ingestion
from cryptocurrency exchanges:
- Binance: Binance exchange integration
- Kraken: Kraken exchange integration  
- OKX: OKX exchange integration
- Polygon: Polygon.io integration (planned)

Each exchange module provides:
- Runner: High-level API for data ingestion
- WebSocket handler: Real-time streaming
- API client: Historical data fetching
- Normalizers: Exchange-specific data normalization
- Processors: Exchange-specific data processing
"""

__all__ = [
    "binance",
    "kraken",
    "okx",
    "polygon",
]
