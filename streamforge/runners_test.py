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


# async def main():
#     logger = Logger(prefix="Binance")
#     emitter_holder = EmitterHolder()
#     emitter_holder.add(emitter=logger)
#
#     binance_input = DataInput(
#         type="kline",
#         symbols=["btcusdt", "ethusdt"],
#         timeframe="1m",
#         aggregate_list=["5m", "15m"]
#     )
#     ws_client = BinanceWS(streams=binance_input)
#     await ws_client.set_emitter(emitter_holder=emitter_holder)
#     await ws_client.warmup()
#
#     #await ws_client.run()
#     async for data in ws_client.stream():
#         print("Got:", data)


async def main():
    # binance_input = DataInput(
    #             type="kline",
    #             symbols=["btcusdt", "ethusdt"],
    #             timeframe="1m",
    #             aggregate_list=["5m", "15m"]
    #         )
    # binance_runner = BinanceRunner(stream_input=binance_input)
    # kraken_input = DataInput(
    #     type="ohlc",
    #     symbols=["BTC/USD","ETH/USD"],
    #     timeframe="1m",
    #     aggregate_list=[
    #         #"5m",
    #         "15m"
    #     ]
    # )
    # kraken_runner = KrakenRunner(stream_input=kraken_input)
    okx_input = DataInput(
        type="candle",
        symbols=["BTC-USDT", "ETH-USDT"],
        timeframe="1m",
        aggregate_list=["5m", "15m"]
    )
    okx_runner = OKXRunner(stream_input=okx_input)

    async for data in okx_runner.stream():
        print("Got:", data)


asyncio.run(main())