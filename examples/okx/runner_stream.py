import asyncio
import streamforge as sf


okx_input = sf.DataInput(
        type="candle",
        symbols=["BTC-USDT", "ETH-USDT", "SOL-USDT"],
        timeframe="1m",
        aggregate_list=["5m", "15m"]
    )
okx_runner = sf.OKXRunner(stream_input=okx_input)


async def main():
    async for data in okx_runner.stream():
        print(data) # Do whatever you prefer

asyncio.run(main())