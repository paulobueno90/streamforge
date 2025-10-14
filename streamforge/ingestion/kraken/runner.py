"""
Kraken exchange runner.

This module provides the KrakenRunner class for streaming real-time
market data from Kraken exchange.
"""

from streamforge.base.runner import Runner
from streamforge.ingestion.kraken.ws.ws import KrakenWS
from streamforge.ingestion.kraken.processors.processor import KrakenProcessor
from streamforge.base.stream_input import DataInput


class KrakenRunner(Runner):
    """
    Runner for Kraken exchange data ingestion.
    
    KrakenRunner provides an interface for streaming real-time OHLC data
    from Kraken exchange, with support for timeframe aggregation and
    multiple output formats.
    
    Args:
        stream_input: DataInput configuration specifying what to stream
        websocket_client: WebSocket handler class (default: KrakenWS)
        processor_class: Data processor class (default: KrakenProcessor)
        source: Exchange name (default: "Kraken")
        active_warmup: Whether to fetch historical data on startup (default: True)
        emit_warmup: Whether to emit warmup data to outputs (default: False)
        verbose: Enable verbose logging (default: False)
        
    Examples:
        >>> import asyncio
        >>> from streamforge.ingestion.kraken.runner import KrakenRunner
        >>> from streamforge.base.stream_input import DataInput
        >>> 
        >>> async def main():
        ...     stream = DataInput(
        ...         type="ohlc",
        ...         symbols=["BTC/USD"],
        ...         timeframe="1"  # Kraken uses minutes as integers
        ...     )
        ...     runner = KrakenRunner(stream_input=stream)
        ...     await runner.run()
        >>> 
        >>> asyncio.run(main())
    
    Note:
        Kraken uses different symbol formats (BTC/USD vs BTCUSDT) and
        timeframe representations (integer minutes vs strings like '1m').
    """
    def __init__(
            self,
            stream_input: DataInput,
            websocket_client=KrakenWS,
            processor_class=KrakenProcessor,
            source="Kraken",
            active_warmup=True,
            emit_warmup=False,
            verbose=False,

    ):
        super().__init__(
            websocket_client=websocket_client,
            processor_class=processor_class,
            source="Kraken",
            active_warmup=active_warmup,
            emit_warmup=emit_warmup,
            verbose=verbose

        )

        self.set_stream_input(ws_input=stream_input)