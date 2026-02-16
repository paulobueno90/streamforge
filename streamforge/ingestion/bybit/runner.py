"""
Bybit exchange runner.

This module provides the BybitRunner class for streaming real-time
market data from Bybit exchange.
"""

from typing import Optional
from streamforge.base.runner import Runner
from streamforge.ingestion.bybit.ws.ws import BybitWS
from streamforge.ingestion.bybit.processors.processor import BybitProcessor
from streamforge.base.stream_input import DataInput


class BybitRunner(Runner):
    """
    Runner for Bybit exchange data ingestion.
    
    BybitRunner provides a simple interface for streaming real-time market data
    from Bybit, including kline/candlestick data, with support for multiple
    timeframe aggregation and various output formats.
    
    Supports Spot, Linear (USDT/USDC perpetuals), and Inverse futures markets.
    
    Args:
        stream_input: DataInput configuration specifying what to stream
        websocket_client: WebSocket handler class (default: BybitWS)
        processor_class: Data processor class (default: BybitProcessor)
        source: Exchange name (default: "Bybit")
        active_warmup: Whether to fetch historical data on startup (default: True)
        emit_warmup: Whether to emit warmup data to outputs (default: False)
        emit_only_closed_candles: Only emit completed candles (default: True)
        verbose: Enable verbose logging (default: False)
        market_type: Market type - SPOT, LINEAR, or INVERSE (default: "SPOT")
        
    Examples:
        Basic usage (Spot):
        >>> import asyncio
        >>> from streamforge.ingestion.bybit.runner import BybitRunner
        >>> from streamforge.base.stream_input import DataInput
        >>> from streamforge.base.emitters import CSVEmitter
        >>> 
        >>> async def main():
        ...     # Configure stream
        ...     stream = DataInput(
        ...         type="kline",
        ...         symbols=["BTCUSDT"],
        ...         timeframe="1m"
        ...     )
        ...     
        ...     # Create runner
        ...     runner = BybitRunner(stream_input=stream)
        ...     
        ...     # Add CSV output
        ...     runner.register_emitter(CSVEmitter(file_path="btc_1m.csv"))
        ...     
        ...     # Start streaming
        ...     await runner.run()
        >>> 
        >>> asyncio.run(main())
        
        Linear futures:
        >>> stream = DataInput(
        ...     type="kline",
        ...     symbols=["BTCUSDT"],
        ...     timeframe="1m"
        ... )
        >>> runner = BybitRunner(stream_input=stream, market_type="LINEAR")
        >>> await runner.run()
        
        With aggregation:
        >>> stream = DataInput(
        ...     type="kline",
        ...     symbols=["BTCUSDT", "ETHUSDT"],
        ...     timeframe="1m",
        ...     aggregate_list=["5m", "15m", "1h"]
        ... )
        >>> runner = BybitRunner(stream_input=stream, active_warmup=True)
        >>> await runner.run()
    
    Note:
        Bybit WebSocket streams are free and don't require API keys for
        public market data. Rate limits apply for API calls during warmup.
        Bybit uses topic-based subscriptions (e.g., "kline.1.BTCUSDT").
    """
    
    def __init__(
            self,
            stream_input: DataInput,
            websocket_client=BybitWS,
            processor_class=BybitProcessor,
            source="Bybit",
            active_warmup=True,
            emit_warmup=False,
            emit_only_closed_candles=True,
            verbose=False,
            market_type: Optional[str] = 'SPOT',
    ):
        super().__init__(
            websocket_client=websocket_client,
            processor_class=processor_class,
            source=source,
            active_warmup=active_warmup,
            emit_warmup=emit_warmup,
            emit_only_closed_candles=emit_only_closed_candles,
            verbose=verbose,
            market_type=market_type,
        )

        self.set_stream_input(ws_input=stream_input)
        self._market_type = market_type  # Store for use in _init_run

    async def _init_run(self):
        """
        Initialize WebSocket client with market_type parameter.
        
        Overrides base class to pass market_type to BybitWS.
        """
        self._check_input()

        # Pass market_type to BybitWS
        self.ws_client = self.ws_client(
            streams=self._ws_input,
            processor_class=self._processor_class,
            market_type=self._market_type
        )

        await self.ws_client.set_emitter(emitter_holder=self._emitter_holder)

        await self.warmup_run()

