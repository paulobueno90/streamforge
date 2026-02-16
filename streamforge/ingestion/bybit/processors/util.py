"""
Bybit processor utilities for data validation and aggregation setup.
"""

from streamforge.base.models import BaseKlineBuffer, WarmupConfigurationError
from streamforge.base.config import config


def check_offset(data, offset):
    """
    Check if data points have consistent offset intervals.
    
    Args:
        data: List of timestamps
        offset: Expected offset in seconds
        
    Returns:
        True if all intervals match the offset, False otherwise
    """
    if len(data) == 1:
        return True
    for i in range(1, len(data)):
        if (data[i] - data[i - 1]) != offset:
            return False
    return True


def check_aggregation_setup(warmup_active, streams_input):
    """
    Check if aggregation is properly configured.
    
    Args:
        warmup_active: Whether warmup is active
        streams_input: DataInput object with aggregation settings
        
    Returns:
        True if aggregation is properly configured, False otherwise
        
    Raises:
        WarmupConfigurationError: If aggregation is requested but warmup is not active
    """
    if streams_input.aggregate_list:
        if not warmup_active:
            raise WarmupConfigurationError()
        else:
            return True
    else:
        return False


def config_aggregation(streams_input, aggregate_cls, warmup_active):
    """
    Configure timeframe aggregation.
    
    Args:
        streams_input: DataInput object with aggregation settings
        aggregate_cls: Aggregate class to use
        warmup_active: Whether warmup is active
        
    Returns:
        Aggregate object if configured, None otherwise
    """
    if check_aggregation_setup(warmup_active=warmup_active, streams_input=streams_input):
        agg_obj = aggregate_cls(timeframe=streams_input.timeframe, target_timeframes=streams_input.aggregate_list)

        if agg_obj.is_empty:
            config.logger.info(f"Aggregation Could not be initiated for timeframes: {streams_input.aggregate_list}")
            config.logger.info("Aggregation Deactivated")
            return None
        else:
            config.logger.info(f"Aggregation Activated for: {[tf.string_tf for tf in agg_obj.target_timeframes]}")
            return agg_obj
    else:
        config.logger.info("Aggregation Deactivated")
        return None


def timestamp_ms_to_s(timestamp):
    """
    Convert timestamp from milliseconds to seconds.
    
    Args:
        timestamp: Timestamp in milliseconds
        
    Returns:
        Timestamp in seconds
    """
    return timestamp // 1000


def adjust_timestamp(timestamp, offset):
    """
    Adjust timestamp to align with timeframe boundaries.
    
    Args:
        timestamp: Timestamp to adjust
        offset: Timeframe offset in seconds
        
    Returns:
        Adjusted timestamp
    """
    return (timestamp + 1) - offset


def get_first_index(base_data: BaseKlineBuffer, target_ts: int):
    """
    Get the first index in buffer where open_ts matches target timestamp.
    
    Args:
        base_data: BaseKlineBuffer instance
        target_ts: Target timestamp in seconds
        
    Returns:
        Index of matching data point, or None if not found
    """
    for i, data in enumerate(base_data.data):
        if data.open_ts == target_ts:
            return i
    return None

