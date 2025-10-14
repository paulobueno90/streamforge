from streamforge.base.normalize.normalize import Normalizer
from streamforge.base.normalize.ohlc.models.candle import Kline
from streamforge.ingestion.binance.normalizers.util import adjust_binance_timestamps
from typing import Union, Dict, Any, List


class KlineNormalizer(Normalizer):

    API_KLINES_COLUMNS = [
        "t",  # Kline open time
        "o",  # Open price
        "h",  # High price
        "l",  # Low price
        "c",  # Close price
        "v",  # Volume
        "T",  # Kline Close time
        "q",  # Quote asset volume
        "n",  # Number of trades
        "V",  # Taker buy base asset volume
        "Q",  # Taker buy quote asset volume
        "B",  # Unused field, ignore.
    ]

    def api(self, data: Union[Dict[str, Any], List], **kwargs):
        source = kwargs.get('source', 'binance')
        symbol = kwargs.get("symbol")
        timeframe = kwargs.get('timeframe')

        candle_data = dict(source=source, s=symbol, i=timeframe)
        for c, k in zip(self.API_KLINES_COLUMNS, data):
            candle_data[c] = k
        candle_data = adjust_binance_timestamps(data=candle_data)

        return Kline(**candle_data)

    def ws(self, data: Dict[str, Any]) -> Kline:
        datapoint = data["data"]["k"]
        datapoint["source"] = "binance"
        datapoint = adjust_binance_timestamps(data=datapoint)

        return Kline(**datapoint)

    def csv(self, data: Dict[str, Any]) -> Kline:
        data["source"] = "binance"
        data["t"] = data["datetime"]
        data["T"] = data["close time"]
        data = adjust_binance_timestamps(data=data)
        return Kline(**data)



