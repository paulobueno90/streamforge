
def adjust_binance_timestamps(data: dict):
    """Convert milliseconds to seconds (for API and WebSocket data)"""
    data["t"] = int(data["t"]) // 1000
    data["T"] = int(data["T"]) // 1000
    return data


def adjust_binance_timestamps_csv(data: dict):
    """Convert microseconds to seconds (for CSV data)"""
    data["t"] = int(data["t"]) // 1_000_000
    data["T"] = int(data["T"]) // 1_000_000
    return data
