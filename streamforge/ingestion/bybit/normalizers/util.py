"""
Bybit normalizer utilities for timestamp conversion and timeframe mapping.
"""

TIMESTAMP_PRECISION_MAP = {
    'seconds': 1,
    'milliseconds': 1_000,
    'microseconds': 1_000_000,
}


def get_timestamp_precision(timestamp: int) -> int:
    """
    Detect timestamp precision based on digit count.
    
    Returns:
        'seconds': 10 digits (e.g., 1609459200)
        'milliseconds': 13 digits (e.g., 1609459200000)
        'microseconds': 16 digits (e.g., 1609459200000000)
    """
    digit_count = len(str(timestamp))
    
    if digit_count == 10:
        return 1 # seconds
    elif digit_count == 13:
        return 1000 # milliseconds
    elif digit_count == 16:
        return 1000000 # microseconds
    else:
        # Heuristic: if >= 16, likely microseconds; if >= 13, likely milliseconds
        if digit_count >= 16:
            return 1000000 # microseconds
        elif digit_count >= 13:
            return 1000 # milliseconds
        else:
            return 1 # seconds


def adjust_bybit_timestamps(data: dict):
    """
    Convert Bybit timestamps from milliseconds to seconds.
    
    Bybit uses milliseconds for timestamps in both API and WebSocket.
    StreamForge Kline model expects seconds.
    
    Args:
        data: Dictionary with 't' (start) and 'T' (end) timestamp fields
        
    Returns:
        Dictionary with timestamps converted to seconds
    """
    
    precision = get_timestamp_precision(data["start"])
    data["start"] = int(data["start"]) // precision
    data["end"] = int(data["end"]) // precision

    data.pop("timestamp")
    
    return data