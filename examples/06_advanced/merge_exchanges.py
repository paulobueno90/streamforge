"""
Merge Exchanges - Combine Multiple Exchange Streams
===================================================

Stream data from multiple exchanges simultaneously and merge into
a single unified stream.

Use Cases:
✓ Price comparison across exchanges
✓ Arbitrage monitoring
✓ Unified multi-exchange database
✓ Aggregate liquidity data

Prerequisites:
- streamforge installed

Run:
    python merge_exchanges.py
"""

import asyncio
import streamforge as sf
from streamforge.merge_stream import merge_streams



async def example1_simple_merge():
    """
    Example 1: Simple Two-Exchange Merge
    
    Merge BTC data from Binance and OKX
    """
    print("\n" + "="*60)
    print("Example 1: Merge Binance + OKX")
    print("="*60)
    
    # Binance runner
    binance_runner = sf.BinanceRunner(
        stream_input=sf.DataInput(
            type="kline",
            symbols=["BTCUSDT", "ETHUSDT", "SOLUSDT"],
            timeframe="1m"
        )
    )
    
    # OKX runner
    okx_runner = sf.OKXRunner(
        stream_input=sf.DataInput(
            type="candle",
            symbols=["BTC-USDT", "ETH-USDT", "SOL-USDT"],
            timeframe="1m"
        )
    )
    
    print("✓ Merging BTC streams from:")
    print("  - Binance")
    print("  - OKX")
    
    # Merge and process
    async for data in merge_streams(binance_runner, okx_runner):
        print(f"📊 {data.source:8} | {data.symbol:10} | ${data.close:,.2f}")


async def example2_three_exchanges():
    """
    Example 2: Three Exchange Merge
    
    Binance + OKX + Kraken
    """
    print("\n" + "="*60)
    print("Example 2: Merge Binance + OKX + Kraken")
    print("="*60)
    
    binance_runner = sf.BinanceRunner(
        stream_input=sf.DataInput(
            type="kline",
            symbols=["BTCUSDT", "ETHUSDT", "SOLUSDT"],
            timeframe="1m"
        )
    )
    
    okx_runner = sf.OKXRunner(
        stream_input=sf.DataInput(
            type="candle",
            symbols=["BTC-USDT", "ETH-USDT", "SOL-USDT"],
            timeframe="1m"
        )
    )
    
    kraken_runner = sf.KrakenRunner(
        stream_input=sf.DataInput(
            type="ohlc",
            symbols=["BTC/USD", "ETH/USD", "SOL/USD"],
            timeframe="1m"
        )
    )
    
    print("✓ Merging 3 exchanges")
    
    async for data in merge_streams(binance_runner, okx_runner, kraken_runner):
        print(f"📡 {data.source:8} | {data.symbol:12} | ${data.close:,.2f}")


async def example3_merge_to_database():
    """
    Example 3: Merge to Unified Database
    
    Store all exchanges in one database table
    """
    print("\n" + "="*60)
    print("Example 3: Merge to Unified Database")
    print("="*60)
    
    from sqlalchemy.orm import declarative_base
    from sqlalchemy import Column, String, Float, BigInteger
    
    Base = declarative_base()
    
    class UnifiedKlineTable(Base):
        __tablename__ = 'unified_klines'
        source = Column(String, primary_key=True)  # Binance, OKX, Kraken
        symbol = Column(String, primary_key=True)
        timeframe = Column(String, primary_key=True)
        open_ts = Column(BigInteger, primary_key=True)
        end_ts = Column(BigInteger)
        open = Column(Float)
        high = Column(Float)
        low = Column(Float)
        close = Column(Float)
        volume = Column(Float)
    
    # Shared emitter for all exchanges
    postgres_emitter = (sf.PostgresEmitter(
            host="localhost",
            dbname="crypto",
            user="postgres",
            password="mysecretpassword"
        )
        .set_model(UnifiedKlineTable)
        .on_conflict(["source", "symbol", "timeframe", "open_ts"])
    )
    
    await postgres_emitter.connect()
    
    # Create runners
    binance_runner = sf.BinanceRunner(
        stream_input=sf.DataInput(
            type="kline",
            symbols=["BTCUSDT", "ETHUSDT", "SOLUSDT"],
            timeframe="1m"
        )
    )
    
    okx_runner = sf.OKXRunner(
        stream_input=sf.DataInput(
            type="candle",
            symbols=["BTC-USDT", "ETH-USDT", "SOL-USDT"],
            timeframe="1m"
        )
    )
    
    print("✓ Streaming to unified database")
    print("  All exchanges → same table")
    
    # Merge and emit
    async for data in merge_streams(binance_runner, okx_runner):
        await postgres_emitter.emit(data)
        print(f"💾 Saved {data.source} {data.symbol}")


async def example4_price_comparison():
    """
    Example 4: Real-time Price Comparison
    
    Track price differences across exchanges
    """
    print("\n" + "="*60)
    print("Example 4: Price Comparison")
    print("="*60)
    
    # Store latest prices
    latest_prices = {}
    
    binance_runner = sf.BinanceRunner(
        stream_input=sf.DataInput(
            type="kline",
            symbols=["BTCUSDT", "ETHUSDT", "SOLUSDT"],
            timeframe="1m"
        )
    )
    
    okx_runner = sf.OKXRunner(
        stream_input=sf.DataInput(
            type="candle",
            symbols=["BTC-USDT", "ETH-USDT", "SOL-USDT"],
            timeframe="1m"
        )
    )
    
    print("✓ Comparing BTC prices...")
    
    async for data in merge_streams(binance_runner, okx_runner):
        # Update latest price
        latest_prices[data.source] = data.close
        
        # Compare when we have both
        if len(latest_prices) >= 2:
            binance_price = latest_prices.get("Binance", 0)
            okx_price = latest_prices.get("OKX", 0)
            
            if binance_price and okx_price:
                diff = binance_price - okx_price
                diff_pct = (diff / binance_price) * 100
                
                print(f"\n💰 Price Comparison:")
                print(f"   Binance: ${binance_price:,.2f}")
                print(f"   OKX:     ${okx_price:,.2f}")
                print(f"   Diff:    ${diff:+.2f} ({diff_pct:+.4f}%)")
                
                if abs(diff_pct) > 0.1:
                    print(f"   🚨 ARBITRAGE OPPORTUNITY!")


async def example5_multi_symbol_multi_exchange():
    """
    Example 5: Multiple Symbols × Multiple Exchanges
    
    The ultimate merge: many symbols from many exchanges
    """
    print("\n" + "="*60)
    print("Example 5: Multi-Symbol × Multi-Exchange")
    print("="*60)
    
    binance_runner = sf.BinanceRunner(
        stream_input=sf.DataInput(
            type="kline",
            symbols=["BTCUSDT", "ETHUSDT", "SOLUSDT"],
            timeframe="1m"
        )
    )
    
    okx_runner = sf.OKXRunner(
        stream_input=sf.DataInput(
            type="candle",
            symbols=["BTC-USDT", "ETH-USDT", "SOL-USDT"],
            timeframe="1m"
        )
    )
    
    print("✓ Streaming:")
    print("  - 3 symbols (BTC, ETH, SOL)")
    print("  - 2 exchanges (Binance, OKX)")
    print("  = 6 data streams merged!")
    
    async for data in merge_streams(binance_runner, okx_runner):
        print(f"📈 {data.source:8} | {data.symbol:10} | ${data.close:>10,.2f} | Vol: {data.volume:>10,.2f}")


async def main():
    """
    Merging Benefits:
    
    ✓ Unified view of multiple exchanges
    ✓ Price comparison and arbitrage detection
    ✓ Aggregated liquidity analysis
    ✓ Single database for all exchanges
    ✓ Reduced code complexity
    """
    print("""
╔══════════════════════════════════════════════════════════════╗
║          Merge Multiple Exchange Streams                    ║
╚══════════════════════════════════════════════════════════════╝

Available examples:
1. example1_simple_merge() - Binance + OKX
2. example2_three_exchanges() - Binance + OKX + Kraken
3. example3_merge_to_database() - Unified database
4. example4_price_comparison() - Arbitrage detection
5. example5_multi_symbol_multi_exchange() - Everything! ⭐

Choose one example below:
""")
    
    # Uncomment ONE example to run:
    await example1_simple_merge()
    # await example2_three_exchanges()
    # await example3_merge_to_database()
    # await example4_price_comparison()
    # await example5_multi_symbol_multi_exchange()


if __name__ == "__main__":
    asyncio.run(main())

