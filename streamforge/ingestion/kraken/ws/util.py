

WS_STREAM_NAME_MAP = {
    "kline":"ohlc",
    "ohlc":"ohlc",
    "klines":"ohlc",
    "ohlcv":"ohlc",
    "aggtrade":"aggtrade",
    "trade":"trade",
    "trades":"trades",
    "level3": "level3",
    "book": "book",
    "orderbook": "book",
    "ticker": "ticker",
    "tickers": "ticker"
}


TIMEFRAMES_MAP = {
    "1m": 1,
    "5m": 5,
    "15m": 15,
    "30m": 30,
    "1h": 60,
    "4h": 240,
    "1d": 1440,
}


def get_stream_type_name(name):
    if (name.lower() == "kline") or (name.lower() == "ohlcv") or (name.lower() == "ohlc"):
        return "ohlc"
    #TODO Implement other stream formats
    else:
        raise ValueError(f"Invalid stream input: {name}.")


def get_timeframe(tf):
    timeframe_output = TIMEFRAMES_MAP.get(tf.lower())
    if timeframe_output is None:
        raise ValueError(f"Timeframe invalid: {tf}. Must be: '1m', '5m', '15m', '30m', '1h','4h' or '1d'.")
    return timeframe_output


from pydantic import BaseModel, field_validator
from typing import List, Optional

class DataInput(BaseModel):
    type: str
    pairs: List[str]
    timeframe: str
    aggregate_list: Optional[List[str]] = []

    @field_validator("pairs")
    def validate_pairs(cls, v: List[str]) -> List[str]:
        for pair in v:
            if pair.count("/") != 1:
                raise ValueError(f"Invalid pair format: {pair}. Must contain exactly one '/'. "
                                 f"Example: BTC and USD -> BTC/USD")
        return v


def create_stream_params_v1(ws_input: DataInput):
    stream_name = get_stream_type_name(ws_input.type)
    timeframe = get_timeframe(ws_input.timeframe)

    return {
        "event": "subscribe",
        "pair": ws_input.pairs,
        "subscription": {"name": stream_name, "interval": timeframe}
    }


def create_stream_params_v2(ws_input: DataInput):
    stream_name = get_stream_type_name(ws_input.type)
    timeframe = get_timeframe(ws_input.timeframe)

    return {
    "method": "subscribe",
    "params": {
        "channel": stream_name,
        "symbol": ws_input.pairs,
        "interval": timeframe
    }
    }