"""
Hello World - Simplest StreamForge Example
==========================================

This is the absolute simplest way to use StreamForge.
It streams live Bitcoin price data and prints it to console.

Prerequisites:
- None! Just install streamforge

What it does:
- Connects to Binance WebSocket
- Streams 1-minute BTC/USDT candlestick data
- Prints each candle to console

Run:
    python hello_world.py
"""

import asyncio
import streamforge as sf


async def main():
    # Configure what data to stream
    stream_input = sf.DataInput(
        type="kline",           # Type of data (kline = candlestick)
        symbols=["BTCUSDT"],    # Bitcoin/USDT trading pair
        timeframe="1m"          # 1-minute candles
    )
    
    # Create a runner for Binance
    runner = sf.BinanceRunner(stream_input=stream_input)
    
    # Note: Internal logging is handled by sf.config.logger
    # You can customize it: sf.config.logger = your_logger
    # Or stream and log yourself
    
    # Start streaming (runs forever until Ctrl+C)
    await runner.run()

if __name__ == "__main__":
    asyncio.run(main())

