"""
Bybit general processor for routing messages to appropriate processors.
"""

from abc import ABC, abstractmethod
from streamforge.base.data_processor.processor import GeneralProcessor
from streamforge.base.stream_input import DataInput
from streamforge.ingestion.bybit.processors.kline import BybitCandleProcessor

bybit_processors_map = {
    "candle": BybitCandleProcessor,
    "kline": BybitCandleProcessor,
    "ohlc": BybitCandleProcessor,
    "ohlcv": BybitCandleProcessor,
}


class BybitProcessor(GeneralProcessor):
    """
    General processor for Bybit exchange data.
    
    Routes messages to appropriate processors based on topic type.
    Bybit uses topic-based subscriptions (e.g., "kline.1.BTCUSDT").
    """

    def __init__(self,
                 processors_map=bybit_processors_map,
                 emit_only_closed_candles: bool = True,
                 market_type: str = "SPOT"):
        super().__init__(processors_map, emit_only_closed_candles=emit_only_closed_candles)
        self._market_type = market_type

    def init_processors(self, data_input: DataInput):
        """
        Override to pass market_type to processor instances.
        """
        if data_input.type in self._processors_map:
            if data_input.type in self.WARMUP_CANDLE_TYPES:
                if data_input.aggregate_list:
                    warmup_active = True
                else:
                    warmup_active = False

                # Pass market_type to the processor
                self._processors_map[data_input.type] = self._processors_map[data_input.type](
                    stream_input=data_input,
                    warmup_active=warmup_active,
                    emit_only_closed_candles=self._emit_only_closed_candles,
                    market_type=self._market_type
                )
            else:
                self._processors_map[data_input.type] = self._processors_map[data_input.type](
                    stream_input=data_input,
                    market_type=self._market_type
                )
        else:
            raise NotImplementedError(f"Stream Type: '{data_input.type}' is not implemented for this exchange yet.")

    async def process_data(self, data, raw_data):
        """
        Process incoming data by routing to appropriate processor.
        
        Args:
            data: Normalized data (Kline object)
            raw_data: Raw WebSocket message dictionary
            
        Yields:
            Processed data items
        """
        # Bybit uses topic-based messages
        # Topic format: "kline.{interval}.{symbol}"
        topic = raw_data.get("topic", "")
        
        if not topic:
            return
        
        # Parse topic to get stream type
        topic_parts = topic.split(".")
        if len(topic_parts) < 1:
            return
        if "kline" in raw_data.get("topic", "").lower():
            processor = self._processors_map.get("kline")
            if processor:
                async for processed in processor.process_data(data=data):
                    yield processed
            else:
                stream_type = raw_data.get("topic", "").split(".")[0].lower()
                raise NotImplementedError(f'Stream Type: {stream_type}. Processor not implemented.')
        else:
            topic = raw_data.get("topic", "").split(".")[0].lower()
            raise NotImplementedError(f'Stream Type: {topic}. Processor not implemented.')

