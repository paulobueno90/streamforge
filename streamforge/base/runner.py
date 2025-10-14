"""
Base runner module for orchestrating data ingestion.

This module provides the Runner abstract base class which coordinates WebSocket
connections, data processing, and output emission for cryptocurrency data streams.
"""

import logging
from abc import ABC
from pydantic import BaseModel
from sqlalchemy.orm import declarative_base
from typing import Dict, Union, List, Optional

from streamforge.base.emitters.base import DataEmitter, EmitterHolder
from streamforge.base.data_processor.processor import GeneralProcessor
from streamforge.base.ws import WebsocketHandler
from streamforge.base.stream_input import DataInput

Base = declarative_base()


class Runner(ABC):
    """
    Abstract base class for running data ingestion pipelines.
    
    Runner orchestrates the entire data flow: connecting to WebSocket streams,
    processing incoming data, and emitting results to configured outputs.
    It handles warmup (fetching historical data), reconnection logic, and
    manages the lifecycle of processors and emitters.
    
    Attributes:
        _ws_input: DataInput configuration for the stream
        _emitter_holder: Container holding all registered data emitters
        _allowed_warmup_list: Stream types that support warmup/historical data
        ws_client: WebSocket handler for exchange connection
        
    Examples:
        >>> # Subclass example (see BinanceRunner for concrete implementation)
        >>> runner = BinanceRunner()
        >>> stream_input = DataInput(type="kline", symbols=["BTCUSDT"], timeframe="1m")
        >>> runner.set_stream_input(stream_input)
        >>> runner.register_emitter(CSVEmitter("output.csv"))
        >>> await runner.run()
    
    Note:
        This is an abstract base class. Use exchange-specific implementations
        like BinanceRunner, KrakenRunner, or OKXRunner.
    """

    _ws_input = None
    _emitter_holder = EmitterHolder()
    _allowed_warmup_list = ["klines", "kline", "candle", "candles", "ohlc", "ohlcv"]

    def __init__(
            self,
            websocket_client: WebsocketHandler,
            processor_class: GeneralProcessor,
            source: str,
            active_warmup=True,
            emit_warmup=False,
            emit_only_closed_candles=True,
            verbose=False,


    ):
        self.ws_client = websocket_client
        self._processor_class = processor_class(emit_only_closed_candles=emit_only_closed_candles)

        self._active_warmup = active_warmup
        self._emit_warmup = emit_warmup
        self._emit_only_closed_candles = emit_only_closed_candles

    def set_stream_input(self, ws_input: DataInput):
        """
        Configure the data stream to subscribe to.
        
        Args:
            ws_input: DataInput object specifying symbol, type, and timeframe
        """
        self._ws_input = ws_input

    def register_emitter(
            self,
            emitter: DataEmitter,
            model: Optional[Union[Base, BaseModel]] = None,
            map_object: Optional[Dict] = None
    ):
        """
        Register an output emitter for processed data.
        
        Multiple emitters can be registered to output data to different
        destinations simultaneously (e.g., CSV file + PostgreSQL + Kafka).
        
        Args:
            emitter: DataEmitter instance (CSVEmitter, PostgresEmitter, KafkaEmitter, etc.)
            model: Optional data model for structured outputs (SQLAlchemy or Pydantic)
            map_object: Optional column mapping dictionary for custom field names
            
        Examples:
            >>> runner.register_emitter(CSVEmitter("output.csv"))
            >>> runner.register_emitter(PostgresEmitter(connection_string="..."))
        """
        self._emitter_holder.add(emitter=emitter, data_model=model, columns_map=map_object)

    def _check_input(self):
        if self._ws_input is None:
            raise ValueError("Websocket StreamInput Missing")

        if self._ws_input.type in self._allowed_warmup_list:
            if not self._ws_input.aggregate_list:
                if not self._emit_warmup:
                    self._active_warmup = False

    async def warmup_run(self):
        """
        Execute warmup phase by fetching historical data.
        
        Warmup fetches recent historical data from current date to initialize
        processors and enable immediate aggregation calculations. This is particularly
        useful when aggregating from smaller to larger timeframes.
        
        The warmup data can optionally be emitted to outputs if emit_warmup=True.
        """
        if self._active_warmup:
            if self._emit_warmup:
                for stream_type in self.ws_client.stream_types:
                    if stream_type in self._allowed_warmup_list:
                        async for kline_data in self.ws_client.processor.emit_warmup():
                            await self.ws_client.emitter_holder.emit(kline_data)
            else:
                for stream_type in self.ws_client.stream_types:
                    if stream_type in self._allowed_warmup_list:
                        await self.ws_client.warmup()
        else:
            return None

    async def _init_run(self):

        self._check_input()

        self.ws_client = self.ws_client(streams=self._ws_input, processor_class=self._processor_class)

        await self.ws_client.set_emitter(emitter_holder=self._emitter_holder)

        await self.warmup_run()

    async def run(self):
        """
        Start the data ingestion pipeline and run indefinitely.
        
        This method initializes the WebSocket connection, performs warmup if configured,
        and begins streaming data. It will run continuously with automatic reconnection
        until interrupted.
        
        Raises:
            ValueError: If stream input is not configured
            ConnectionError: If initial connection fails
            
        Examples:
            >>> runner = BinanceRunner()
            >>> runner.set_stream_input(DataInput(type="kline", symbols=["BTCUSDT"], timeframe="1m"))
            >>> await runner.run()  # Runs indefinitely
        """
        await self._init_run()
        await self.ws_client.run()

    async def stream(self):
        """
        Stream processed data as an async generator.
        
        Alternative to run() that yields data items instead of emitting them.
        Useful for custom processing or merging multiple streams.
        
        Yields:
            Processed data items (typically Kline objects)
            
        Examples:
            >>> runner = BinanceRunner()
            >>> runner.set_stream_input(DataInput(type="kline", symbols=["BTCUSDT"], timeframe="1m"))
            >>> async for kline in runner.stream():
            ...     print(f"BTC Price: {kline.close}")
        """
        await self._init_run()
        async for data in self.ws_client.stream():
            yield data