import datetime as dt
from datetime import datetime
from streamforge.ingestion.binance.api.api import BinanceAPI

import asyncio

DATE_STRING_FORMATS = ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"]
SECONDS_IN_A_DAY = 1440 * 60

AGG_TIMESTAMP_MAP = {
    "3m": 3 * 60,
    "5m": 5 * 60,
    "10m": 10 * 60,
    "15m": 15 * 60,
    "30m": 30 * 60,
    "60m": 60 * 60,
    "1h": 60 * 60,
    "4h": 240 * 60,
    "1d": 1444 * 60
}


def is_timestamp_in_ms(timestamp: int) -> bool:
    return len(str(timestamp)) >= 13


def process_timestamp(value):
    if isinstance(value, int):
        return value if is_timestamp_in_ms(value) else value * 1000
    elif isinstance(value, str):
        for dt_format in DATE_STRING_FORMATS:
            try:
                return datetime.strptime(value, dt_format).timestamp() * 1000
            except:
                continue

        raise ValueError(f'String datetime variables should be in format: '
                         f'"%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d".\n'
                         f'Instead {value} was sent.')

    elif isinstance(value, datetime):
        return value.timestamp() * 1000

    else:
        raise TypeError(f"Date and time expected integers or string in date format. Instead {type(value)} was sent.")


def today_utc_timestamp():
    return (datetime.utcnow().timestamp() // SECONDS_IN_A_DAY) * SECONDS_IN_A_DAY


def check_end_timestamp(ts):
    aggregation_triggered = []
    for tf, value in AGG_TIMESTAMP_MAP.items():
        if (ts % value) == 0:
            aggregation_triggered.append(tf)
    return aggregation_triggered


async def get_symbol_set():
    info = await BinanceAPI().get_info()
    all_symbols = set()
    for symbol_data in info["symbols"]:
        all_symbols.add(symbol_data["symbol"])

    return all_symbols
