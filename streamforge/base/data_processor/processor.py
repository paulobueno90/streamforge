"""
Data processor base classes.

This module defines abstract base classes for processing streaming market data.
Processors handle data transformation, aggregation, and validation before emission.
"""

from typing import Type, Optional, Dict, Union, List, ClassVar, AnyStr, Any
from abc import ABC, abstractmethod
from streamforge.base.normalize.ohlc.models.candle import Kline
from streamforge.base.stream_input import DataInput


class Processor(ABC):
    """
    Abstract base class for generic data processors.
    
    Processors transform and validate incoming data before it's emitted.
    """

    @abstractmethod
    def process_data(self):
        """Process incoming data."""
        pass


class CandleProcessor(ABC):
    """
    Abstract base class for candlestick/kline data processors.
    
    CandleProcessor handles OHLC data processing including aggregation,
    buffering, and timeframe conversion.
    """

    @abstractmethod
    async def process_data(self, data: Kline):
        """
        Process candlestick data.
        
        Args:
            data: Normalized Kline object
            
        Yields:
            Processed Kline objects (may include aggregated timeframes)
        """
        pass


class GeneralProcessor(ABC):
    """
    General processor coordinating multiple data type processors.
    
    GeneralProcessor manages a map of processors for different stream types
    (kline, trade, depth, etc.) and routes data to the appropriate processor.
    
    Attributes:
        WARMUP_CANDLE_TYPES: Set of stream types that support historical data warmup
        
    Note:
        Each exchange has its own GeneralProcessor implementation that defines
        which stream types are supported and how they're processed.
    """

    WARMUP_CANDLE_TYPES = {"klines", "kline", "candle", "ohlc", "olhcv"}

    def __init__(
            self,
            processors_map: Dict[str, Union[Processor, CandleProcessor, Type[Processor], Type[CandleProcessor]]],
            emit_only_closed_candles: bool = True,
    ):
        self._processors_map = processors_map
        self._emit_only_closed_candles = emit_only_closed_candles

    def init_processors(self, data_input: DataInput):

        if data_input.type in self._processors_map:
            if data_input.type in self.WARMUP_CANDLE_TYPES:

                if data_input.aggregate_list:
                    warmup_active = True
                else:
                    warmup_active = False

                self._processors_map[data_input.type] = self._processors_map[data_input.type](
                                                                stream_input=data_input,
                                                                warmup_active=warmup_active,
                                                                emit_only_closed_candles=self._emit_only_closed_candles,
                                                                )
            else:
                self._processors_map[data_input.type] = self._processors_map[data_input.type](stream_input=data_input)

        else:
            raise NotImplementedError(f"Stream Type: '{data_input.type}' is not implemented for this exchange yet.")

    async def warmup(self, stream_types):

        for s_type in self.WARMUP_CANDLE_TYPES:
            if s_type in stream_types:
                await self._processors_map[s_type].warmup()
                break

    async def emit_warmup(self, stream_types):
        for s_type in self.WARMUP_CANDLE_TYPES:
            if s_type in stream_types:
                async for data in self._processors_map[s_type].emit_warmup():
                    yield data
                return

    @abstractmethod
    async def process_data(self, data, raw_data):
        pass
