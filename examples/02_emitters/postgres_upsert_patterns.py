"""
PostgreSQL Emitter - Upsert Patterns
====================================

Understanding ON CONFLICT DO UPDATE (upsert) in PostgreSQL emitter.

Key Concepts:
- Upsert = Insert or Update (if conflict exists, update instead of error)
- index_elements = columns that define uniqueness (usually primary key)
- When conflict occurs, all non-key columns are updated

Use Cases:
✓ Backfilling historical data (avoid duplicates)
✓ Re-streaming same time periods
✓ Correcting data (update existing records)
✗ Pure append-only streaming (simpler without upsert)

Prerequisites:
- PostgreSQL with table created
- streamforge installed

Run:
    python postgres_upsert_patterns.py
"""

import asyncio
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String, Float, BigInteger
import streamforge as sf


Base = declarative_base()


class KlineTable(Base):
    __tablename__ = 'klines'
    
    # These columns form the composite primary key
    source = Column(String, primary_key=True)
    symbol = Column(String, primary_key=True)
    timeframe = Column(String, primary_key=True)
    open_ts = Column(BigInteger, primary_key=True)
    
    # These columns will be updated on conflict
    end_ts = Column(BigInteger)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Float)


async def pattern1_no_upsert():
    """
    Pattern 1: No Upsert (Default)
    
    Behavior:
    - Insert new records
    - If duplicate exists → ERROR and skip
    
    Best for:
    - Pure append-only streaming
    - When you're sure there are no duplicates
    - Fastest performance (no conflict checking)
    """
    print("\n" + "="*60)
    print("PATTERN 1: No Upsert (Default)")
    print("="*60)
    print("Will error if trying to insert duplicate records")
    
    emitter = sf.PostgresEmitter(
        host="localhost",
        dbname="crypto",
        user="postgres",
        password="mysecretpassword"
    ).set_model(KlineTable)
    # No upsert configuration
    
    runner = sf.BinanceRunner(
        stream_input=sf.DataInput(type="kline", symbols=["BTCUSDT","ETHUSDT","SOLUSDT"], timeframe="1m")
    )
    runner.register_emitter(emitter)
    
    await runner.run()


async def pattern2_upsert_via_constructor():
    """
    Pattern 2: Upsert via Constructor
    
    Set upsert parameters when creating the emitter
    """
    print("\n" + "="*60)
    print("PATTERN 2: Upsert via Constructor")
    print("="*60)
    print("Upsert enabled from the start")
    
    emitter = sf.PostgresEmitter(
        host="localhost",
        dbname="crypto",
        user="postgres",
        password="mysecretpassword",
        upsert=True,  # Enable upsert mode
        index_elements=["source", "symbol", "timeframe", "open_ts"]  # Define conflict columns
    ).set_model(KlineTable)
    
    runner = sf.BinanceRunner(
        stream_input=sf.DataInput(type="kline", symbols=["BTCUSDT","ETHUSDT","SOLUSDT"], timeframe="1m")
    )
    runner.register_emitter(emitter)
    
    await runner.run()


async def pattern3_upsert_via_method_chaining():
    """
    Pattern 3: Upsert via on_conflict() - Method Chaining
    
    Most common and cleanest approach
    """
    print("\n" + "="*60)
    print("PATTERN 3: Upsert via on_conflict() - Method Chaining")
    print("="*60)
    print("Clean fluent interface")
    
    emitter = (sf.PostgresEmitter(
            host="localhost",
            dbname="crypto",
            user="postgres",
            password="mysecretpassword"
        )
        .set_model(KlineTable)
        .on_conflict(["source", "symbol", "timeframe", "open_ts"])  # Enables upsert + sets index
    )
    
    runner = sf.BinanceRunner(
        stream_input=sf.DataInput(type="kline", symbols=["BTCUSDT","ETHUSDT","SOLUSDT"], timeframe="1m")
    )
    runner.register_emitter(emitter)
    
    await runner.run()


async def pattern4_upsert_via_inplace():
    """
    Pattern 4: Upsert via on_conflict() - Inplace
    
    Step-by-step configuration
    """
    print("\n" + "="*60)
    print("PATTERN 4: Upsert via on_conflict() - Inplace")
    print("="*60)
    print("Step-by-step configuration")
    
    emitter = sf.PostgresEmitter(
        host="localhost",
        dbname="crypto",
        user="postgres",
        password="mysecretpassword"
    )
    
    emitter.set_model(KlineTable, inplace=True)
    emitter.on_conflict(
        index_elements=["source", "symbol", "timeframe", "open_ts"],
        inplace=True
    )
    
    runner = sf.BinanceRunner(
        stream_input=sf.DataInput(type="kline", symbols=["BTCUSDT","ETHUSDT","SOLUSDT"], timeframe="1m")
    )
    runner.register_emitter(emitter)
    
    await runner.run()


async def pattern5_backfilling_with_upsert():
    """
    Pattern 5: Backfilling with Upsert
    
    Real-world use case: Backfill historical data safely
    Even if you run it multiple times, no duplicates!
    """
    print("\n" + "="*60)
    print("PATTERN 5: Backfilling with Upsert")
    print("="*60)
    print("Safe to run multiple times - no duplicates!")
    
    # Configure emitter with upsert
    emitter = (sf.PostgresEmitter(
            host="localhost",
            dbname="crypto",
            user="postgres",
            password="mysecretpassword"
        )
        .set_model(KlineTable)
        .on_conflict(["source", "symbol", "timeframe", "open_ts"])
    )
    
    # Backfill historical data
    backfiller = sf.BinanceBackfilling(
        symbol="BTCUSDT",
        timeframe="1m",
        from_date="2025-10-01",
        to_date="2025-10-07"
    )
    
    backfiller.register_emitter(emitter)
    
    print("Starting backfill... (can be run multiple times safely)")
    backfiller.run()
    
    print("\n✓ Backfill complete!")
    print("Try running this again - no errors, just updates existing records")


async def pattern6_multiple_emitters_mixed():
    """
    Pattern 6: Multiple Emitters with Different Upsert Settings
    
    You can have different emitters with different configurations
    """
    print("\n" + "="*60)
    print("PATTERN 6: Multiple Emitters - Mixed Upsert Settings")
    print("="*60)
    
    # Emitter 1: With upsert (to main database)
    db_emitter = (sf.PostgresEmitter(
            host="localhost",
            dbname="crypto",
            user="postgres",
            password="mysecretpassword"
        )
        .set_model(KlineTable)
        .on_conflict(["source", "symbol", "timeframe", "open_ts"])
    )
    
    # Emitter 2: Without upsert (to archive database - append only)
    archive_emitter = sf.PostgresEmitter(
        host="localhost",
        dbname="crypto_archive",
        user="postgres",
        password="mysecretpassword"
    ).set_model(KlineTable)
    # No upsert - keep all historical versions
    
    runner = sf.BinanceRunner(
        stream_input=sf.DataInput(type="kline", symbols=["BTCUSDT","ETHUSDT","SOLUSDT"], timeframe="1m")
    )
    
    # Register both
    runner.register_emitter(db_emitter)      # Upserts to main DB
    runner.register_emitter(archive_emitter)  # Appends to archive
    
    await runner.run()


async def main():
    """
    Decision Guide:
    
    Need to handle duplicates? → Use upsert (Pattern 3 or 4)
    Pure append-only stream? → No upsert (Pattern 1)
    Backfilling data? → Definitely use upsert (Pattern 5)
    Re-running same data? → Use upsert (Pattern 3 or 4)
    
    Recommended: Pattern 3 (on_conflict with method chaining)
    """
    print("""
╔══════════════════════════════════════════════════════════════╗
║        PostgreSQL Emitter: Upsert Patterns                  ║
╚══════════════════════════════════════════════════════════════╝

What is Upsert?
- Insert if record doesn't exist
- Update if record exists (based on primary key)
- Prevents duplicate key errors

Available patterns:
1. pattern1_no_upsert() - Default behavior
2. pattern2_upsert_via_constructor() - Set in __init__
3. pattern3_upsert_via_method_chaining() - Cleanest ✓
4. pattern4_upsert_via_inplace() - Step-by-step
5. pattern5_backfilling_with_upsert() - Real-world example ⭐
6. pattern6_multiple_emitters_mixed() - Advanced

Choose one pattern below:
""")
    
    # Uncomment ONE pattern to run:
    # await pattern1_no_upsert()
    # await pattern2_upsert_via_constructor()
    await pattern3_upsert_via_method_chaining()
    # await pattern4_upsert_via_inplace()
    # await pattern5_backfilling_with_upsert()
    # await pattern6_multiple_emitters_mixed()


if __name__ == "__main__":
    asyncio.run(main())

