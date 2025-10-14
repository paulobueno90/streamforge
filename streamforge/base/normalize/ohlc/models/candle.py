"""
Candle/Kline data model.

This module defines the Kline class, the core data structure for representing
OHLC (Open, High, Low, Close) candlestick data across all supported exchanges.
"""

from typing import List, Any, Optional
from pydantic import BaseModel, Field, AliasChoices, field_validator
from streamforge.base.normalize.ohlc.util import parse_string_to_timestamp


class Kline(BaseModel):
    """
    Normalized candlestick/kline data model.
    
    Kline represents OHLC market data in a standardized format across all exchanges.
    It uses Pydantic for validation and supports multiple field aliases to handle
    different exchange data formats.
    
    Attributes:
        source: Exchange name (e.g., 'Binance', 'Kraken', 'OKX')
        symbol: Trading pair symbol (e.g., 'BTCUSDT', 'BTC/USD')
        timeframe: Candle timeframe (e.g., '1m', '5m', '1h', '1d')
        open_ts: Opening timestamp in seconds (Unix epoch)
        end_ts: Closing timestamp in seconds (Unix epoch)
        open: Opening price
        high: Highest price during the period
        low: Lowest price during the period
        close: Closing price
        volume: Base asset volume traded
        quote_volume: Quote asset volume traded (optional)
        vwap: Volume-weighted average price (optional)
        n_trades: Number of trades during the period (optional)
        is_closed: Whether the candle is closed/finalized (optional)
        
    Examples:
        >>> kline = Kline(
        ...     source="Binance",
        ...     symbol="BTCUSDT",
        ...     timeframe="1m",
        ...     open_ts=1609459200,
        ...     end_ts=1609459260,
        ...     open=29000.0,
        ...     high=29100.0,
        ...     low=28900.0,
        ...     close=29050.0,
        ...     volume=125.5,
        ...     is_closed=True
        ... )
        >>> print(f"BTC closed at ${kline.close}")
        BTC closed at $29050.0
        
    Note:
        The model supports multiple field aliases (e.g., 's', 'symbol', 'ticker', 'pair')
        to handle different exchange data formats. Fields are automatically validated
        and converted to the standard format.
    """

    # Metadata Variables
    source: Optional[str] = Field(None, alias="source", validation_alias=AliasChoices("source"))
    symbol: str = Field(alias="s", validation_alias=AliasChoices("s", "symbol", "ticker", "pair"))
    timeframe: str = Field(alias="i", validation_alias=AliasChoices("i", "timeframe", "tf"))

    # Time related Variables
    open_ts: int = Field(alias="t", validation_alias=AliasChoices("t","interval_begin","ts"))
    end_ts: int = Field(alias="T", validation_alias=AliasChoices("T","timestamp"))

    # Price Variables
    open: float = Field(alias="o", validation_alias=AliasChoices("o", "open", "open_price"))
    high: float = Field(alias="h", validation_alias=AliasChoices("h", "high", "high_price"))
    low: float = Field(alias="l", validation_alias=AliasChoices("l", "low", "low_price"))
    close: float = Field(alias="c", validation_alias=AliasChoices("c", "close", "close_price"))

    # Volume Variables
    volume: float = Field(alias="v", validation_alias=AliasChoices("v", "volume", "base_volume"))
    quote_volume: Optional[float] = Field(None, alias="q",validation_alias=AliasChoices("q", "quote_volume", "Quote asset volume"))
    vwap: Optional[float] = Field(None, alias="vwap", validation_alias=AliasChoices("vwap", "volume_weighted_avg_price"))
    n_trades: Optional[int] = Field(None, alias="n", validation_alias=AliasChoices("n", "count", "trades"))
    is_closed: Optional[bool] = Field(None, alias="is_closed", validation_alias=AliasChoices("is_closed", "x"))

    def map_key(self):
        return f'{self.symbol.upper()}-{self.timeframe}'

    @field_validator('open_ts', mode="before")
    def parse_iso_datetime_begin(cls, v):
        if isinstance(v, str):
            return parse_string_to_timestamp(v)
        elif isinstance(v, int):
            return v
        return v

    @field_validator('end_ts', mode="before")
    def parse_iso_datetime_end(cls, v):
        if isinstance(v, str):
            return parse_string_to_timestamp(v, offset=1)
        elif isinstance(v, int):
            return v
        return v

    def __eq__(self, other: Any) -> bool:
        """Compares Kline objects based on their open timestamp."""
        if other is None:
            return False
        if not isinstance(other, Kline):
            return NotImplemented
        return self.open_ts == other.open_ts

    def __lt__(self, other: Any) -> bool:
        """Compares Kline objects based on their open timestamp."""
        if other is None:
            return False
        if not isinstance(other, Kline):
            return NotImplemented
        return self.open_ts < other.open_ts

    def __gt__(self, other: Any) -> bool:
        """Compares Kline objects based on their open timestamp."""
        if other is None:
            return True
        if not isinstance(other, Kline):
            return NotImplemented
        return self.open_ts > other.open_ts

    def __sub__(self, other: Any) -> int:
        """Calculates the time difference in seconds between two Klines."""
        if not isinstance(other, Kline):
            raise TypeError(f"unsupported operand type(s) for -: 'Kline' and '{type(other).__name__}'")
        return self.end_ts - other.end_ts