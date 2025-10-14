
from streamforge.base.emitters.base import EmitterHolder

from typing import Type, Optional, Dict, Union, List, ClassVar, AnyStr, Any
from streamforge.base.ws import WebsocketHandler
from streamforge.base.stream_input import DataInput
from streamforge.base.normalize.normalize import GeneralNormalizers
from streamforge.base.data_processor.processor import GeneralProcessor
from streamforge.ingestion.kraken.ws.util import TIMEFRAMES_MAP, WS_STREAM_NAME_MAP
from streamforge.ingestion.kraken.normalizers.normalizer import kraken_normalizer
from streamforge.ingestion.kraken.processors.processor import KrakenProcessor

class WebsocketParameters:

    @classmethod
    def get_stream_type_name(cls, name):
        if (name.lower() == "kline") or (name.lower() == "ohlcv") or (name.lower() == "ohlc"):
            return "ohlc"
        # TODO Implement other stream formats
        else:
            raise ValueError(f"Invalid stream input: {name}.")

    @classmethod
    def get_timeframe(cls, tf):
        timeframe_output = TIMEFRAMES_MAP.get(tf.lower())
        if timeframe_output is None:
            raise ValueError(f"Timeframe invalid: {tf}. Must be: '1m', '5m', '15m', '30m', '1h','4h' or '1d'.")
        return timeframe_output

    @classmethod
    def build_params(cls, ws_input: DataInput):
        stream_name = cls.get_stream_type_name(ws_input.type)
        timeframe = cls.get_timeframe(ws_input.timeframe)

        return {
        "method": "subscribe",
        "params": {
            "channel": stream_name,
            "symbol": ws_input.symbols,
            "interval": timeframe
        }
        }


class KrakenWS(WebsocketHandler):

    def __init__(self,

                 streams: Union[DataInput, List[DataInput]],

                 normalizer_class: GeneralNormalizers = kraken_normalizer,
                 processor_class: GeneralProcessor = KrakenProcessor(),
                 websocket_url: str = "wss://ws.kraken.com/v2",
                 source: str = "Kraken",

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

