import asyncio
import streamforge as sf


bybit_input = sf.DataInput(
        type="kline",
        symbols=["BTCUSDT", "ETHUSDT", "SOLUSDT"],
        timeframe="1m",
        aggregate_list=["5m", "15m"]
    )
bybit_runner = sf.BybitRunner(stream_input=bybit_input, market_type="SPOT")


async def main():
    async for data in bybit_runner.stream():
        print(data) # Do whatever you prefer

asyncio.run(main())

