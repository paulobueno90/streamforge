"""
Bybit utility functions for market type mapping and timeframe conversion.
"""

MARKET_TYPE_STRING_MAP = {
    "DEFAULT": "SPOT",
    "SPOT": "SPOT",
    "LINEAR": "LINEAR",           # USDT/USDC perpetuals
    "INVERSE": "INVERSE",         # Inverse contracts
    "FUTURES (LINEAR)": "LINEAR", # Alias
    "FUTURES (INVERSE)": "INVERSE", # Alias
}

MARKET_TYPE_PATH_MAP = {
    "SPOT": "spot",
    "LINEAR": "linear",
    "INVERSE": "inverse",
    "DEFAULT": "spot",
}

# Bybit timeframe format: "1", "5", "15", "30", "60", "240", "D", "W", "M"
TIMEFRAME_TO_BYBIT_MAP = {
    "1m": "1",
    "3m": "3",
    "5m": "5",
    "15m": "15",
    "30m": "30",
    "1h": "60",
    "2h": "120",
    "4h": "240",
    "1d": "D",
    "1w": "W",
    "1M": "M",
}

# Reverse mapping: Bybit format to StreamForge format
BYBIT_TO_TIMEFRAME_MAP = {
    "1": "1m",
    "3": "3m",
    "5": "5m",
    "15": "15m",
    "30": "30m",
    "60": "1h",
    "120": "2h",
    "240": "4h",
    "D": "1d",
    "W": "1w",
    "M": "1M",
}

TIMEFRAME_TO_MINUTES_MAP = {
    "1m": 1,
    "3m": 3,
    "5m": 5,
    "15m": 15,
    "30m": 30,
    "1h": 60,
    "2h": 120,
    "4h": 240,
    "1d": 1440,
}


def get_timeframe_seconds(timeframe: str) -> int:
    return TIMEFRAME_TO_MINUTES_MAP.get(timeframe, 1) * 60


def get_bybit_timeframe(streamforge_timeframe: str) -> str:
    """
    Convert StreamForge timeframe format to Bybit format.
    
    Args:
        streamforge_timeframe: Timeframe in StreamForge format (e.g., "1m", "5m", "1h")
        
    Returns:
        Bybit timeframe format (e.g., "1", "5", "60", "D")
        
    Examples:
        >>> get_bybit_timeframe("1m")
        '1'
        >>> get_bybit_timeframe("1h")
        '60'
        >>> get_bybit_timeframe("1d")
        'D'
    """
    return TIMEFRAME_TO_BYBIT_MAP.get(streamforge_timeframe.lower(), streamforge_timeframe)


def get_streamforge_timeframe(bybit_timeframe: str) -> str:
    """
    Convert Bybit timeframe format to StreamForge format.
    
    Args:
        bybit_timeframe: Timeframe in Bybit format (e.g., "1", "5", "60", "D")
        
    Returns:
        StreamForge timeframe format (e.g., "1m", "5m", "1h", "1d")
        
    Examples:
        >>> get_streamforge_timeframe("1")
        '1m'
        >>> get_streamforge_timeframe("60")
        '1h'
        >>> get_streamforge_timeframe("D")
        '1d'
    """
    return BYBIT_TO_TIMEFRAME_MAP.get(bybit_timeframe, bybit_timeframe)

