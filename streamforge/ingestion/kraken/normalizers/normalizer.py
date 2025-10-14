from streamforge.base.normalize.normalize import GeneralNormalizers, Normalizer
from streamforge.ingestion.kraken.normalizers.ohlc import KlineNormalizer
from typing import Union, Dict, Any, List
from streamforge.base.normalize.ohlc.models.candle import Kline


normalizer_map = {
    "kline": KlineNormalizer(),
    "ohlc": KlineNormalizer(),
    "ohlcv": KlineNormalizer()
}


class KrakenNormalizers(GeneralNormalizers):

    CANDLE_WS_COLUMNS = ["ts", "open", "high", "low", "close", "volume", "quote_volume", "volCcyQuote", "is_closed"]

    def api(self, data: Union[Dict[str, Any], List], **kwargs):
        if normalizer := self._normalizers_map.get(kwargs.get('data_type')):
            symbol = kwargs.get("symbol")
            timeframe = kwargs.get("timeframe")
            return normalizer.api(data=data, symbol=symbol, timeframe=timeframe)
        else:
            raise NotImplementedError(f'Stream Type: {data.get("e")}. Normalizer not implemented.')

    def ws(self, data: Dict[str, Any]) -> Union[Kline, None]:

        channel = data.get("channel")
        if channel is None:
            return None

        if normalizer := self._normalizers_map.get(channel):
            return normalizer.ws(data)
        elif normalizer is None:
            return None
        else:
            raise NotImplementedError(f'Stream Type: {data.get("e")}. Normalizer not implemented.')


kraken_normalizer = KrakenNormalizers(normalizers_map=normalizer_map)