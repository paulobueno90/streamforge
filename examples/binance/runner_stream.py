import asyncio
import streamforge as sf


binance_input = sf.DataInput(
        type="kline",
        symbols=["BTCUSDT", "ETHUSDT", "SOLUSDT"],
        timeframe="1m",
        aggregate_list=["5m", "15m"]
    )
binance_runner = sf.BinanceRunner(stream_input=binance_input)


async def main():
    async for data in binance_runner.stream():
        print(data) # Do whatever you prefer

asyncio.run(main())