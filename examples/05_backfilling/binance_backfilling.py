"""
Binance Backfilling - Load Historical Data
==========================================

Backfill historical kline/candlestick data from Binance.

Uses Binance's public data archive (no API keys required).

Prerequisites:
- streamforge installed

Run:
    python binance_backfilling.py
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
    print("Example 1: Backfill to CSV")
    print("="*60)
    
    backfiller = sf.BinanceBackfilling(
        symbol="BTCUSDT",
        timeframe="1m",
        from_date="2025-10-01",
        to_date="2025-10-07"
    )
    
    # No emitter = defaults to CSV
    print("✓ Backfilling BTC 1m data from 2025-10-01 to 2025-10-07")
    print("  Output: Binance-BTCUSDT-1m-2025-10-01_2025-10-07.csv")
    
    backfiller.run()
    
    print("\n✓ Backfill complete!")


def example2_backfill_to_postgres():
    """
    Example 2: Backfill to PostgreSQL
    
    Load historical data directly into database
    """
    print("\n" + "="*60)
    print("Example 2: Backfill to PostgreSQL")
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
    
    backfiller = sf.BinanceBackfilling(
        symbol="BTCUSDT",
        timeframe="1m",
        from_date="2025-10-01",
        to_date="2025-10-07"
    )
    
    backfiller.register_emitter(emitter)
    
    print("✓ Backfilling to PostgreSQL")
    print("  Can be run multiple times safely (upsert enabled)")
    
    backfiller.run()
    
    print("\n✓ Backfill complete!")


def example3_backfill_multiple_symbols():
    """
    Example 3: Backfill Multiple Symbols
    
    Load data for multiple cryptocurrencies
    """
    print("\n" + "="*60)
    print("Example 3: Backfill Multiple Symbols")
    print("="*60)
    
    symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
    
    emitter = (sf.PostgresEmitter(
            host="localhost",
            dbname="crypto",
            user="postgres",
            password="mysecretpassword"
        )
        .set_model(KlineTable)
        .on_conflict(["source", "symbol", "timeframe", "open_ts"])
    )
    
    for symbol in symbols:
        print(f"\n📊 Backfilling {symbol}...")
        
        backfiller = sf.BinanceBackfilling(
            symbol=symbol,
            timeframe="1m",
            from_date="2025-10-01",
            to_date="2025-10-07"
        )
        
        backfiller.register_emitter(emitter)
        backfiller.run()
        
        print(f"✓ {symbol} complete!")
    
    print("\n✓ All backfills complete!")


def example4_backfill_with_transformer():
    """
    Example 4: Backfill with Data Transformation
    
    Transform data during backfilling
    """
    print("\n" + "="*60)
    print("Example 4: Backfill with Transformer")
    print("="*60)
    
    def custom_transformer(data: dict):
        """Add computed fields during backfill"""
        return {
            **data,
            "price_change_pct": ((data["close"] - data["open"]) / data["open"]) * 100,
            "is_bullish": data["close"] > data["open"],
        }
    
    backfiller = sf.BinanceBackfilling(
        symbol="BTCUSDT",
        timeframe="1m",
        from_date="2025-10-01",
        to_date="2025-10-03",
        file_path="btc_transformed.csv"
    )
    
    backfiller.set_transformer(custom_transformer)
    
    print("✓ Backfilling with transformation")
    print("  Adding: price_change_pct, is_bullish")
    
    backfiller.run()
    
    print("\n✓ Backfill complete!")


def example5_backfill_long_period():
    """
    Example 5: Backfill Long Time Period
    
    Load months of historical data
    """
    print("\n" + "="*60)
    print("Example 5: Backfill Long Period (2 years)")
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
    
    backfiller = sf.BinanceBackfilling(
        symbol="BTCUSDT",
        timeframe="1m",
        from_date="2023-07-01",  # 2 years ago
        to_date="2025-10-01"
    )
    
    backfiller.register_emitter(emitter)
    
    print("✓ Backfilling 2 years of data")
    print("  This may take several minutes...") 
    
    backfiller.run()
    
    print("\n✓ Backfill complete!")


def example6_backfill_to_present():
    """
    Example 6: Backfill to Present
    
    Load all data from a date until now
    """
    print("\n" + "="*60)
    print("Example 6: Backfill to Present")
    print("="*60)
    
    backfiller = sf.BinanceBackfilling(
        symbol="BTCUSDT",
        timeframe="1m",
        from_date="2025-10-01",
        to_date="now"  # Special keyword: until now
    )
    
    print("✓ Backfilling from 2025-10-01 to now")
    
    backfiller.run()
    
    print("\n✓ Backfill complete!")


def main():
    """
    Backfilling Tips:
    
    ✓ Always use upsert for PostgreSQL (safe to re-run)
    ✓ Backfill in chunks if dealing with very long periods
    ✓ Use transformers to add computed fields
    ✓ Defaults to CSV if no emitter specified
    """
    print("""
╔══════════════════════════════════════════════════════════════╗
║            Binance Backfilling Examples                     ║
╚══════════════════════════════════════════════════════════════╝

Available examples:
1. example1_backfill_to_csv() - Simple CSV backfill
2. example2_backfill_to_postgres() - Load into database
3. example3_backfill_multiple_symbols() - Multiple cryptos
4. example4_backfill_with_transformer() - Transform data
5. example5_backfill_long_period() - Long time periods
6. example6_backfill_to_present() - Until now

Choose one example below:
""")
    
    # Uncomment ONE example to run:
    example1_backfill_to_csv()
    # example2_backfill_to_postgres()
    # example3_backfill_multiple_symbols()
    # example4_backfill_with_transformer()
    # example5_backfill_long_period()
    # example6_backfill_to_present()


if __name__ == "__main__":
    main()

