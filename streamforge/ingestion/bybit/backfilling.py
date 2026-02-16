"""
Bybit backfilling module for historical data retrieval.

This module provides the BybitBackfilling class for downloading historical
kline/candlestick data from Bybit exchange using the REST API.
"""

import asyncio
from streamforge.base.config import config
from datetime import datetime, timezone
from typing import List, Dict, Optional, Any, Union, Callable
from pydantic import BaseModel
from sqlalchemy.orm import declarative_base

from streamforge.base.emitters.base import DataEmitter, EmitterHolder
from streamforge.ingestion.bybit.normalizers.normalizer import KlineNormalizer
from streamforge.ingestion.bybit.api.api import BybitAPI
from streamforge.base.normalize.ohlc.models.timeframes import TIMEFRAME_CLASS_MAP
from streamforge.base.normalize.ohlc.models.candle import Kline
from streamforge.base.emitters.csv.csv import CSVEmitter
from streamforge.ingestion.bybit.util import MARKET_TYPE_STRING_MAP


Base = declarative_base()


class BybitBackfilling:
    """
    Bybit backfilling class for fetching historical kline/candlestick data.
    
    Uses Bybit REST API to fetch historical data for backfilling purposes.
    Supports Spot, Linear (USDT/USDC perpetuals), and Inverse futures markets.
    
    Args:
        symbol: Trading pair symbol (e.g., 'BTCUSDT')
        timeframe: Candle timeframe (e.g., '1m', '5m', '1h', '1d')
        from_date: Start date in '%Y-%m-%d' format
        to_date: End date in '%Y-%m-%d' format or 'now' (default: 'now')
        file_path: Optional custom file path for CSV output
        market_type: Market type - SPOT, LINEAR, or INVERSE (default: 'DEFAULT')
        transformer: Optional data transformation function
        
    Examples:
        Basic usage:
        >>> backfiller = BybitBackfilling(
        ...     symbol="BTCUSDT",
        ...     timeframe="1m",
        ...     from_date="2024-01-01",
        ...     to_date="2024-01-31"
        ... )
        >>> backfiller.run()
        
        With market type:
        >>> backfiller = BybitBackfilling(
        ...     symbol="BTCUSDT",
        ...     timeframe="1h",
        ...     from_date="2024-01-01",
        ...     market_type="LINEAR"
        ... )
        >>> backfiller.run()
    """
    
    _emitter_holder = EmitterHolder()
    _normalizer = KlineNormalizer()
    
    def __init__(self,
                 symbol: str,
                 timeframe: str,
                 from_date: str,
                 to_date: str = "now",
                 file_path: Optional[str] = None,
                 market_type: str = 'DEFAULT',
                 transformer: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None
                 ):
        self.symbol = symbol
        self.timeframe = timeframe
        self.from_date = from_date
        self.to_date = to_date
        self.market_type = market_type
        self.file_path = self._file_name() if file_path is None else file_path
        self.transformer = transformer
        
        # Initialize API with market type
        self._api = BybitAPI(market_type=self.market_type)
    
    def _file_name(self):
        """Generate default CSV filename."""
        market_type_string = MARKET_TYPE_STRING_MAP.get(self.market_type, "SPOT").lower().replace(" ", "_")
        today_string = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        end_date_string = today_string if ((self.to_date == "now") or (self.to_date is None)) else self.to_date
        file_name = f"Bybit-{self.symbol.replace('/', '')}-{market_type_string}-{self.timeframe}-{self.from_date}_{end_date_string}.csv"
        return file_name
    
    def set_transformer(self, transformer_func: Callable[[Dict[str, Any]], Dict[str, Any]], inplace: bool = False):
        """Set data transformation function."""
        self.transformer = transformer_func
        if inplace:
            return None
        else:
            return self
    
    def transform(self, data: Union[Dict[str, Any], Kline]):
        """Apply transformer to data if set."""
        if not isinstance(data, dict):
            data = data.model_dump()
        
        if self.transformer is not None:
            return self.transformer(data)
        else:
            return data
    
    def register_emitter(
            self,
            emitter: DataEmitter,
            model: Optional[Union[Base, BaseModel]] = None,
            map_object: Optional[Dict] = None
    ):
        """Register output emitter (CSV, Postgres, etc.)."""
        if emitter.EMITTER == "csv":
            emitter.set_file_path(file_path=self.file_path, inplace=True)
        self._emitter_holder.add(emitter=emitter, data_model=model, columns_map=map_object)
        config.logger.info(f"Bybit | ADDED | name: '{emitter.EMITTER}' type: '{emitter.EMITTER_TYPE}'")
    
    def _parse_date(self, date_string: str, format_string: str = "%Y-%m-%d"):
        """Parse date string to datetime object."""
        try:
            return datetime.strptime(date_string, format_string)
        except ValueError:
            raise ValueError(f"date_string: {date_string} expected to be in the format '{format_string}'")
    
    async def fetch_historical_data(self):
        """
        Fetch historical data from Bybit API and normalize it.
        
        Yields:
            Kline objects with normalized data
        """
        tf_class = TIMEFRAME_CLASS_MAP[self.timeframe]
        config.logger.info(f"Bybit | Fetching historical data from {self.from_date} to {self.to_date}")
        
        async for kline_batch in self._api.fetch_historical_candles(
            symbol=self.symbol,
            timeframe=tf_class,
            from_date=self.from_date,
            to_date=self.to_date
        ):
            for kline_array in kline_batch:
                kline = self._normalizer.api(
                    data=kline_array,
                    symbol=self.symbol,
                    timeframe=self.timeframe
                )
                yield kline
    
    async def stream(self, batch_size: int = 1000):
        """
        Stream historical data in batches.
        
        Args:
            batch_size: Number of records per batch (default: 1000)
            
        Yields:
            Batches of transformed data dictionaries
        """
        buffer = []
        async for kline_data in self.fetch_historical_data():
            row = self.transform(kline_data)
            buffer.append(row)
            if len(buffer) >= batch_size:
                yield buffer
                buffer = []
        
        if buffer:
            yield buffer
    
    async def _run_with_emitter_bulk(self, batch_size: int = 1000):
        """Run backfilling with bulk emission to registered emitters."""
        await self._emitter_holder.connect()
        
        async for batch in self.stream(batch_size=batch_size):
            await self._emitter_holder.emit_bulk(data=batch)
    
    def run(self):
        """
        Execute backfilling process.
        
        Creates default CSV emitter if none registered, then fetches and emits
        historical data to registered emitters.
        """
        if self._emitter_holder.empty:
            csv_emitter = CSVEmitter(
                file_path=self.file_path,
                transformer_function=self.transformer
            )
            self.register_emitter(emitter=csv_emitter)
        
        asyncio.run(self._run_with_emitter_bulk())

