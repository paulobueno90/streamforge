"""
Binance exchange runner.

This module provides the BinanceRunner class for streaming real-time
market data from Binance exchange.
"""

from streamforge.base.runner import Runner
from streamforge.ingestion.binance.ws.ws import BinanceWS
from streamforge.ingestion.binance.processors.processor import BinanceProcessor
from streamforge.base.stream_input import DataInput


class BinanceRunner(Runner):
    """
    Runner for Binance exchange data ingestion.
    
    BinanceRunner provides a simple interface for streaming real-time market data
    from Binance, including kline/candlestick data, with support for multiple
    timeframe aggregation and various output formats.
    
    Args:
        stream_input: DataInput configuration specifying what to stream
        websocket_client: WebSocket handler class (default: BinanceWS)
        processor_class: Data processor class (default: BinanceProcessor)
        source: Exchange name (default: "Binance")
        active_warmup: Whether to fetch historical data on startup (default: True)
        emit_warmup: Whether to emit warmup data to outputs (default: False)
        emit_only_closed_candles: Only emit completed candles (default: True)
        verbose: Enable verbose logging (default: False)
        
    Examples:
        Basic usage:
        >>> import asyncio
        >>> from streamforge.ingestion.binance.runner import BinanceRunner
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
        ...     runner = BinanceRunner(stream_input=stream)
        ...     
        ...     # Add CSV output
        ...     runner.register_emitter(CSVEmitter(file_path="btc_1m.csv"))
        ...     
        ...     # Start streaming
        ...     await runner.run()
        >>> 
        >>> asyncio.run(main())
        
        With aggregation:
        >>> stream = DataInput(
        ...     type="kline",
        ...     symbols=["BTCUSDT", "ETHUSDT"],
        ...     timeframe="1m",
        ...     aggregate_list=["5m", "15m", "1h"]
        ... )
        >>> runner = BinanceRunner(stream_input=stream, active_warmup=True)
        >>> await runner.run()
    
    Note:
        Binance WebSocket streams are free and don't require API keys for
        public market data. Rate limits apply for API calls during warmup.
    """
    def __init__(
            self,
            stream_input: DataInput,
            websocket_client=BinanceWS,
            processor_class=BinanceProcessor,
            source="Binance",
            active_warmup=True,
            emit_warmup=False,
            emit_only_closed_candles=True,
            verbose=False,

    ):
        super().__init__(
            websocket_client=websocket_client,
            processor_class=processor_class,
            source="Binance",
            active_warmup=active_warmup,
            emit_warmup=emit_warmup,
            emit_only_closed_candles=emit_only_closed_candles,
            verbose=verbose,
        )

        self.set_stream_input(ws_input=stream_input)


