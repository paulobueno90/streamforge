from streamforge.base.normalize.normalize import Normalizer
from streamforge.base.normalize.ohlc.models.candle import Kline
from typing import Union, Dict, Any, List

KRAKEN_TIMEFRAME_INTERVAL_MAP = {
    1: '1m',
    5: '5m',
    10: '10m',
    15: '15m',
    30: '30m',
    60: '1h',
    240: '4h',
    1440: '1d'
}


class KlineNormalizer(Normalizer):

    API_KLINES_COLUMNS = [
        "t",  # Time (Unix timestamp)
        "o",  # Open price
        "h",  # High price
        "l",  # Low price
        "c",  # Close price
        "vwap",  # Volume weighted average price
        "v",  # Volume
        "n",  # Number of trades
    ]

    def api(self, data: Union[Dict[str, Any], List], **kwargs):
        source = kwargs.get('source', 'kraken')
        symbol = kwargs.get("symbol")
        timeframe = kwargs.get('timeframe')

        candle_data = dict(source=source, s=symbol, i=timeframe.string_tf)

        for c, k in zip(self.API_KLINES_COLUMNS, data):
            candle_data[c] = k

        timeframe_minutes = int(timeframe.tf)
        timeframe_seconds = timeframe_minutes * 60
        candle_data["T"] = candle_data["t"] + timeframe_seconds

        return Kline(**candle_data)

    def ws(self, data: Dict[str, Any]) -> Kline:
        datapoint = data["data"][-1]
        datapoint["source"] = "kraken"
        datapoint["timeframe"] = KRAKEN_TIMEFRAME_INTERVAL_MAP.get(datapoint["interval"])

        return Kline(**datapoint)
    