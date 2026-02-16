"""
Bybit general normalizer for routing messages to appropriate normalizers.
"""

from streamforge.base.normalize.normalize import GeneralNormalizers, Normalizer
from streamforge.ingestion.bybit.normalizers.ohlc import KlineNormalizer
from typing import Union, Dict, Any, List
from streamforge.base.normalize.ohlc.models.candle import Kline


normalizer_map = {
    "kline": KlineNormalizer(),
    "ohlc": KlineNormalizer(),
    "ohlcv": KlineNormalizer()
}


class BybitNormalizers(GeneralNormalizers):
    """
    General normalizer for Bybit exchange data.
    
    Routes messages to appropriate normalizers based on topic type.
    Bybit uses topic-based subscriptions (e.g., "kline.1.BTCUSDT").
    """

    CANDLE_WS_COLUMNS = ["ts", "open", "high", "low", "close", "volume", "quote_volume", "volCcyQuote", "is_closed"]

    def api(self, data: Union[Dict[str, Any], List], **kwargs):
        """
        Normalize Bybit REST API response.
        
        Args:
            data: API response data (array format for klines)
            **kwargs: Must include 'data_type', 'symbol', and 'timeframe'
            
        Returns:
            Normalized Kline object
        """
        data_type = kwargs.get('data_type', 'kline')
        if normalizer := self._normalizers_map.get(data_type):
            symbol = kwargs.get("symbol")
            timeframe = kwargs.get("timeframe")
            return normalizer.api(data=data, symbol=symbol, timeframe=timeframe)
        else:
            raise NotImplementedError(f'Stream Type: {data_type}. Normalizer not implemented.')

    def ws(self, data: Dict[str, Any]) -> Union[Kline, None]:
        """
        Normalize Bybit WebSocket message.
        
        Bybit uses topic-based messages. Topic format: "kline.{interval}.{symbol}"
        
        Args:
            data: WebSocket message dictionary with 'topic' and 'data' fields
            
        Returns:
            Normalized Kline object or None if message should be skipped
        """
        

        


        
        topic = data.get("topic", "")
        
        
        # Map stream types to normalizer
        if "kline" in topic:
            if normalizer := self._normalizers_map.get("kline"):
                return normalizer.ws(data)
        
        # Return None for unsupported stream types (don't raise error, just skip)
        return None


bybit_normalizer = BybitNormalizers(normalizers_map=normalizer_map)

