import logging
from typing import List
from streamforge.base.models import BaseKlineBuffer, BaseAggregateTF
from .util import adjust_timestamp, get_first_index
from streamforge.base.normalize.ohlc.models.timeframes import BaseTimeframe, TIMEFRAME_CLASS_MAP
#from streamforge.ingestion.normalize.ohlc.models.candle import Kline
from streamforge.base.normalize.ohlc.models.candle import Kline


class AggregateTF(BaseAggregateTF):
    def __init__(self, timeframe: BaseTimeframe, target_timeframes: List[str]):
        self.timeframe = TIMEFRAME_CLASS_MAP[timeframe]
        self.target_timeframes = self._process_target_timeframes(timeframes_list=target_timeframes)

    def _process_target_timeframes(self, timeframes_list):
        timeframes_to_agg = []

        for tf in timeframes_list:
            try:
                tf_class = TIMEFRAME_CLASS_MAP[tf]
                if ((tf_class % self.timeframe)  == 0) and (tf_class > self.timeframe):
                    timeframes_to_agg.append(tf_class)
                else:
                    logging.warning(f"Data in timeframe '{self.timeframe.string_tf}' cannot be aggregated to '{tf_class.string_tf}'. "
                                    f"Aggregation for this timeframe dropped.")
            except KeyError:
                logging.error(f"'{tf}' Timeframe does not exist, dropping data timeframe.")

            except Exception:
                logging.error(f"Not possible to aggregate '{tf}'.")

        return timeframes_to_agg

    def timeframes_to_aggregate(self, timestamp):
        ts = timestamp + 1

        for tf in self.target_timeframes:
            if (ts % tf.offset) == 0:
                yield tf

    def aggregate(self, base_data: BaseKlineBuffer, timeframe: BaseTimeframe, ref_timestamp: int | float):

        target_ts = adjust_timestamp(timestamp=ref_timestamp, offset=timeframe.offset)

        first_index = get_first_index(base_data, target_ts)
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
            "q": first_data.quote_volume,
            "count": 1,
        }

        for data_point in base_data.data[first_index+1:]:

            candle_base["h"] = max(candle_base["h"], data_point.high)
            candle_base["l"] = min(candle_base["l"], data_point.low)
            candle_base["v"] += data_point.volume
            candle_base["q"] += data_point.quote_volume
            candle_base["c"] = data_point.close
            candle_base["count"] += 1

        return Kline(**candle_base)

    @property
    def is_empty(self):
        return False if self.target_timeframes else True
