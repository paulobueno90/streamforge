"""
Stream vs Run - Understanding the Two Main Patterns
===================================================

StreamForge offers two ways to consume data:
1. run() - Automatic emission to registered emitters
2. stream() - Manual iteration with full control

Prerequisites:
- streamforge installed

When to use which:
- Use run() when: You want data automatically saved to outputs
- Use stream() when: You need custom logic per data point

Run:
    python stream_vs_run.py
"""

import asyncio
import streamforge as sf

from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String, Float, BigInteger


class KlineTable(Base):
    """
    SQLAlchemy ORM Model for Kline/Candlestick Data
    
    Must match your database table structure
    """
    __tablename__ = 'klines'
    
    # Primary key components
    source = Column(String, primary_key=True)
    symbol = Column(String, primary_key=True)
    timeframe = Column(String, primary_key=True)
    open_ts = Column(BigInteger, primary_key=True)
    
    # Data fields
    end_ts = Column(BigInteger)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Float)


# Create PostgreSQL emitter
postgres_emitter = sf.PostgresEmitter(
    host="localhost",
    dbname="crypto",
    user="postgres",
    password="mysecretpassword",
    port=5432
)

# Set the ORM model
postgres_emitter.set_model(KlineTable, inplace=True)



async def pattern1_run():
    """
    Pattern 1: run() - Automatic Emission
    
    Best for: Straightforward data pipelines where you just want to
    save/forward data to outputs (CSV, database, Kafka, etc.)
    """
    print("\n" + "="*60)
    print("PATTERN 1: Using run() for automatic emission")
    print("="*60)
    
    runner = sf.BinanceRunner(
        stream_input=sf.DataInput(
            type="kline",
            symbols=["BTCUSDT"],
            timeframe="1m"
        )
    )
    
    
    # Register emitter
    runner.register_emitter(postgres_emitter)
    
    # This runs forever and automatically emits to all registered emitters
    await runner.run()


async def pattern2_stream():
    """
    Pattern 2: stream() - Manual Iteration
    
    Best for: Custom logic, filtering, alerts, or when you need
    to decide what to do with each data point
    """
    print("\n" + "="*60)
    print("PATTERN 2: Using stream() for manual control")
    print("="*60)
    
    runner = sf.BinanceRunner(
        stream_input=sf.DataInput(
            type="kline",
            symbols=["BTCUSDT"],
            timeframe="1m"
        )
    )
    
    # No emitters registered - we'll handle data manually
    
    async for kline in runner.stream():
        # Custom logic for each data point
        price = kline.close
        
        # Example: Only log when price crosses certain thresholds
        if price > 50000:
            print(f"🚀 BTC above $50k! Current: ${price:,.2f}")
        elif price < 30000:
            print(f"📉 BTC below $30k! Current: ${price:,.2f}")
        else:
            print(f"📊 BTC: ${price:,.2f}")
        
        # You could also:
        # - Save to database conditionally
        # - Send alerts
        # - Trigger trades
        # - Calculate custom indicators
        # - Forward to different outputs based on conditions


async def pattern3_stream_with_emitter():
    """
    Pattern 3: Hybrid - Stream with Conditional Emission
    
    Best for: When you want both control and automatic saving
    """
    print("\n" + "="*60)
    print("PATTERN 3: Hybrid approach - conditional saving")
    print("="*60)
    
    runner = sf.BinanceRunner(
        stream_input=sf.DataInput(
            type="kline",
            symbols=["BTCUSDT", "ETHUSDT"],
            timeframe="1m"
        )
    )
    
    # Note: Use sf.config.logger for internal logging
    # Or create a custom emitter if you need to log data items
    
    async for kline in runner.stream():
        # Calculate price change
        price_change_pct = ((kline.close - kline.open) / kline.open) * 100
        
        # Only save data if there's significant movement
        if abs(price_change_pct) > 0.5:  # More than 0.5% change
            print(f"📈 {kline.symbol}: {price_change_pct:+.2f}% - Saving to output")
            await postgres_emitter.emit(kline)
        else:
            print(f"😴 {kline.symbol}: {price_change_pct:+.2f}% - Skipping (too small)")


async def pattern4_merge_streams():
    """
    Pattern 4: Merge Multiple Streams
    
    Best for: Combining data from multiple exchanges or symbols
    """
    print("\n" + "="*60)
    print("PATTERN 4: Merging multiple exchange streams")
    print("="*60)
    
    # Create runners for different exchanges
    binance_runner = sf.BinanceRunner(
        stream_input=sf.DataInput(
            type="kline",
            symbols=["BTCUSDT"],
            timeframe="1m"
        )
    )
    
    okx_runner = sf.OKXRunner(
        stream_input=sf.DataInput(
            type="candle",
            symbols=["BTC-USDT"],
            timeframe="1m"
        )
    )
    
    # Merge streams from both exchanges
    from streamforge.merge_stream import merge_streams
    
    async for data in merge_streams(binance_runner, okx_runner):
        print(f"📡 Data from {data.source}: ${data.close:,.2f}")


# Choose which pattern to run
async def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║          StreamForge: stream() vs run() Patterns            ║
╚══════════════════════════════════════════════════════════════╝

Choose a pattern to demonstrate:
1. run() - Automatic emission to registered emitters
2. stream() - Manual iteration with custom logic
3. Hybrid - Stream with conditional emission
4. Merge - Combine multiple exchange streams

Press Ctrl+C to stop any demo
""")
    
    # Uncomment ONE pattern to run:
    
    # await pattern1_run()
    # await pattern2_stream()
    await pattern3_stream_with_emitter()
    # await pattern4_merge_streams()


if __name__ == "__main__":
    asyncio.run(main())

