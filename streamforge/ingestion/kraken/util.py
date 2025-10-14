from ciso8601 import parse_datetime
from streamforge.ingestion.kraken.api.api import KrakenAPI


def parse_string_to_timestamp(date_string: str, offset: int=0) -> int:
    datetime_obj = parse_datetime(date_string)
    timestamp_obj = datetime_obj.timestamp() - offset
    return int(timestamp_obj)


async def get_symbol_set():
    info = await KrakenAPI().get_info()
    all_symbols = set()
    for symbol_data in info["symbols"]:
        all_symbols.add(symbol_data["symbol"])

    return all_symbols
