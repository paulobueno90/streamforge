from typing import Type, Optional, Dict, Union, List, ClassVar, AnyStr, Any
from streamforge.base.ws import WebsocketHandler
from streamforge.base.stream_input import DataInput
from streamforge.base.emitters.base import EmitterHolder
from streamforge.base.data_processor.ohlc import CandleProcessor
from streamforge.base.data_processor.processor import GeneralProcessor
from streamforge.base.normalize.normalize import GeneralNormalizers
from streamforge.ingestion.okx.processors.processor import OkxProcessor
from streamforge.ingestion.okx.normalizers.normalizer import okx_normalizer


class WebsocketParameters:

    _candle_type_names = {"kline", "candle", "ohlc", "ohlcv"}

    @classmethod
    def _build_candle_params(cls, ws_input):
        params = []
        timeframe = ws_input.timeframe
        for symbol in ws_input.symbols:
            symbol_input = {
                "channel": "candle" + timeframe,
                "instId": symbol
            }
            params.append(symbol_input)

        return {
            "op": "subscribe",
            "args": params
        }

    @classmethod
    def build_params(cls, ws_input: DataInput):
        ws_type = ws_input.type
        if ws_type in cls._candle_type_names:
            return cls._build_candle_params(ws_input=ws_input)
        else:
            raise NotImplementedError(f"Type sent: {ws_type}. "
                                      f"For now the only types supported are: {cls._candle_type_names}")


class OkxWS(WebsocketHandler):

    def __init__(self,

                 streams: Union[DataInput, List[DataInput]],
                 normalizer_class: GeneralNormalizers = okx_normalizer,
                 processor_class: GeneralProcessor = OkxProcessor(),
                 websocket_url: str = 'wss://ws.okx.com:8443/ws/v5/business',
                 source: str = "OKX",

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





