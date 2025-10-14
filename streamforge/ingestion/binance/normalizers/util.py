
def adjust_binance_timestamps(data: dict):
    data["t"] = data["t"] // 1000
    data["T"] = data["T"] // 1000
    return data
