from functools import lru_cache
from typing import Dict, Any
from streamforge.base.normalize.ohlc.models.timeframes import BaseTimeframe, TIMEFRAME_CLASS_MAP



def not_data(data: Dict[str, Any]) -> bool:
    if "data" in data:
        return False
    else:
        return True


@lru_cache(maxsize=None)
def get_channel_type(channel: str):
    if "candle" in channel:
        return "candle"


def _ws_get_symbol_and_timeframe(data: Dict[str, Any]) -> tuple:
    arg_metadata = data["arg"]
    symbol = arg_metadata["instId"]
    timeframe_string = arg_metadata["channel"].replace("candle", "")
    timeframe = TIMEFRAME_CLASS_MAP.get(timeframe_string)

    return symbol, timeframe


def adjust_ms_timestamps(data: dict):
    data["t"] = data["t"] // 1000
    data["T"] = data["T"] // 1000
    return data
