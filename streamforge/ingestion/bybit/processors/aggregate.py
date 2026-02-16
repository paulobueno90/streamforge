"""
Bybit timeframe aggregation logic.
"""

from typing import List
from streamforge.base.models import BaseKlineBuffer, BaseAggregateTF
from streamforge.base.config import config
from .util import adjust_timestamp, get_first_index
from streamforge.base.normalize.ohlc.models.timeframes import BaseTimeframe, TIMEFRAME_CLASS_MAP
from streamforge.base.normalize.ohlc.models.candle import Kline


class AggregateTF(BaseAggregateTF):
    """
    Bybit timeframe aggregation handler.
    
    Aggregates base timeframe candles to higher timeframes (e.g., 1m → 5m, 15m, 1h).
    """
    
    def __init__(self, timeframe: BaseTimeframe, target_timeframes: List[str]):
        self.timeframe = TIMEFRAME_CLASS_MAP[timeframe]
        self.target_timeframes = self._process_target_timeframes(timeframes_list=target_timeframes)

    def _process_target_timeframes(self, timeframes_list):
        """
        Process and validate target timeframes for aggregation.
        
        Args:
            timeframes_list: List of timeframe strings to aggregate to
            
        Returns:
            List of validated timeframe classes
        """
        timeframes_to_agg = []

        for tf in timeframes_list:
            try:
                tf_class = TIMEFRAME_CLASS_MAP[tf]
                if ((tf_class % self.timeframe) == 0) and (tf_class > self.timeframe):
                    timeframes_to_agg.append(tf_class)
                else:
                    config.logger.warning(f"Data in timeframe '{self.timeframe.string_tf}' cannot be aggregated to '{tf_class.string_tf}'. "
                                    f"Aggregation for this timeframe dropped.")
            except KeyError:
                config.logger.error(f"'{tf}' Timeframe does not exist, dropping data timeframe.")

            except Exception:
                config.logger.error(f"Not possible to aggregate '{tf}'.")

        return timeframes_to_agg

    def timeframes_to_aggregate(self, timestamp):
        """
        Determine which timeframes should be aggregated at the given timestamp.
        
        Args:
            timestamp: Timestamp in seconds
            
        Yields:
            Timeframe classes that should be aggregated
        """
        ts = timestamp + 1

        for tf in self.target_timeframes:
            if (ts % tf.offset) == 0:
                yield tf

    def aggregate(self, base_data: BaseKlineBuffer, timeframe: BaseTimeframe, ref_timestamp: int | float):
        """
        Aggregate base timeframe candles to target timeframe.
        
        Args:
            base_data: BaseKlineBuffer containing base timeframe candles
            timeframe: Target timeframe to aggregate to
            ref_timestamp: Reference timestamp for aggregation
            
        Returns:
            Aggregated Kline object
        """
        target_ts = adjust_timestamp(timestamp=ref_timestamp, offset=timeframe.offset)

        first_index = get_first_index(base_data, target_ts)
        if first_index is None:
            # No data found for this timestamp
            return None
            
        first_data = base_data.data[first_index]
        candle_base = {
            "source": first_data.source,
            "s": base_data.symbol,
            "i": timeframe.string_tf,
            "t": target_ts,
            "T": ref_timestamp,
            "o": first_data.open,
            "h": first_data.high,
            "l": first_data.low,
            "c": first_data.close,
            "v": first_data.volume,
            "q": first_data.quote_volume or 0,
            "count": 1,
        }

        for data_point in base_data.data[first_index+1:]:
            if data_point.open_ts >= ref_timestamp:
                break
                
            candle_base["h"] = max(candle_base["h"], data_point.high)
            candle_base["l"] = min(candle_base["l"], data_point.low)
            candle_base["v"] += data_point.volume
            candle_base["q"] += (data_point.quote_volume or 0)
            candle_base["c"] = data_point.close
            candle_base["count"] += 1

        return Kline(**candle_base)

    @property
    def is_empty(self):
        """Check if aggregation is configured."""
        return False if self.target_timeframes else True

