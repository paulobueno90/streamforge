from abc import ABC, abstractmethod
from typing import Union, Dict, Any, List, AnyStr
from streamforge.base.normalize.ohlc.models.candle import Kline
from streamforge.base.normalize.ohlc.models.timeframes import BaseTimeframe


class BaseCandleParser(ABC):
    """Abstract base class for parsing websocket messages."""

    @abstractmethod
    def parse_message(self, message: str) -> Dict[str, Any]:
        """Parse raw websocket message."""
        pass

    @abstractmethod
    def should_process_message(self, data: Dict[str, Any], config: Union[Dict[str, Any], None]) -> bool:
        """Determine if message should be processed."""
        pass


class OHLCDataNormalizer(ABC):

    @classmethod
    @abstractmethod
    def normalize_candle_ws(cls, data: Dict[str, Any]) -> Kline | None:
        pass

    @classmethod
    @abstractmethod
    def normalize_candle_api(cls, kline: List, symbol: AnyStr, timeframe: BaseTimeframe, source: AnyStr) -> Kline:
        pass