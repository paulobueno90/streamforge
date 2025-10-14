import logging
from typing import List
from datetime import datetime, timezone

from streamforge.base.models import API_KLINES_COLUMNS, BaseKlineBuffer, WarmupConfigurationError
from streamforge.base.normalize.ohlc.processor import OHLCDatNormalizer
from streamforge.base.normalize.ohlc.models.candle import Kline
from streamforge.base.normalize.ohlc.models.timeframes import BaseTimeframe, TIMEFRAME_CLASS_MAP


TIMEFRAMES_5M_REQUIRED_AGG = {"15m", "30m", "1h", "4h", "1d"}


def parse_api_ohlc_item(ohlc: list, symbol: str, timeframe: BaseTimeframe, timestamp: int, source: str = "kraken"):
    """Parse Kraken OHLC data item into Kline object"""

    for ohlc_data in ohlc:
        if ohlc_data[0] < timestamp:
            continue
        candle_data = dict(source=source, s=symbol, i=timeframe.string_tf)

        # Map Kraken OHLC data to our Kline structure
        # Kraken format: [time, open, high, low, close, vwap, volume, count]
        for c, k in zip(API_KLINES_COLUMNS, ohlc_data):
            candle_data[c] = k

        # Calculate end timestamp (Kraken only provides start time)
        # We need to add the timeframe duration to get end time
        timeframe_minutes = int(timeframe.tf)
        timeframe_seconds = timeframe_minutes * 60
        candle_data["T"] = candle_data["t"] + timeframe_seconds

        yield OHLCDatNormalizer.normalize_kraken(candle_data)


def check_offset(data, offset):
    """Check if data has consistent time intervals"""
    if len(data) == 1:
        return True
    for i in range(1, len(data)):
        if (data[i] - data[i - 1]) != offset:
            return False
    return True


def check_aggregation_setup(warmup_active, streams_input):
    """Check if aggregation setup is valid"""
    if streams_input.aggregate_list:
        if not warmup_active:
            raise WarmupConfigurationError()
        else:
            return True
    else:
        return False


def handle_aggregate_list(base_tf: str, aggregate_list: List[str]):

    force_5m = False

    agg_set = set(aggregate_list)
    if base_tf == "1m":
        if (agg_set & TIMEFRAMES_5M_REQUIRED_AGG) and ("5m" not in agg_set):
            aggregate_list.insert(0, "5m")
            force_5m = True
            logging.warning("Kraken | Timeframe '5 minutes' included in warmup and processing because '1 minute' "
                            "warmup might have missing data due to API limitations.")

    return aggregate_list, force_5m


def config_aggregation(streams_input, aggregate_cls, warmup_active):
    """Configure aggregation based on stream input"""
    if check_aggregation_setup(warmup_active=warmup_active, streams_input=streams_input):

        aggregate_list, force_5m = handle_aggregate_list(
                                            base_tf=streams_input.timeframe,
                                            aggregate_list=streams_input.aggregate_list
                                            )

        agg_obj = aggregate_cls(
            timeframe=streams_input.timeframe,
            target_timeframes=aggregate_list,
            tf_5m_force_included=force_5m
        )

        if agg_obj.is_empty:
            logging.info(f"Aggregation Could not be initiated for timeframes: {streams_input.aggregate_list}")
            logging.info("Aggregation Deactivated")
            return None
        else:
            logging.info(f"Aggregation Activated for: {[tf.tf for tf in agg_obj.target_timeframes]}")
            return agg_obj
    else:
        logging.info("Aggregation Deactivated")
        return None


def get_start_timestamp():
    daily_multiplier = (24 * 60 * 60)
    utc_timestamp_now = int(datetime.now(timezone.utc).timestamp())
    return (utc_timestamp_now // daily_multiplier) * daily_multiplier


def adjust_timestamp(timestamp, offset):
    return (timestamp + 1) - offset


def get_first_index(base_data: BaseKlineBuffer, target_ts: int):

    for i, data in enumerate(base_data.data):
        if data.open_ts == target_ts:
            return i


def get_map_key(base_tf: str, timeframe: BaseTimeframe, datapoint: Kline):

    map_key = datapoint.map_key()
    if (base_tf == "1m") and (timeframe.string_tf in TIMEFRAMES_5M_REQUIRED_AGG):
        return map_key.replace("1m", "5m")
    else:
        return map_key


def number_of_datapoints(base_timeframe: str, target_timeframe: str):
    base_tf = TIMEFRAME_CLASS_MAP[base_timeframe]
    target_tf = TIMEFRAME_CLASS_MAP[target_timeframe]
    return target_tf.offset // base_tf.offset


def filter_timestamp(ohlc_data_array: list, timestamp: int):
    for ohlc_data in ohlc_data_array:
        if ohlc_data[0] > timestamp:
            yield ohlc_data
