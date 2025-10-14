import asyncio
import contextlib
from streamforge.ingestion.binance.ws.ws import BinanceWS


import asyncio
import logging
from streamforge.base.stream_input import DataInput
from streamforge.ingestion.binance.runner import BinanceRunner
from streamforge.ingestion.kraken.runner import KrakenRunner
from streamforge.ingestion.okx.runner import OKXRunner

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


async def merge_streams(*handlers):
    queue = asyncio.Queue()

    async def forward(handler):
        async for item in handler.stream():
            await queue.put(item)

    tasks = [asyncio.create_task(forward(h)) for h in handlers]

    try:
        while True:
            item = await queue.get()
            yield item
    finally:
        for t in tasks:
            t.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await asyncio.gather(*tasks)


# async def main():
#     binance_input = DataInput(
#                 type="kline",
#                 symbols=["btcusdt", "ethusdt"],
#                 timeframe="1m",
#                 aggregate_list=["5m", "15m"]
#             )
#     binance_runner = BinanceRunner(stream_input=binance_input)
#     kraken_input = DataInput(
#         type="ohlc",
#         symbols=["BTC/USD","ETH/USD"],
#         timeframe="1m",
#         aggregate_list=[
#             #"5m",
#             "15m"
#         ]
#     )
#     kraken_runner = KrakenRunner(stream_input=kraken_input)
#     okx_input = DataInput(
#         type="candle",
#         symbols=["BTC-USDT", "ETH-USDT"],
#         timeframe="1m",
#         aggregate_list=["5m", "15m"]
#     )
#     okx_runner = OKXRunner(stream_input=okx_input)
#
#     async for data in merge_streams(
#             binance_runner,
#             kraken_runner,
#             okx_runner
#     ):
#         test = data
#
#
# asyncio.run(main())
