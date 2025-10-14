import orjson
from typing import List


WS_STREAM_NAME_MAP = {
    "kline":"kline",
    "klines":"kline",
    "aggtrade":"aggtrade",
    "trade":"trade",
}

STREAMS_MAP = {
    "trade": "{}@trade",
    "aggTrade": "{}@aggTrade",
    "kline": "{}@kline_{}",  # 1m, 5m, 1h, 1d, etc.
    "candle": "{}@kline_{}",
    "ohlcv": "{}@kline_{}",
    "miniTicker": "{}@miniTicker",
    "ticker": "{}@ticker",
    "all_tickers": "!ticker@arr",

}

def parse_input(stream_input):

    if stream_input.type == "trade":
        return [STREAMS_MAP["trade"].format(symbol) for symbol in stream_input.symbols]
    elif stream_input.type == "aggtrade":
        return [STREAMS_MAP["aggTrade"].format(symbol) for symbol in stream_input.symbols]
    elif stream_input.type in ["klines","kline", "candle", "ohlcv", "ohlc"]:
        return [STREAMS_MAP["kline"].format(symbol, stream_input.timeframe) for symbol in stream_input.symbols]
    else:
        raise NotImplementedError(f"Stream type '{stream_input.type}' not implemented or does not exist.")

def get_params(stream_input):
    params = parse_input(check_input(stream_input=stream_input))

    return {
        "method": 'SUBSCRIBE',
        "params": params,
        "id": 999
    }

def check_input(stream_input):
    if not stream_input.type:
        raise KeyError("Input expects a key named 'type'")
    elif stream_input.type.lower() not in ["trade", "aggtrade", "klines", "kline", "candle", "ohlcv", "ohlc"]:
        raise ValueError(f"Stream type '{stream_input.type}' is not a valid type or is not implemented.")
    else:
        return stream_input





def get_streams(streams):

    if isinstance(streams, list):

        base_list = []
        for stream_input in streams:
            parsed_streams = parse_input(check_input(stream_input=stream_input))
            base_list.extend(parsed_streams)

        return base_list

    else:
        return parse_input(check_input(stream_input=streams))


def parse_input(stream_input):

    if stream_input.type == "trade":
        return [STREAMS_MAP["trade"].format(symbol) for symbol in stream_input.symbols]
    elif stream_input.type == "aggtrade":
        return [STREAMS_MAP["aggTrade"].format(symbol) for symbol in stream_input.symbols]
    elif stream_input.type in ["klines","kline", "candle", "ohlcv", "ohlc"]:
        return [STREAMS_MAP["kline"].format(symbol, stream_input.timeframe) for symbol in stream_input.symbols]
    else:
        raise NotImplementedError(f"Stream type '{stream_input.type}' not implemented or does not exist.")

def get_params(stream_input):
    params = parse_input(check_input(stream_input=stream_input))

    return {
        "method": 'SUBSCRIBE',
        "params": params,
        "id": 999
    }


def base_url(streams):
    if len(streams) == 1:
        return "wss://stream.binance.com:9443/ws/"
    else:
        return "wss://stream.binance.com:9443/stream?streams="


def multi_stream_data(message):
    return orjson.loads(message)["data"]


def single_stream_data(message):
    return orjson.loads(message)