"""
Basic model classes for the crypto_ingest package.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class BaseKlineBuffer:
    """Base class for kline buffer implementations."""
    
    def __init__(self):
        self.buffer = []
    
    def add(self, item: Any):
        """Add an item to the buffer."""
        self.buffer.append(item)
    
    def clear(self):
        """Clear the buffer."""
        self.buffer.clear()
    
    def get_buffer(self) -> List[Any]:
        """Get the current buffer."""
        return self.buffer.copy()


class BaseAggregateTF:
    """Base class for timeframe aggregation."""
    
    def __init__(self, timeframe: str):
        self.timeframe = timeframe
    
    def aggregate(self, data: Any) -> Any:
        """Aggregate data for the timeframe."""
        return data


class WarmupConfigurationError(Exception):
    """Exception raised for warmup configuration errors."""
    pass


# Kraken specific constants
API_KLINES_COLUMNS = [
    'timestamp',
    'open',
    'high', 
    'low',
    'close',
    'volume',
    'count'
]
