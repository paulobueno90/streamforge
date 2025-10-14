from streamforge.base.normalize.normalize import GeneralNormalizers, Normalizer
from streamforge.ingestion.binance.normalizers.ohlc import KlineNormalizer
from typing import Union, Dict, Any, List
from streamforge.base.normalize.ohlc.models.candle import Kline


normalizer_map = {
    "kline": KlineNormalizer(),
    "ohlc": KlineNormalizer(),
    "ohlcv": KlineNormalizer()
}


class BinanceNormalizers(GeneralNormalizers):

    CANDLE_WS_COLUMNS = ["ts", "open", "high", "low", "close", "volume", "quote_volume", "volCcyQuote", "is_closed"]

    def api(self, data: Union[Dict[str, Any], List], **kwargs):
        if normalizer := self._normalizers_map.get(kwargs.get('data_type')):
            symbol = kwargs.get("symbol")
            timeframe = kwargs.get("timeframe")
            return normalizer.api(data=data, symbol=symbol, timeframe=timeframe)
        else:
            raise NotImplementedError(f'Stream Type: {data.get("e")}. Normalizer not implemented.')

    def ws(self, data: Dict[str, Any]) -> Union[Kline, None]:
        if "data" not in data:
            return None

        if normalizer := self._normalizers_map.get(data["data"].get("e")):
            return normalizer.ws(data)
        else:
            raise NotImplementedError(f'Stream Type: {data.get("e")}. Normalizer not implemented.')


binance_normalizer = BinanceNormalizers(normalizers_map=normalizer_map)



