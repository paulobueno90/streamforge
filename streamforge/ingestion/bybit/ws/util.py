"""
Bybit WebSocket utilities for subscription parameter building and topic parsing.
"""

from streamforge.base.stream_input import DataInput
from streamforge.ingestion.bybit.util import get_bybit_timeframe


def parse_topic(topic: str):
    """
    Parse Bybit WebSocket topic to extract stream type, interval, and symbol.
    
    Topic format: "kline.{interval}.{symbol}"
    
    Args:
        topic: Bybit topic string (e.g., "kline.1.BTCUSDT")
        
    Returns:
        Tuple of (stream_type, interval, symbol) or None if invalid
    """
    parts = topic.split(".")
    if len(parts) >= 3:
        return parts[0], parts[1], parts[2]
    return None


def build_subscription_args(stream_input: DataInput) -> list:
    """
    Build Bybit WebSocket subscription arguments.
    
    Bybit format: {"op": "subscribe", "args": ["kline.1.BTCUSDT"]}
    
    Args:
        stream_input: DataInput object with type, symbols, and timeframe
        
    Returns:
        List of subscription topic strings
    """
    if not stream_input.type:
        raise ValueError("Input expects a key named 'type'")
    
    stream_type = stream_input.type.lower()
    if stream_type not in ["kline", "klines", "candle", "ohlc", "ohlcv"]:
        raise ValueError(f"Stream type '{stream_input.type}' is not supported for Bybit klines.")
    
    # Convert timeframe to Bybit format
    bybit_interval = get_bybit_timeframe(stream_input.timeframe)
    
    # Build topic strings: "kline.{interval}.{symbol}"
    topics = []
    for symbol in stream_input.symbols:
        topic = f"kline.{bybit_interval}.{symbol.upper()}"
        topics.append(topic)
    
    return topics


def check_input(stream_input: DataInput) -> DataInput:
    """
    Validate stream input for Bybit WebSocket.
    
    Args:
        stream_input: DataInput object to validate
        
    Returns:
        Validated DataInput object
        
    Raises:
        ValueError: If input is invalid
    """
    if not stream_input.type:
        raise ValueError("Input expects a key named 'type'")
    
    valid_types = ["kline", "klines", "candle", "ohlc", "ohlcv"]
    if stream_input.type.lower() not in valid_types:
        raise ValueError(f"Stream type '{stream_input.type}' is not a valid type or is not implemented.")
    
    if not stream_input.symbols:
        raise ValueError("Input expects at least one symbol in 'symbols' list")
    
    if not stream_input.timeframe:
        raise ValueError("Input expects a 'timeframe' (e.g., '1m', '5m', '1h')")
    
    return stream_input

