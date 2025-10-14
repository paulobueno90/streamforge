"""
WebSocket handler module for real-time data streaming.

This module provides the WebsocketHandler abstract base class for managing
WebSocket connections to cryptocurrency exchanges, handling reconnections,
and coordinating data normalization and processing.
"""

import asyncio
import inspect
import orjson
import logging
import websockets
from typing import Type, Optional, Dict, Union, List, ClassVar, AnyStr, Any
from abc import ABC, abstractmethod
from streamforge.base.stream_input import DataInput
from streamforge.base.normalize.normalize import GeneralNormalizers
from streamforge.base.emitters.base import EmitterHolder
from streamforge.base.data_processor.processor import GeneralProcessor


class SubscribeError(Exception):
    """Raised when WebSocket subscription fails."""
    pass


class WebsocketHandler(ABC):
    """
    Abstract base class for handling WebSocket connections to exchanges.
    
    WebsocketHandler manages the lifecycle of WebSocket connections including:
    - Establishing and maintaining connections
    - Automatic reconnection on failures
    - Subscribing to data streams
    - Normalizing incoming data
    - Processing and emitting data
    
    Attributes:
        _source: Exchange name (e.g., 'Binance', 'Kraken')
        _url: WebSocket URL endpoint
        _ws_input: Stream configuration(s)
        emitter_holder: Container for output emitters
        processor: Data processor instance
        stream_types: List of subscribed stream types
        
    Examples:
        >>> # Typically used via exchange-specific implementations
        >>> handler = BinanceWS(
        ...     streams=DataInput(type="kline", symbols=["BTCUSDT"], timeframe="1m"),
        ...     processor_class=BinanceProcessor
        ... )
        >>> await handler.run()
    
    Note:
        This is an abstract base class. Use exchange-specific implementations
        like BinanceWS, KrakenWS, or OKXWS.
    """
    _warmup_required = ["kline","candle","ohlc","ohlcv"]
    _WS_STREAM_NAME_MAP: Dict[str, str]

    def __init__(self,
                 source: str,
                 streams: Union[DataInput, List[DataInput]],
                 websocket_url: str,
                 normalizer_class: GeneralNormalizers,
                 processor_class: GeneralProcessor,
                 emit_only_closed_candles: bool = True,
                 ):

        self._source = source.title()
        self._url = websocket_url
        self._ws_input = streams
        self._params = self._get_params(ws_input=streams)
        self._sleep_time = 5

        self.emitter_holder = None
        self.processor = processor_class
        self._normalizer = normalizer_class
        self._stream_types = self._get_stream_types()
        self._emit_only_closed_candles = emit_only_closed_candles

        self.start_processors(data_input=self._ws_input)

    @abstractmethod
    def _get_params(self, ws_input: DataInput) -> Dict[str, Any]:
        pass

    @property
    def url(self):
        return self._url

    def start_processors(self, data_input: DataInput, emit_only_closed_candles: bool = True):
        self.processor.init_processors(data_input=data_input)

    async def set_emitter(self, emitter_holder: EmitterHolder):
        self.emitter_holder = emitter_holder
        await self.emitter_holder.connect()
        return None

    def _get_stream_types(self):
        stream_types = []
        if isinstance(self._ws_input, list):
            for stream in self._ws_input:
                stream_types.append(stream.type)
        elif isinstance(self._ws_input, DataInput):
            stream_types.append(self._ws_input.type)
        else:
            raise ValueError(f"Stream Input in the wrong type.")

        return stream_types

    async def warmup(self):
        await self.processor.warmup(stream_types=self._stream_types)

    async def run(self):

        async for websocket in websockets.connect(self.url):

            await websocket.send(orjson.dumps(self._params).decode())

            try:

                logging.info(f"{self._source:<{10}} | Subscribed Successful to params: {self._params} | "
                             f"Websocket Input: {self._ws_input}.")

                logging.info(f"{self._source:<{10}} | Websocket Connection established successfully!")

                while True:
                    message = await websocket.recv()
                    data = orjson.loads(message)

                    normalized_data = self._normalizer.ws(data=data)
                    if normalized_data is None:
                        continue

                    async for processed in self.processor.process_data(data=normalized_data, raw_data=data):
                        logging.info(f"{self._source:<{10}} | Data Received: {processed}")
                        await self.emitter_holder.emit(processed)

            except websockets.exceptions.ConnectionClosed:
                logging.warning(f"Connection closed. Attempting to reconnect...")
                continue

            except asyncio.TimeoutError:
                logging.warning("Connection timed out. Attempting to reconnect...")
                continue

            except Exception as e:
                logging.error(f"An unexpected error occurred: {e}. Reconnecting...")
                raise Exception(e)

    async def stream(self):
        """
        Stream processed data as an async generator with automatic reconnection.
        
        This method continuously yields normalized and processed data from the
        WebSocket connection. It automatically handles reconnections on failures,
        connection drops, or timeouts.
        
        Yields:
            Processed data items (type depends on stream type, typically Kline for OHLC data)
            
        Note:
            This method runs indefinitely with automatic reconnection logic.
            Use asyncio.timeout() or similar to limit execution time.
        """
        while True:  # reconnect loop
            try:
                async for websocket in websockets.connect(self.url):
                    # send subscription params
                    await websocket.send(orjson.dumps(self._params).decode())

                    logging.info(f"{self._source:<{10}} | Subscribed successfully: {self._params}")
                    logging.info(f"{self._source:<{10}} | Connection established.")

                    while True:  # recv loop
                        message = await websocket.recv()
                        data = orjson.loads(message)

                        normalized_data = self._normalizer.ws(data=data)
                        if normalized_data is None:
                            continue

                        async for processed in self.processor.process_data(
                                data=normalized_data,
                                raw_data=data
                        ):
                            logging.info(f"{self._source:<{10}} | Data Received: {processed}")

                            yield processed

            except websockets.exceptions.ConnectionClosed:
                logging.warning(f"{self._source:<{10}} | Connection closed. Reconnecting in {self._sleep_time}s...")
                await asyncio.sleep(self._sleep_time)

            except asyncio.TimeoutError:
                logging.warning(f"{self._source:<{10}} | Timeout. Reconnecting in {self._sleep_time}s...")
                await asyncio.sleep(self._sleep_time)

            except Exception as e:
                logging.error(f"{self._source:<{10}} | Unexpected error: {e}. Reconnecting in {self._sleep_time}s...")
                await asyncio.sleep(self._sleep_time)

    @property
    def stream_types(self):
        return self._stream_types
