from streamforge.base.normalize.normalize import Normalizer
from streamforge.base.normalize.ohlc.models.candle import Kline
from streamforge.ingestion.okx.normalizers.util import adjust_ms_timestamps, _ws_get_symbol_and_timeframe
from typing import Union, Dict, Any, List



class KlineNormalizer(Normalizer):

    CANDLE_WS_COLUMNS = ["ts", "open", "high", "low", "close", "volume", "quote_volume", "volCcyQuote", "is_closed"]
    CANDLE_API_COLUMNS = ["ts", "open", "high", "low", "close", "volume", "quote_volume", "volCcyQuote", "is_closed"]

    @classmethod
    def api(cls, data: Union[Dict[str, Any], List], **kwargs):
        source = kwargs.get('source', 'okx')
        symbol = kwargs.get("symbol")
        timeframe = kwargs.get('timeframe')

        candle_data = dict(source=source, s=symbol, i=timeframe.string_tf)
        for c, k in zip(cls.CANDLE_API_COLUMNS, data):
            candle_data[c] = k

        candle_data["ts"] = int(candle_data["ts"]) // 1000

        timeframe_minutes = int(timeframe.tf)
        timeframe_seconds = timeframe_minutes * 60
        candle_data["T"] = (candle_data["ts"] + timeframe_seconds) - 1

        return Kline(**candle_data)

    @classmethod
    def ws(cls, data: Dict[str, Any]) -> Kline:

        symbol, timeframe = _ws_get_symbol_and_timeframe(data=data)

        kline = data["data"][0]

        candle_data = dict(source="okx", s=symbol, i=timeframe.string_tf)

        for c, k in zip(cls.CANDLE_WS_COLUMNS, kline):
            candle_data[c] = k

        candle_data["ts"] = int(candle_data["ts"]) // 1000

        timeframe_minutes = int(timeframe.tf)
        timeframe_seconds = timeframe_minutes * 60
        candle_data["T"] = (candle_data["ts"] + timeframe_seconds) - 1

        return Kline(**candle_data)