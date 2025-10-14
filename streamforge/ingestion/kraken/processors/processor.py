from abc import ABC, abstractmethod
from streamforge.base.data_processor.processor import GeneralProcessor
from streamforge.ingestion.kraken.processors.ohlc import KrakenCandleProcessor

kraken_processors_map = {
    "candle": KrakenCandleProcessor,
    "kline": KrakenCandleProcessor,
    "ohlc": KrakenCandleProcessor
}


class KrakenProcessor(GeneralProcessor):

    def __init__(self, processors_map=kraken_processors_map,
                 emit_only_closed_candles: bool = True):
        super().__init__(processors_map, emit_only_closed_candles=emit_only_closed_candles)

    async def process_data(self, data, raw_data):

        channel_type = raw_data.get("channel")

        if processor := self._processors_map.get(channel_type):
            async for processed in processor.process_data(data=data):
                yield processed
        else:
            raise NotImplementedError(f'Stream Type: {channel_type}. Normalizer not implemented.')