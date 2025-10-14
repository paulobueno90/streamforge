from abc import ABC, abstractmethod
from streamforge.base.data_processor.processor import GeneralProcessor
from streamforge.ingestion.okx.processors.candle import OkxCandleProcessor

okx_processors_map = {
    "candle":OkxCandleProcessor,
    "kline":OkxCandleProcessor,
    "ohlc":OkxCandleProcessor
}


class OkxProcessor(GeneralProcessor):

    def __init__(self, processors_map=okx_processors_map,
                 emit_only_closed_candles: bool = True):
        super().__init__(processors_map, emit_only_closed_candles=emit_only_closed_candles)

    async def process_data(self, data, raw_data):
        channel_type = raw_data["arg"]["channel"]
        if "candle" in channel_type:
            channel_type = "candle"

        if processor := self._processors_map.get("candle"):
            async for processed in processor.process_data(data=data):
                yield processed
        else:
            raise NotImplementedError(f'Stream Type: {channel_type}. Normalizer not implemented.')

