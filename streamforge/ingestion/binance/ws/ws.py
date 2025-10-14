import asyncio
import inspect
import orjson
import logging
import websockets

# DataInput is imported below from base.stream_input
from streamforge.ingestion.binance.normalizers.normalizer import binance_normalizer


from typing import Type, Optional, Dict, Union, List, ClassVar, AnyStr, Any
from streamforge.base.ws import WebsocketHandler
from streamforge.base.stream_input import DataInput
from streamforge.base.normalize.normalize import GeneralNormalizers
from streamforge.base.data_processor.processor import GeneralProcessor

from streamforge.ingestion.binance.processors.processor import BinanceProcessor




logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


class WebsocketParameters:
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

    @classmethod
    def _check_input(cls, stream_input):
        if not stream_input.type:
            raise ValueError("Input expects a key named 'type'")
        elif stream_input.type.lower() not in ["trade", "aggtrade", "klines", "kline", "candle", "ohlcv", "ohlc"]:
            raise ValueError(f"Stream type '{stream_input.type}' is not a valid type or is not implemented.")
        else:
            return stream_input

    @classmethod
    def _parse_input(cls, stream_input):

        if stream_input.type == "trade":
            return [cls.STREAMS_MAP["trade"].format(symbol) for symbol in stream_input.symbols]
        elif stream_input.type == "aggtrade":
            return [cls.STREAMS_MAP["aggTrade"].format(symbol) for symbol in stream_input.symbols]
        elif stream_input.type in ["klines", "kline", "candle", "ohlcv", "ohlc"]:
            return [cls.STREAMS_MAP["kline"].format(symbol.lower(), stream_input.timeframe) for symbol in stream_input.symbols]
        else:
            raise NotImplementedError(f"Stream type '{stream_input.type}' not implemented or does not exist.")

    @classmethod
    def build_params(cls, ws_input: DataInput):
        params = cls._parse_input(cls._check_input(stream_input=ws_input))

        return {
            "method": 'SUBSCRIBE',
            "params": params,
            "id": 999
        }


class SubscribeError(Exception):
    pass


class BinanceWS(WebsocketHandler):

    def __init__(self,

                 streams: Union[DataInput, List[DataInput]],

                 normalizer_class: GeneralNormalizers = binance_normalizer,
                 processor_class: GeneralProcessor = BinanceProcessor(),
                 websocket_url: str = "wss://stream.binance.com:9443/stream",
                 source: str = "Binance",

                 ):

        super().__init__(
            source=source,
            streams=streams,
            normalizer_class=normalizer_class,
            processor_class=processor_class,
            websocket_url=websocket_url,
        )

    def _get_params(self, ws_input: DataInput):
        return WebsocketParameters.build_params(ws_input=ws_input)

