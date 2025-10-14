from abc import ABC, abstractmethod
import logging
from typing import Dict, Any, List
from streamforge.base.normalize.ohlc.models.candle import Kline
from streamforge.base.normalize.ohlc.models.timeframes import BaseTimeframe, TIMEFRAME_CLASS_MAP
from streamforge.base.data_container.ohlc import CandleData


def adjust_timestamp(timestamp, offset):
    return (timestamp + 1) - offset


def get_first_index(base_data: CandleData, target_ts: int):

    for i, data in enumerate(base_data.data):
        if data.open_ts == target_ts:
            return i


def number_of_datapoints(base_timeframe: str, target_timeframe: str):
    base_tf = TIMEFRAME_CLASS_MAP[base_timeframe]
    target_tf = TIMEFRAME_CLASS_MAP[target_timeframe]
    return target_tf.offset // base_tf.offset


class BaseAggregateTF(ABC):

    @abstractmethod
    def __init__(self, *args, **kwargs):
        pass

    @property
    @abstractmethod
    def is_empty(self) -> bool:
        pass

    @abstractmethod
    def aggregate(self, base_data, timeframe, ref_timestamp):
        pass


class AggregateTF(BaseAggregateTF):

    def __init__(
            self,
            source: str,
            timeframe: BaseTimeframe,
            target_timeframes: List[str],
            tf_5m_force_included: bool = False
    ):
        self.source = source
        self.tf_5m_force_included = tf_5m_force_included
        self.timeframe = TIMEFRAME_CLASS_MAP[timeframe]
        self.target_timeframes = self._process_target_timeframes(timeframes_list=target_timeframes)

    def _process_target_timeframes(self, timeframes_list):
        timeframes_to_agg = []

        for tf in timeframes_list:
            try:
                tf_class = TIMEFRAME_CLASS_MAP[tf]
                if ((tf_class % self.timeframe) == 0) and (tf_class > self.timeframe):
                    timeframes_to_agg.append(tf_class)
                else:
                    logging.warning(f"{self.source.title():<{10}} | Data in timeframe '{self.timeframe.string_tf}' "
                                    f"cannot be aggregated to '{tf_class.string_tf}'. "
                                    f"Aggregation for this timeframe dropped.")
            except KeyError:
                logging.error(f"{self.source.title():<{10}} | '{tf}' Timeframe does not exist, dropping data timeframe.")

            except Exception:
                logging.error(f"{self.source.title():<{10}} | Not possible to aggregate '{tf}'.")

        return timeframes_to_agg

    def timeframes_to_aggregate(self, timestamp):
        """Determine which timeframes should be aggregated at this timestamp"""
        ts = timestamp + 1

        for tf in self.target_timeframes:
            if (ts % tf.offset) == 0:
                yield tf

    def aggregate(self, base_data: CandleData, timeframe: BaseTimeframe, ref_timestamp: int | float):
        pass
        """Aggregate data from base timeframe to target timeframe"""
        target_ts = adjust_timestamp(timestamp=ref_timestamp, offset=timeframe.offset)
        first_index = get_first_index(base_data, target_ts)

        if first_index is None:
            return None

        first_data = base_data.data[first_index]

        candles_necessary = number_of_datapoints(
            base_timeframe=base_data.timeframe.string_tf,
            target_timeframe=timeframe.string_tf
        )

        # Create base candle structure
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
            "vwap": first_data.vwap if first_data.vwap else None,
            "n": first_data.n_trades if first_data.n_trades else 1,
        }

        # Aggregate remaining data points
        for data_point in base_data.data[first_index + 1:first_index + candles_necessary]:
            candle_base["h"] = max(candle_base["h"], data_point.high)
            candle_base["l"] = min(candle_base["l"], data_point.low)
            candle_base["v"] += data_point.volume
            candle_base["c"] = data_point.close

            # Update VWAP (volume weighted average price)
            if data_point.vwap and candle_base["vwap"]:
                # Simple VWAP calculation - in practice, you might want more sophisticated logic
                total_volume = candle_base["v"]
                if total_volume > 0:
                    candle_base["vwap"] = ((candle_base["vwap"] * (candle_base["v"] - data_point.volume)) +
                                           (data_point.vwap * data_point.volume)) / total_volume

            candle_base["n"] += data_point.n_trades if data_point.n_trades else 0

        return Kline(**candle_base)

    @property
    def is_empty(self):
        return False if self.target_timeframes else True
