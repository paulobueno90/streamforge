
from datetime import datetime, timezone
from typing import List, Union

from streamforge.base.normalize.ohlc.models.candle import Kline


def check_offset(data, offset):
    """Check if data has consistent time intervals"""
    if len(data) == 1:
        return True
    for i in range(1, len(data)):
        if (data[i] - data[i - 1]) != offset:
            return False
    return True


def get_start_timestamp():
    daily_multiplier = (24 * 60 * 60)
    utc_timestamp_now = int(datetime.now(timezone.utc).timestamp())
    return (utc_timestamp_now // daily_multiplier) * daily_multiplier


def timestamp_ms_to_seconds(timestamp: int | str):
    return int(timestamp) // 1000


def filter_timestamp(candle_data_array: list, timestamp: Union[str, int], handle_timestamp: bool = False):

    for candle_data in candle_data_array:

        candle_timestamp = candle_data[0]

        candle_timestamp = timestamp_ms_to_seconds(timestamp=candle_timestamp) if handle_timestamp else candle_timestamp

        if candle_timestamp >= timestamp:
            yield candle_data
