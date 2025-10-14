from typing import Dict, Any
from abc import ABC

#from streamforge.base.normalize.normalize import OHLCDataNormalizer


class ExchangeInterface(ABC):

    _ws_url = None
    _candle_ws_columns = None
    #_candle_normalizer: OHLCDataNormalizer = None

    @property
    def ws_url(self):
        return self._ws_url

    @property
    def ws_candle_columns(self):
        return self._candle_ws_columns

    def parse_candle_ws(self, data: Dict[str, Any]):
        return self._candle_normalizer.normalize_candle_ws(data=data)

