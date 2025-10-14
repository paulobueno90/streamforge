import logging
from streamforge.base.models import BaseKlineBuffer, WarmupConfigurationError


def check_offset(data, offset):
    if len(data) == 1:
        return True
    for i in range(1, len(data)):
        if (data[i] - data[i - 1]) != offset:
            return False
    return True


def check_aggregation_setup(warmup_active, streams_input):
    if streams_input.aggregate_list:
        if not warmup_active:
            raise WarmupConfigurationError()
        else:
            return True
    else:
        return False


def config_aggregation(streams_input, aggregate_cls, warmup_active):

    if check_aggregation_setup(warmup_active=warmup_active, streams_input=streams_input):

        agg_obj = aggregate_cls(timeframe=streams_input.timeframe, target_timeframes=streams_input.aggregate_list)

        if agg_obj.is_empty:
            logging.info(f"Aggregation Could not be initiated for timeframes: {streams_input.aggregate_list}")
            logging.info("Aggregation Deactivated")
            return None
        else:
            logging.info(f"Aggregation Activated for: {[tf.string_tf for tf in agg_obj.target_timeframes]}")
            return agg_obj
    else:
        logging.info("Aggregation Deactivated")
        return None


def timestamp_ms_to_s(timestamp):
    return timestamp // 1000


def adjust_timestamp(timestamp, offset):
    return (timestamp + 1) - offset


def get_first_index(base_data: BaseKlineBuffer, target_ts: int):
    for i, data in enumerate(base_data.data):
        if data.open_ts == target_ts:
            return i

