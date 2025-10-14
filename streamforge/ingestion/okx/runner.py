"""
OKX exchange runner.

This module provides the OKXRunner class for streaming real-time
market data from OKX exchange.
"""

from streamforge.base.runner import Runner
from streamforge.ingestion.okx.ws.ws import OkxWS
from streamforge.ingestion.okx.processors.processor import OkxProcessor
from streamforge.base.stream_input import DataInput


class OKXRunner(Runner):
    """
    Runner for OKX exchange data ingestion.
    
    OKXRunner provides an interface for streaming real-time candlestick data
    from OKX exchange, with support for timeframe aggregation and multiple
    output formats.
    
    Args:
        stream_input: DataInput configuration specifying what to stream
        websocket_client: WebSocket handler class (default: OkxWS)
        processor_class: Data processor class (default: OkxProcessor)
        source: Exchange name (default: "OKX")
        active_warmup: Whether to fetch historical data on startup (default: True)
        emit_warmup: Whether to emit warmup data to outputs (default: False)
        verbose: Enable verbose logging (default: False)
        
    Examples:
        >>> import asyncio
        >>> from streamforge.ingestion.okx.runner import OKXRunner
        >>> from streamforge.base.stream_input import DataInput
        >>> 
        >>> async def main():
        ...     stream = DataInput(
        ...         type="candle",
        ...         symbols=["BTC-USDT"],
        ...         timeframe="1m"
        ...     )
        ...     runner = OKXRunner(stream_input=stream)
        ...     await runner.run()
        >>> 
        >>> asyncio.run(main())
    
    Note:
        OKX uses hyphenated symbol format (BTC-USDT) and supports
        various timeframe intervals for candlestick data.
    """
    def __init__(
            self,
            stream_input: DataInput,
            websocket_client=OkxWS,
            processor_class=OkxProcessor,
            source="OKX",
            active_warmup=True,
            emit_warmup=False,
            verbose=False,

    ):
        super().__init__(
            websocket_client=websocket_client,
            processor_class=processor_class,
            source="OKX",
            active_warmup=active_warmup,
            emit_warmup=emit_warmup,
            verbose=verbose,
        )

        self.set_stream_input(ws_input=stream_input)