from typing import Dict, Optional, Any, Union
from streamforge.base.normalize.ohlc.models.candle import Kline
from streamforge.base.normalize.normalize import Normalizer
from streamforge.base.normalize.ohlc.models.timeframes import BaseTimeframe, TIMEFRAME_CLASS_MAP


CANDLE_WS_COLUMNS = ["ts", "open", "high", "low", "close", "volume", "quote_volume", "volCcyQuote", "is_closed"]

# class OhlcCandleParser(BaseCandleParser):
#     """Abstract base class for parsing websocket messages."""
#
#     def parse_message(self, message: str) -> Dict[str, Any]:
#         """Parse raw websocket message."""
#         pass
#
#     def extract_stream_type(self, data: Dict[str, Any]) -> str:
#         pass
#
#     def should_process_message(self, data: Dict[str, Any], config: Union[Dict[str, Any], None]) -> bool:
#         if "data" in data and data["data"][0][8]:
#             return True
#         else:
#             return False
#
#     def extract_timeframe(self, data: Dict[str, Any]) -> Optional[float]:
#         pass
#
#     def extract_symbol(self, data: Dict[str, Any]) -> Optional[str]:
#         if "data" in data:
#             return data["arg"]["instId"]
#         else:
#             return None


def adjust_ms_timestamps(data: dict):
    data["t"] = data["t"] // 1000
    data["T"] = data["T"] // 1000
    return data


class OKXCandleNormalizer(Normalizer):

    def ws(self, data: Dict[str, Any]) -> Union[Kline]:
        pass


    def is_data(self, data: Dict[str, Any]) -> bool:
        if "data" in data:
            return True
        else:
            return False


    def _ws_get_symbol_and_timeframe(self, data: Dict[str, Any]) -> tuple:
        arg_metadata = data["arg"]
        symbol = arg_metadata["instId"]
        timeframe_string = arg_metadata["channel"].replace("candle", "")
        timeframe = TIMEFRAME_CLASS_MAP.get(timeframe_string)

        return symbol,timeframe

    @classmethod
    def normalize_candle_ws(cls, data: Dict[str, Any]) -> Kline | None:
        if cls.is_data(data=data):

            symbol, timeframe = cls._ws_get_symbol_and_timeframe(data=data)

            kline = data["data"][0]

            candle_data = dict(source="okx", s=symbol, i=timeframe.string_tf)

            for c, k in zip(CANDLE_WS_COLUMNS, kline):
                candle_data[c] = k

            timeframe_minutes = int(timeframe.tf)
            timeframe_seconds = timeframe_minutes * 60
            candle_data["t"] = int(candle_data["ts"])
            candle_data["T"] = candle_data["t"] + timeframe_seconds - 1

            candle_data = adjust_ms_timestamps(data=candle_data)

            return Kline(**candle_data)

        else:
            return None

    @classmethod
    def normalize_candle_api(cls, kline: list, symbol: str, timeframe: BaseTimeframe, source: str) -> Kline:
        pass




