"""
StreamForge - Real-time cryptocurrency and financial data ingestion system.

StreamForge is a unified, async-first framework for ingesting real-time market data
from cryptocurrency exchanges. It provides:

- **Multi-exchange support**: Binance, Kraken, OKX, Bybit, and more
- **Real-time streaming**: WebSocket-based live data feeds
- **Data normalization**: Standardized data models across exchanges
- **Multiple outputs**: CSV, PostgreSQL, Kafka, and custom emitters
- **Timeframe aggregation**: Automatic aggregation to higher timeframes
- **Type-safe**: Full type hints and Pydantic validation

Quick Start:
    >>> import asyncio
    >>> from streamforge import BinanceRunner, DataInput
    >>> from streamforge.base.emitters import CSVEmitter
    >>> 
    >>> async def main():
    ...     stream = DataInput(type="kline", symbols=["BTCUSDT"], timeframe="1m")
    ...     runner = BinanceRunner(stream_input=stream)
    ...     runner.register_emitter(CSVEmitter("btc_data.csv"))
    ...     await runner.run()
    >>> 
    >>> asyncio.run(main())

Modules:
    base: Core framework components (Runner, WebsocketHandler, emitters, processors)
    ingestion: Exchange-specific implementations (binance, kraken, okx, bybit)
"""

__version__ = "0.1.2"
__author__ = "Paulo Bueno"

# Main package imports
from . import base
from .ingestion.binance.runner import BinanceRunner
from .ingestion.kraken.runner import KrakenRunner
from .ingestion.okx.runner import OKXRunner
from .ingestion.bybit.runner import BybitRunner

# Convenience imports
from .base.stream_input import DataInput
from .base.emitters.base import DataEmitter, EmitterHolder
from .base.emitters.postgresql.db import PostgresEmitter
from .base.emitters.kafka.kafka import KafkaEmitter
from .base.emitters.csv.csv import CSVEmitter
from .base.normalize.ohlc.models.candle import Kline

from .ingestion.binance.backfilling import BinanceBackfilling
from .ingestion.okx.backfilling import OkxBackfilling
from .ingestion.bybit.backfilling import BybitBackfilling

# Merge stream imports
from .merge_stream import merge_streams

# Logger and config imports
from .base.config import config
from .base.logger import DefaultLogger, SilentLogger

__all__ = [
    # Submodules
    "base",
    "ingestion",
    
    # Configuration
    "DataInput",
    "config",
    
    # Runners (most common usage)
    "BinanceRunner",
    "KrakenRunner",
    "OKXRunner",
    "BybitRunner",
    
    # Emitters
    "DataEmitter",
    "EmitterHolder",
    "PostgresEmitter",
    "KafkaEmitter",
    
    # Data models
    "Kline",
    
    # Backfilling
    "BinanceBackfilling",
    "OkxBackfilling",
    "BybitBackfilling",
    
    # Logger utilities
    "DefaultLogger",
    "SilentLogger",
    
    # Metadata
    "__version__",
    "__author__",

    # Merge stream
    "merge_streams",
]
