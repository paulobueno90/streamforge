import warnings


class LimitedData(Warning):
    pass


def timeframe_warning(tf_offset: int):
    if tf_offset == 60:
        warnings.warn(
            "Kraken API calls are limited to 720 datapoints. "
            "This means that '1m' timeframe warmup might be incomplete for aggregation.",
            LimitedData,
            stacklevel=2
        )