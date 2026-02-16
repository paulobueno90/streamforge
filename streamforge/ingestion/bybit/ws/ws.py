"""
Bybit WebSocket handler for real-time market data streaming.
"""

import asyncio
import orjson
import websockets
from typing import Optional, Dict, Union, List

from streamforge.base.ws import WebsocketHandler
from streamforge.base.stream_input import DataInput
from streamforge.base.normalize.normalize import GeneralNormalizers
from streamforge.base.data_processor.processor import GeneralProcessor
from streamforge.ingestion.bybit.normalizers.normalizer import bybit_normalizer
from streamforge.ingestion.bybit.processors.processor import BybitProcessor
from streamforge.ingestion.bybit.ws.util import build_subscription_args, check_input
from streamforge.ingestion.bybit.util import MARKET_TYPE_STRING_MAP, MARKET_TYPE_PATH_MAP


class WebsocketParameters:
    """
    Helper class for building Bybit WebSocket subscription parameters.
    """
    
    MARKET_TYPE_STRING_MAP = {
        "DEFAULT": "SPOT",
        "SPOT": "SPOT",
        "LINEAR": "LINEAR",
        "INVERSE": "INVERSE",
        "FUTURES (LINEAR)": "LINEAR",
        "FUTURES (INVERSE)": "INVERSE",
    }

    MARKET_TYPE_URL_MAP = {
        "SPOT": "wss://stream.bybit.com/v5/public/spot",
        "LINEAR": "wss://stream.bybit.com/v5/public/linear",
        "INVERSE": "wss://stream.bybit.com/v5/public/inverse",
        "DEFAULT": "wss://stream.bybit.com/v5/public/spot",
    }

    @classmethod
    def build_params(cls, ws_input: DataInput):
        """
        Build Bybit WebSocket subscription parameters.
        
        Bybit format: {"op": "subscribe", "args": ["kline.1.BTCUSDT"]}
        
        Args:
            ws_input: DataInput object with type, symbols, and timeframe
            
        Returns:
            Dictionary with subscription parameters
        """
        validated_input = check_input(stream_input=ws_input)
        args = build_subscription_args(stream_input=validated_input)
        
        return {
            "op": "subscribe",
            "args": args
        }

    @classmethod
    def get_url(cls, market_type: str):
        """
        Get WebSocket URL for the specified market type.
        
        Args:
            market_type: Market type string (SPOT, LINEAR, INVERSE, etc.)
            
        Returns:
            WebSocket URL string
        """
        market_type_string = cls.MARKET_TYPE_STRING_MAP.get(market_type.upper(), "DEFAULT")
        return cls.MARKET_TYPE_URL_MAP.get(market_type_string, "wss://stream.bybit.com/v5/public/spot")


class BybitWS(WebsocketHandler):
    """
    WebSocket handler for Bybit exchange.
    
    Manages WebSocket connections, subscriptions, and message handling
    for Bybit Spot, Linear, and Inverse markets.
    """

    def __init__(self,
                 streams: Union[DataInput, List[DataInput]],
                 normalizer_class: GeneralNormalizers = bybit_normalizer,
                 processor_class: GeneralProcessor = None,
                 source: str = "Bybit",
                 market_type: Optional[str] = 'SPOT',
                 ):
        """
        Initialize Bybit WebSocket handler.
        
        Args:
            streams: DataInput or list of DataInput objects
            normalizer_class: Normalizer class for data conversion
            processor_class: Processor class for data processing (will be instantiated with market_type)
            source: Exchange name (default: "Bybit")
            market_type: Market type - SPOT, LINEAR, or INVERSE (default: "SPOT")
        """
        websocket_url = WebsocketParameters.get_url(market_type=market_type)
        
        # Instantiate processor with market_type if it's a class
        if processor_class is None:
            processor_class = BybitProcessor(market_type=market_type)
        elif isinstance(processor_class, type):
            # If it's a class, instantiate it with market_type
            processor_class = processor_class(market_type=market_type)
        elif hasattr(processor_class, '_market_type'):
            # If it's already an instance, update market_type
            processor_class._market_type = market_type

        super().__init__(
            source=source,
            streams=streams,
            normalizer_class=normalizer_class,
            processor_class=processor_class,
            websocket_url=websocket_url,
        )
        
        self._market_type = market_type
        self._ping_interval = 30  # Send ping every 30 seconds

    def _get_params(self, ws_input: DataInput):
        """
        Get subscription parameters for WebSocket connection.
        
        Args:
            ws_input: DataInput object
            
        Returns:
            Dictionary with subscription parameters
        """
        return WebsocketParameters.build_params(ws_input=ws_input)

    async def _handle_ping_pong(self, websocket):
        """
        Handle ping/pong messages to keep connection alive.
        
        Bybit requires periodic ping messages (every 30 seconds recommended).
        """
        while True:
            await asyncio.sleep(self._ping_interval)
            try:
                ping_msg = {"op": "ping"}
                await websocket.send(orjson.dumps(ping_msg).decode())
            except Exception as e:
                # Connection closed, exit ping loop
                break

    async def run(self):
        """
        Run WebSocket connection with automatic reconnection.
        
        Overrides base class to add ping/pong handling.
        """
        ping_task = None
        
        async for websocket in websockets.connect(self.url):
            # Start ping task
            ping_task = asyncio.create_task(self._handle_ping_pong(websocket))
            
            # Send subscription
            params = self._get_params(ws_input=self._ws_input)
            await websocket.send(orjson.dumps(params).decode())

            try:
                from streamforge.base.config import config
                config.logger.info(f"{self._source:<{10}} | Subscribed Successful to params: {params} | "
                             f"Websocket Input: {self._ws_input}.")
                config.logger.info(f"{self._source:<{10}} | Websocket Connection established successfully!")

                while True:
                    message = await websocket.recv()
                    data = orjson.loads(message)
                    
                    # Skip subscription confirmations and pong messages
                    if data.get("op") == "subscribe" or data.get("op") == "pong":
                        if data.get("success"):
                            config.logger.info(f"{self._source:<{10}} | Subscription confirmed: {data}")
                        continue

                    normalized_data = self._normalizer.ws(data=data)
                    if normalized_data is None:
                        continue

                    async for processed in self.processor.process_data(data=normalized_data, raw_data=data):
                        config.logger.info(f"{self._source:<{10}} | Data Received: {processed}")
                        await self.emitter_holder.emit(processed)

            except websockets.exceptions.ConnectionClosed:
                if ping_task:
                    ping_task.cancel()
                from streamforge.base.config import config
                config.logger.warning(f"{self._source:<{10}} | Connection closed. Attempting to reconnect...")
                continue

            except asyncio.TimeoutError:
                if ping_task:
                    ping_task.cancel()
                from streamforge.base.config import config
                config.logger.warning(f"{self._source:<{10}} | Connection timed out. Attempting to reconnect...")
                continue

            except Exception as e:
                if ping_task:
                    ping_task.cancel()
                from streamforge.base.config import config
                config.logger.error(f"{self._source:<{10}} | An unexpected error occurred: {e}. Reconnecting...")
                raise Exception(e)

    async def stream(self):
        """
        Stream processed data as an async generator with automatic reconnection.
        
        Overrides base class to add ping/pong handling.
        """
        ping_task = None
        
        while True:  # reconnect loop
            try:
                async for websocket in websockets.connect(self.url):
                    # Start ping task
                    ping_task = asyncio.create_task(self._handle_ping_pong(websocket))
                    
                    # Send subscription
                    params = self._get_params(ws_input=self._ws_input)
                    await websocket.send(orjson.dumps(params).decode())

                    from streamforge.base.config import config
                    config.logger.info(f"{self._source:<{10}} | Subscribed successfully: {params}")
                    config.logger.info(f"{self._source:<{10}} | Connection established.")

                    while True:  # recv loop
                        message = await websocket.recv()
                        data = orjson.loads(message)
                        
                        # Skip subscription confirmations and pong messages
                        if data.get("op") == "subscribe" or data.get("op") == "pong":
                            if data.get("success"):
                                config.logger.info(f"{self._source:<{10}} | Subscription confirmed: {data}")
                            continue

                        normalized_data = self._normalizer.ws(data=data)
                        if normalized_data is None:
                            continue

                        async for processed in self.processor.process_data(
                                data=normalized_data,
                                raw_data=data
                        ):
                            config.logger.info(f"{self._source:<{10}} | Data Received: {processed}")
                            yield processed

            except websockets.exceptions.ConnectionClosed:
                if ping_task:
                    ping_task.cancel()
                from streamforge.base.config import config
                config.logger.warning(f"{self._source:<{10}} | Connection closed. Reconnecting in {self._sleep_time}s...")
                await asyncio.sleep(self._sleep_time)

            except asyncio.TimeoutError:
                if ping_task:
                    ping_task.cancel()
                from streamforge.base.config import config
                config.logger.warning(f"{self._source:<{10}} | Timeout. Reconnecting in {self._sleep_time}s...")
                await asyncio.sleep(self._sleep_time)

            except Exception as e:
                if ping_task:
                    ping_task.cancel()
                from streamforge.base.config import config
                config.logger.error(f"{self._source:<{10}} | Unexpected error: {e}. Reconnecting in {self._sleep_time}s...")
                await asyncio.sleep(self._sleep_time)
