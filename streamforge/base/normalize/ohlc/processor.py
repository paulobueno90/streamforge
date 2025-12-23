from ciso8601 import parse_datetime
from streamforge.base.normalize.ohlc.models.candle import Kline
from streamforge.base.normalize.ohlc.maps import KRAKEN_TIMEFRAME_INTERVAL_MAP
from streamforge.base.normalize.ohlc.api import kraken, binance
from streamforge.base.normalize.ohlc.models.timeframes import BaseTimeframe


def parse_string_to_timestamp(date_string: str, offset: int=0) -> int:
    datetime_obj = parse_datetime(date_string)
    timestamp_obj = datetime_obj.timestamp() - offset
    return int(timestamp_obj)


def adjust_binance_timestamps(data: dict):
    data["t"] = int(data["t"]) // 1000
    data["T"] = int(data["T"]) // 1000
    return data


class OHLCDatNormalizer:

    @classmethod
    def normalize_binance_ws(cls, data: dict):
        datapoint = data["k"]
        datapoint["source"] = "binance"
        datapoint = adjust_binance_timestamps(data=datapoint)

        return Kline(**datapoint)

    @classmethod
    def normalize_kraken_ws(cls, data: dict):

        data["source"] = "kraken"
        data["timeframe"] = KRAKEN_TIMEFRAME_INTERVAL_MAP.get(data["interval"])

        return Kline(**data)

    @classmethod
    def normalize_kraken_api(cls, kline: list, symbol: str, timeframe: BaseTimeframe, source: str = "kraken"):
        """Parse Kraken OHLC data item into Kline object"""

        candle_data = dict(source=source, s=symbol, i=timeframe.string_tf)

        for c, k in zip(kraken.API_KLINES_COLUMNS, kline):
            candle_data[c] = k

        timeframe_minutes = int(timeframe.tf)
        timeframe_seconds = timeframe_minutes * 60
        candle_data["T"] = candle_data["t"] + timeframe_seconds

        return Kline(**candle_data)

    @classmethod
    def normalize_binance_api(cls, kline: list, symbol: str, timeframe: str, source: str = "binance"):
        candle_data = dict(source=source, s=symbol, i=timeframe)
        for c, k in zip(binance.API_KLINES_COLUMNS, kline):
            candle_data[c] = k
        candle_data = adjust_binance_timestamps(data=candle_data)
        return Kline(**candle_data)

