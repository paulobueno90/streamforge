"""
Stream input configuration module.

This module defines the DataInput class which configures what data streams
to subscribe to from cryptocurrency exchanges.
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class DataInput:
    """
    Configuration for a data stream subscription.
    
    DataInput specifies what type of market data to stream from an exchange,
    including the symbols, timeframe, and any aggregation requirements.
    
    Attributes:
        type: Type of data stream (e.g., 'kline', 'trade', 'depth', 'ticker')
        symbols: List of trading pair symbols to subscribe to (e.g., ['BTCUSDT', 'ETHUSDT'])
        timeframe: Timeframe interval for OHLC data (e.g., '1m', '5m', '1h', '1d')
        aggregate_list: Optional list of additional timeframes to aggregate to
                       (e.g., ['5m', '15m', '1h'] when base is '1m')
    
    Examples:
        Basic kline stream:
        >>> stream = DataInput(
        ...     type="kline",
        ...     symbols=["BTCUSDT"],
        ...     timeframe="1m"
        ... )
        
        With aggregation:
        >>> stream = DataInput(
        ...     type="kline",
        ...     symbols=["BTCUSDT", "ETHUSDT"],
        ...     timeframe="1m",
        ...     aggregate_list=["5m", "15m", "1h"]
        ... )
    
    Note:
        The 'type' field determines which processor will handle the data.
        Supported types vary by exchange but commonly include:
        - 'kline', 'candle', 'ohlc': OHLC/candlestick data
        - 'trade': Individual trades
        - 'depth': Order book depth
        - 'ticker': Price ticker updates
    """
    type: str
    symbols: list
    timeframe: Optional[str]
    aggregate_list: Optional[List[str]] = field(default_factory=list)