"""
Bybit OHLC/Kline data normalizer.

Converts Bybit-specific data formats to StreamForge's standardized Kline model.
"""

from streamforge.base.normalize.normalize import Normalizer
from streamforge.base.normalize.ohlc.models.candle import Kline
from streamforge.ingestion.bybit.normalizers.util import adjust_bybit_timestamps
from streamforge.ingestion.bybit.util import get_streamforge_timeframe, get_timeframe_seconds
from streamforge.ingestion.bybit.normalizers.util import get_timestamp_precision
from typing import Union, Dict, Any, List


class KlineNormalizer(Normalizer):
    """
    Normalizer for Bybit kline/candlestick data.
    
    Handles both REST API (array format) and WebSocket (object format) data.
    """

    SOURCE = "bybit"

    # Bybit API returns array format: [startTime, open, high, low, close, volume, turnover]
    API_KLINES_COLUMNS = [
        "t",  # [0] startTime (ms)
        "o",  # [1] open
        "h",  # [2] high
        "l",  # [3] low
        "c",  # [4] close
        "v",  # [5] volume
        "q",  # [6] turnover (quote_volume)
    ]

    def api(self, data: Union[Dict[str, Any], List], **kwargs):
        """
        Normalize Bybit REST API kline data (array format).
        
        Args:
            data: Array format [startTime, open, high, low, close, volume, turnover]
            **kwargs: Must include 'symbol' and 'timeframe'
            
        Returns:
            Kline object with normalized data
        """
        source = kwargs.get('source', 'bybit')
        symbol = kwargs.get("symbol")
        timeframe = kwargs.get('timeframe')
        timeframe_seconds = get_timeframe_seconds(timeframe)

        start_timestamp = data[0]
        start_timestamp = int(start_timestamp) // get_timestamp_precision(start_timestamp)
        end_timestamp = start_timestamp + timeframe_seconds
        end_timestamp = end_timestamp - 1

        # Map array indices to Kline fields
        candle_data = {
            "source": source,
            "s": symbol,
            "i": timeframe,
            "t": start_timestamp,  # startTime (ms)
            "T": end_timestamp,  # endTime (ms)
            "o": float(data[1]),  # open
            "h": float(data[2]),  # high
            "l": float(data[3]),  # low
            "c": float(data[4]),  # close
            "v": float(data[5]),  # volume
            "q": float(data[6]),  # turnover (quote_volume)
        }

        return Kline(**candle_data)

    def ws(self, data: Dict[str, Any]) -> Kline:
        """
        Normalize Bybit WebSocket kline message.
        
        Bybit WebSocket format:
        {
            "topic": "kline.1.BTCUSDT",
            "type": "snapshot" or "delta",
            "ts": 1672304486868,
            "data": [{
                "start": 1672304400000,
                "end": 1672304459999,
                "interval": "1",
                "open": "16578.50",
                "close": "16578.00",
                "high": "16578.50",
                "low": "16578.00",
                "volume": "2.081",
                "turnover": "34481.1270",
                "confirm": false
            }]
        }
        
        Args:
            data: WebSocket message dictionary
            
        Returns:
            Kline object with normalized data
        """
        if "data" not in data or not data["data"] or len(data["data"]) == 0:
            return None

        
        topic = data.get("topic", "")

        if "kline" in topic:
            kline_obj = data["data"][0]
            topic_parts = topic.split(".")

            kline_obj["source"] = self.SOURCE
            kline_obj.update({"s": topic_parts[2], # Symbol
            "i": get_streamforge_timeframe(topic_parts[1])} # Timeframe
            )

        
        # Convert timestamps from milliseconds to seconds before returning

        return Kline(**adjust_bybit_timestamps(data=kline_obj))

