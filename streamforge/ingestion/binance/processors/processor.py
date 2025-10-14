from abc import ABC, abstractmethod
from streamforge.base.data_processor.processor import GeneralProcessor
from streamforge.ingestion.binance.processors.kline import BinanceCandleProcessor

binance_processors_map = {
    "candle": BinanceCandleProcessor,
    "kline": BinanceCandleProcessor,
    "ohlc": BinanceCandleProcessor
}


class BinanceProcessor(GeneralProcessor):

    def __init__(self,
                 processors_map=binance_processors_map,
                 emit_only_closed_candles: bool = True,):
        super().__init__(processors_map, emit_only_closed_candles=emit_only_closed_candles)

    async def process_data(self, data, raw_data):

        channel_type = raw_data["data"]["e"]

        if processor := self._processors_map.get(channel_type):
            async for processed in processor.process_data(data=data):
                yield processed
        else:
            raise NotImplementedError(f'Stream Type: {channel_type}. Normalizer not implemented.')