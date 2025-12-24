TIMESTAMP_PRECISION_MAP = {
    'seconds': 1,
    'milliseconds': 1_000,
    'microseconds': 1_000_000,
}


def detect_timestamp_precision(timestamp: int) -> str:
    """
    Detect timestamp precision based on digit count.
    
    Returns:
        'seconds': 10 digits (e.g., 1609459200)
        'milliseconds': 13 digits (e.g., 1609459200000)
        'microseconds': 16 digits (e.g., 1609459200000000)
    """
    digit_count = len(str(timestamp))
    
    if digit_count == 10:
        return 'seconds'
    elif digit_count == 13:
        return 'milliseconds'
    elif digit_count == 16:
        return 'microseconds'
    else:
        # Heuristic: if >= 16, likely microseconds; if >= 13, likely milliseconds
        if digit_count >= 16:
            return 'microseconds'
        elif digit_count >= 13:
            return 'milliseconds'
        else:
            return 'seconds'



def adjust_binance_timestamps(data: dict):
    """Convert milliseconds to seconds (for API and WebSocket data)"""
    precision = detect_timestamp_precision(data["t"])
    data["t"] = int(data["t"]) // TIMESTAMP_PRECISION_MAP[precision]
    data["T"] = int(data["T"]) // TIMESTAMP_PRECISION_MAP[precision]
    return data

