"""
Multi-Timeframe Aggregation - Higher Timeframe Candles
======================================================

Automatically aggregate base timeframe data into higher timeframes.

Example: Stream 1m candles and automatically get 5m, 15m, 1h, 4h, 1d candles.

Prerequisites:
- streamforge installed

Run:
    python multi_timeframe.py
"""

import asyncio
import streamforge as sf


async def example1_basic_aggregation():
    """
    Example 1: Basic Aggregation
    
    Aggregate 1m candles to 5m
    """
    print("\n" + "="*60)
    print("Example 1: Basic Aggregation (1m → 5m)")
    print("="*60)
    
    runner = sf.BinanceRunner(
        stream_input=sf.DataInput(
            type="kline",
            symbols=["BTCUSDT", "ETHUSDT", "SOLUSDT"],
            timeframe="1m",              # Base timeframe
            aggregate_list=["5m"]        # Aggregate to 5m
        ),
        active_warmup=True  # Required for aggregation! default is True
    )
    
    # Internal logging is handled by sf.config.logger
    
    
    print("✓ Will emit:")
    print("  - 1m candles (every minute)")
    print("  - 5m candles (every 5 minutes)")
    print("\n⏱️  Wait 5 minutes to see first 5m candle!")
    
    await runner.run()


async def example2_multiple_timeframes():
    """
    Example 2: Multiple Timeframe Aggregation
    
    Aggregate to multiple higher timeframes simultaneously
    """
    print("\n" + "="*60)
    print("Example 2: Multiple Timeframes (1m → 5m, 15m, 1h)")
    print("="*60)
    
    runner = sf.BinanceRunner(
        stream_input=sf.DataInput(
            type="kline",
            symbols=["BTCUSDT"],
            timeframe="1m",
            aggregate_list=["5m", "15m", "1h"]  # Multiple timeframes
        ),
        active_warmup=True
    )
    
    # Internal logging is handled by sf.config.logger
    
    print("✓ Will emit:")
    print("  - 1m candles (every 1 minute)")
    print("  - 5m candles (every 5 minutes)")
    print("  - 15m candles (every 15 minutes)")
    print("  - 1h candles (every 60 minutes)")
    
    await runner.run()


async def example3_full_aggregation_pyramid():
    """
    Example 3: Full Aggregation Pyramid
    
    Create a complete pyramid of timeframes
    """
    print("\n" + "="*60)
    print("Example 3: Full Aggregation Pyramid")
    print("="*60)
    
    runner = sf.BinanceRunner(
        stream_input=sf.DataInput(
            type="kline",
            symbols=["BTCUSDT"],
            timeframe="1m",
            aggregate_list=[
                "5m",    # 5 minutes
                "15m",   # 15 minutes
                "30m",   # 30 minutes
                "1h",    # 1 hour
                "4h",    # 4 hours
                "1d"     # 1 day
            ]
        ),
        active_warmup=True
    )
    # Internal logging is handled by sf.config.logger
    
    print("✓ Aggregation pyramid:")
    print("  1m → 5m → 15m → 30m → 1h → 4h → 1d")
    print("\n  All from a single 1m stream!")
    
    await runner.run()


async def example4_save_all_timeframes():
    """
    Example 4: Save All Timeframes to Database
    
    Store all timeframes in one table
    """
    print("\n" + "="*60)
    print("Example 4: Save All Timeframes")
    print("="*60)
    
    from sqlalchemy.orm import declarative_base
    from sqlalchemy import Column, String, Float, BigInteger
    
    Base = declarative_base()
    
    class KlineTable(Base):
        __tablename__ = 'klines'
        source = Column(String, primary_key=True)
        symbol = Column(String, primary_key=True)
        timeframe = Column(String, primary_key=True)  # Includes all TFs
        open_ts = Column(BigInteger, primary_key=True)
        end_ts = Column(BigInteger)
        open = Column(Float)
        high = Column(Float)
        low = Column(Float)
        close = Column(Float)
        volume = Column(Float)
    
    runner = sf.BinanceRunner(
        stream_input=sf.DataInput(
            type="kline",
            symbols=["BTCUSDT"],
            timeframe="1m",
            aggregate_list=["5m", "15m", "1h"]
        ),
        active_warmup=True
    )
    
    postgres_emitter = (sf.PostgresEmitter(
            host="localhost",
            dbname="crypto",
            user="postgres",
            password="mysecretpassword"
        )
        .set_model(KlineTable)
        .on_conflict(["source", "symbol", "timeframe", "open_ts"])
    )
    
    runner.register_emitter(postgres_emitter)
    
    print("✓ Saving to PostgreSQL:")
    print("  - 1m candles")
    print("  - 5m candles")
    print("  - 15m candles")
    print("  - 1h candles")
    print("\n  All in one table, distinguished by 'timeframe' column")
    
    await runner.run()


async def example5_separate_csv_per_timeframe():
    """
    Example 5: Separate CSV File Per Timeframe
    
    Using stream() for manual control over outputs
    """
    print("\n" + "="*60)
    print("Example 5: Separate Files Per Timeframe")
    print("="*60)
    
    # Create emitters for each timeframe
    emitters = {
        "1m": sf.CSVEmitter(
            source="Binance", symbol="BTCUSDT", timeframe="1m",
            file_path="btc_1m.csv"
        ),
        "5m": sf.CSVEmitter(
            source="Binance", symbol="BTCUSDT", timeframe="5m",
            file_path="btc_5m.csv"
        ),
        "15m": sf.CSVEmitter(
            source="Binance", symbol="BTCUSDT", timeframe="15m",
            file_path="btc_15m.csv"
        ),
        "1h": sf.CSVEmitter(
            source="Binance", symbol="BTCUSDT", timeframe="1h",
            file_path="btc_1h.csv"
        ),
    }
    
    
    runner = sf.BinanceRunner(
        stream_input=sf.DataInput(
            type="kline",
            symbols=["BTCUSDT"],
            timeframe="1m",
            aggregate_list=["5m", "15m", "1h"]
        ),
        active_warmup=True
    )
    
    print("✓ Creating separate files:")
    print("  - btc_1m.csv")
    print("  - btc_5m.csv")
    print("  - btc_15m.csv")
    print("  - btc_1h.csv")
    
    # Stream and route to appropriate file
    async for kline in runner.stream():
        timeframe = kline.timeframe
        if timeframe in emitters:
            await emitters[timeframe].emit(kline.model_dump())
            print(f"  Saved {timeframe} candle to btc_{timeframe}.csv")


async def example6_multi_symbol_multi_timeframe():
    """
    Example 6: Multiple Symbols × Multiple Timeframes
    
    Ultimate example: Many symbols, many timeframes
    """
    print("\n" + "="*60)
    print("Example 6: Multi-Symbol × Multi-Timeframe")
    print("="*60)
    
    runner = sf.BinanceRunner(
        stream_input=sf.DataInput(
            type="kline",
            symbols=["BTCUSDT", "ETHUSDT", "SOLUSDT"],  # 3 symbols
            timeframe="1m",
            aggregate_list=["5m", "15m", "1h"]  # 3 aggregations
        ),
        active_warmup=True
    )
    
    # Internal logging is handled by sf.config.logger
    
    print("✓ Streaming:")
    print("  - 3 symbols (BTC, ETH, SOL)")
    print("  - 4 timeframes (1m, 5m, 15m, 1h)")
    print("  = 12 different data streams!")
    print("\n  All from one runner!")
    
    await runner.run()


async def main():
    """
    Aggregation Benefits:
    
    ✓ Get multiple timeframes from one base stream
    ✓ Consistent data across timeframes
    ✓ Reduce API calls
    ✓ Lower bandwidth usage
    ✓ Real-time multi-timeframe analysis
    
    Important:
    - Always enable warmup for aggregation
    - Base timeframe must be smaller than aggregated timeframes
    - Supported: 1m→5m, 1m→1h, 5m→15m, etc.
    - Not supported: 1h→1m (can't disaggregate)
    """
    print("""
╔══════════════════════════════════════════════════════════════╗
║         Multi-Timeframe Aggregation Examples                ║
╚══════════════════════════════════════════════════════════════╝

Available examples:
1. example1_basic_aggregation() - 1m → 5m
2. example2_multiple_timeframes() - 1m → 5m, 15m, 1h
3. example3_full_aggregation_pyramid() - Complete pyramid ⭐
4. example4_save_all_timeframes() - Save to PostgreSQL
5. example5_separate_csv_per_timeframe() - Separate files
6. example6_multi_symbol_multi_timeframe() - Everything at once!

Choose one example below:
""")
    
    # Uncomment ONE example to run:
    # await example1_basic_aggregation()
    await example2_multiple_timeframes()
    # await example3_full_aggregation_pyramid()
    # await example4_save_all_timeframes()
    # await example5_separate_csv_per_timeframe()
    # await example6_multi_symbol_multi_timeframe()


if __name__ == "__main__":
    asyncio.run(main())

