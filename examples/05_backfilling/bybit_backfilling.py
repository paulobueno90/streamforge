"""
Bybit Backfilling - Load Historical Data
========================================

Backfill historical kline/candlestick data from Bybit.

Uses Bybit's public REST API to fetch historical data (no API keys required).
Supports Spot, Linear (USDT/USDC perpetuals), and Inverse futures markets.

Prerequisites:
- streamforge installed

Run:
    python bybit_backfilling.py
"""

import asyncio
import streamforge as sf
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String, Float, BigInteger

sf.show_logs()

Base = declarative_base()


class KlineTable(Base):
    __tablename__ = 'klines'
    source = Column(String, primary_key=True)
    symbol = Column(String, primary_key=True)
    timeframe = Column(String, primary_key=True)
    open_ts = Column(BigInteger, primary_key=True)
    end_ts = Column(BigInteger)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Float)


def example1_backfill_to_csv():
    """
    Example 1: Backfill to CSV (Default)
    
    Simplest backfilling - no emitter specified, defaults to CSV
    """
    print("\n" + "="*60)
    print("Example 1: Backfill to CSV (Spot Market)")
    print("="*60)
    
    backfiller = sf.BybitBackfilling(
        symbol="BTCUSDT",
        timeframe="1m",
        from_date="2024-10-01",
        to_date="2024-10-07",
        market_type="SPOT"  # Default
    )
    
    # No emitter = defaults to CSV
    print("✓ Backfilling BTC 1m data from 2024-10-01 to 2024-10-07")
    print("  Output: Bybit-BTCUSDT-spot-1m-2024-10-01_2024-10-07.csv")
    
    backfiller.run()
    
    print("\n✓ Backfill complete!")


def example2_backfill_linear_futures():
    """
    Example 2: Backfill Linear Futures (USDT/USDC Perpetuals)
    
    Backfill USDT/USDC perpetual futures data
    """
    print("\n" + "="*60)
    print("Example 2: Backfill Linear Futures")
    print("="*60)
    
    backfiller = sf.BybitBackfilling(
        symbol="BTCUSDT",
        timeframe="1h",
        from_date="2024-10-01",
        to_date="2024-10-07",
        market_type="LINEAR"  # USDT/USDC perpetuals
    )
    
    print("✓ Backfilling BTC Linear futures 1h data")
    print("  Output: Bybit-BTCUSDT-linear-1h-2024-10-01_2024-10-07.csv")
    
    backfiller.run()
    
    print("\n✓ Backfill complete!")


def example3_backfill_inverse_futures():
    """
    Example 3: Backfill Inverse Futures (Coin-Margined)
    
    Backfill inverse perpetual futures data
    Note: Inverse uses BTCUSD (not BTCUSDT)
    """
    print("\n" + "="*60)
    print("Example 3: Backfill Inverse Futures")
    print("="*60)
    
    backfiller = sf.BybitBackfilling(
        symbol="BTCUSD",  # Note: USD for inverse, not USDT
        timeframe="1h",
        from_date="2024-10-01",
        to_date="2024-10-07",
        market_type="INVERSE"  # Coin-margined futures
    )
    
    print("✓ Backfilling BTC Inverse futures 1h data")
    print("  Output: Bybit-BTCUSD-inverse-1h-2024-10-01_2024-10-07.csv")
    
    backfiller.run()
    
    print("\n✓ Backfill complete!")


def example4_backfill_to_postgres():
    """
    Example 4: Backfill to PostgreSQL
    
    Load historical data directly into database
    """
    print("\n" + "="*60)
    print("Example 4: Backfill to PostgreSQL")
    print("="*60)
    
    # Create PostgreSQL emitter with upsert
    emitter = (sf.PostgresEmitter(
            host="localhost",
            dbname="crypto",
            user="postgres",
            password="mysecretpassword"
        )
        .set_model(KlineTable)
        .on_conflict(["source", "symbol", "timeframe", "open_ts"])  # Important for backfilling!
    )
    
    backfiller = sf.BybitBackfilling(
        symbol="BTCUSDT",
        timeframe="1m",
        from_date="2024-10-01",
        to_date="2024-10-07",
        market_type="SPOT"
    )
    
    backfiller.register_emitter(emitter)
    
    print("✓ Backfilling to PostgreSQL")
    print("  Can be run multiple times safely (upsert enabled)")
    
    backfiller.run()
    
    print("\n✓ Backfill complete!")


def example5_backfill_multiple_markets():
    """
    Example 5: Backfill Multiple Market Types
    
    Load data for spot, linear, and inverse markets
    """
    print("\n" + "="*60)
    print("Example 5: Backfill Multiple Market Types")
    print("="*60)
    
    emitter = (sf.PostgresEmitter(
            host="localhost",
            dbname="crypto",
            user="postgres",
            password="mysecretpassword"
        )
        .set_model(KlineTable)
        .on_conflict(["source", "symbol", "timeframe", "open_ts"])
    )
    
    markets = [
        ("SPOT", "BTCUSDT"),
        ("LINEAR", "BTCUSDT"),
        ("INVERSE", "BTCUSD")  # Note: USD for inverse
    ]
    
    for market_type, symbol in markets:
        print(f"\n📊 Backfilling {market_type} market ({symbol})...")
        
        backfiller = sf.BybitBackfilling(
            symbol=symbol,
            timeframe="1h",
            from_date="2024-10-01",
            to_date="2024-10-07",
            market_type=market_type
        )
        
        backfiller.register_emitter(emitter)
        backfiller.run()
        
        print(f"✓ {market_type} complete!")
    
    print("\n✓ All market types backfilled!")


def example6_backfill_with_transformer():
    """
    Example 6: Backfill with Data Transformation
    
    Transform data during backfilling
    """
    print("\n" + "="*60)
    print("Example 6: Backfill with Transformer")
    print("="*60)
    
    def custom_transformer(data: dict):
        """Add computed fields during backfill"""
        return {
            **data,
            "price_change_pct": ((data["close"] - data["open"]) / data["open"]) * 100,
            "is_bullish": data["close"] > data["open"],
        }
    
    backfiller = sf.BybitBackfilling(
        symbol="BTCUSDT",
        timeframe="1m",
        from_date="2024-10-01",
        to_date="2024-10-03",
        file_path="btc_transformed.csv",
        market_type="SPOT"
    )
    
    backfiller.set_transformer(custom_transformer)
    
    print("✓ Backfilling with transformation")
    print("  Adding: price_change_pct, is_bullish")
    
    backfiller.run()
    
    print("\n✓ Backfill complete!")


def example7_backfill_to_present():
    """
    Example 7: Backfill to Present
    
    Load all data from a date until now
    """
    print("\n" + "="*60)
    print("Example 7: Backfill to Present")
    print("="*60)
    
    backfiller = sf.BybitBackfilling(
        symbol="BTCUSDT",
        timeframe="1m",
        from_date="2024-10-01",
        to_date="now",  # Special keyword: until now
        market_type="SPOT"
    )
    
    print("✓ Backfilling from 2024-10-01 to now")
    
    backfiller.run()
    
    print("\n✓ Backfill complete!")


def main():
    """
    Bybit Backfilling Tips:
    
    ✓ Always use upsert for PostgreSQL (safe to re-run)
    ✓ Use market_type parameter: SPOT, LINEAR, or INVERSE
    ✓ Inverse futures use BTCUSD (not BTCUSDT)
    ✓ All market types share the same rate limit pool
    ✓ Defaults to CSV if no emitter specified
    """
    print("""
╔══════════════════════════════════════════════════════════════╗
║            Bybit Backfilling Examples                        ║
╚══════════════════════════════════════════════════════════════╝

Available examples:
1. example1_backfill_to_csv() - Simple CSV backfill (Spot)
2. example2_backfill_linear_futures() - Linear futures
3. example3_backfill_inverse_futures() - Inverse futures
4. example4_backfill_to_postgres() - Load into database
5. example5_backfill_multiple_markets() - All market types
6. example6_backfill_with_transformer() - Transform data
7. example7_backfill_to_present() - Until now

Choose one example below:
""")
    
    # Uncomment ONE example to run:
    example1_backfill_to_csv()
    # example2_backfill_linear_futures()
    # example3_backfill_inverse_futures()
    # example4_backfill_to_postgres()
    # example5_backfill_multiple_markets()
    # example6_backfill_with_transformer()
    # example7_backfill_to_present()


if __name__ == "__main__":
    main()

