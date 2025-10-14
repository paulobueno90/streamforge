"""
PostgreSQL Emitter - Custom SQL Queries
=======================================

Use raw SQL queries instead of ORM for maximum control.

Use Cases:
- Custom SQL logic
- Complex upsert conditions
- Database-specific features
- Performance optimization

Prerequisites:
- PostgreSQL server running
- streamforge installed

Run:
    python postgres_custom_query.py
"""

import asyncio
import streamforge as sf



async def basic_custom_query():
    """
    Pattern 1: Basic Custom Query
    
    Use raw SQL instead of ORM
    """
    print("\n" + "="*60)
    print("PATTERN 1: Basic Custom Query")
    print("="*60)
    
    # Custom SQL query with named parameters
    custom_query = """
    INSERT INTO klines (source, symbol, timeframe, open_ts, end_ts, open, high, low, close, volume)
    VALUES (:source, :symbol, :timeframe, :open_ts, :end_ts, :open, :high, :low, :close, :volume)
    """
    
    emitter = sf.PostgresEmitter(
        host="localhost",
        dbname="crypto",
        user="postgres",
        password="mysecretpassword"
    ).set_query(custom_query)
    
    runner = sf.BinanceRunner(
        stream_input=sf.DataInput(type="kline", symbols=["BTCUSDT","ETHUSDT","SOLUSDT"], timeframe="1m")
    )
    runner.register_emitter(emitter)
    
    await runner.run()


async def custom_query_with_upsert():
    """
    Pattern 2: Custom Query with Upsert
    
    Full control over conflict resolution
    """
    print("\n" + "="*60)
    print("PATTERN 2: Custom Query with Upsert")
    print("="*60)
    
    # Custom upsert logic
    custom_query = """
    INSERT INTO klines (source, symbol, timeframe, open_ts, end_ts, open, high, low, close, volume)
    VALUES (:source, :symbol, :timeframe, :open_ts, :end_ts, :open, :high, :low, :close, :volume)
    ON CONFLICT (source, symbol, timeframe, open_ts) 
    DO UPDATE SET 
        end_ts = EXCLUDED.end_ts,
        open = EXCLUDED.open,
        high = EXCLUDED.high,
        low = EXCLUDED.low,
        close = EXCLUDED.close,
        volume = EXCLUDED.volume
    """
    
    emitter = sf.PostgresEmitter(
        host="localhost",
        dbname="postgres",
        user="postgres",
        password="mysecretpassword"
    ).set_query(custom_query)
    
    runner = sf.BinanceRunner(
        stream_input=sf.DataInput(type="kline", symbols=["BTCUSDT","ETHUSDT","SOLUSDT"], timeframe="1m")
    )
    runner.register_emitter(emitter)
    
    await runner.run()


async def custom_query_with_calculation():
    """
    Pattern 3: Custom Query with Calculations
    
    Perform calculations in SQL
    """
    print("\n" + "="*60)
    print("PATTERN 3: Custom Query with Calculations")
    print("="*60)
    
    # Store original data + calculated fields
    custom_query = """
    INSERT INTO klines_extended (
        source, symbol, timeframe, open_ts, end_ts,
        open, high, low, close, volume,
        price_range, price_change, price_change_pct
    )
    VALUES (
        :source, :symbol, :timeframe, :open_ts, :end_ts,
        :open, :high, :low, :close, :volume,
        :high - :low,                        -- price_range
        :close - :open,                      -- price_change
        ((:close - :open) / :open) * 100     -- price_change_pct
    )
    """
    
    emitter = sf.PostgresEmitter(
        host="localhost",
        dbname="crypto",
        user="postgres",
        password="mysecretpassword"
    ).set_query(custom_query)
    
    runner = sf.BinanceRunner(
        stream_input=sf.DataInput(type="kline", symbols=["BTCUSDT","ETHUSDT","SOLUSDT"], timeframe="1m")
    )
    runner.register_emitter(emitter)
    
    await runner.run()


async def custom_query_conditional_upsert():
    """
    Pattern 4: Conditional Upsert
    
    Only update if new data is more recent
    """
    print("\n" + "="*60)
    print("PATTERN 4: Conditional Upsert")
    print("="*60)
    
    # Only update if incoming data is newer
    custom_query = """
    INSERT INTO klines (source, symbol, timeframe, open_ts, end_ts, open, high, low, close, volume)
    VALUES (:source, :symbol, :timeframe, :open_ts, :end_ts, :open, :high, :low, :close, :volume)
    ON CONFLICT (source, symbol, timeframe, open_ts) 
    DO UPDATE SET 
        end_ts = EXCLUDED.end_ts,
        open = EXCLUDED.open,
        high = GREATEST(klines.high, EXCLUDED.high),  -- Keep highest high
        low = LEAST(klines.low, EXCLUDED.low),        -- Keep lowest low
        close = EXCLUDED.close,
        volume = EXCLUDED.volume
    WHERE EXCLUDED.end_ts > klines.end_ts  -- Only update if newer
    """
    
    emitter = sf.PostgresEmitter(
        host="localhost",
        dbname="crypto",
        user="postgres",
        password="mysecretpassword"
    ).set_query(custom_query)
    
    runner = sf.BinanceRunner(
        stream_input=sf.DataInput(type="kline", symbols=["BTCUSDT","ETHUSDT","SOLUSDT"], timeframe="1m")
    )
    runner.register_emitter(emitter)
    
    await runner.run()


async def custom_query_with_trigger():
    """
    Pattern 5: Insert with Metadata
    
    Add metadata like insertion timestamp
    """
    print("\n" + "="*60)
    print("PATTERN 5: Insert with Metadata")
    print("="*60)
    
    # Add metadata to track when data was ingested
    custom_query = """
    INSERT INTO klines_with_metadata (
        source, symbol, timeframe, open_ts, end_ts,
        open, high, low, close, volume,
        ingested_at, ingestion_source
    )
    VALUES (
        :source, :symbol, :timeframe, :open_ts, :end_ts,
        :open, :high, :low, :close, :volume,
        NOW(),              -- ingested_at
        'streamforge'       -- ingestion_source
    )
    """
    
    emitter = sf.PostgresEmitter(
        host="localhost",
        dbname="crypto",
        user="postgres",
        password="mysecretpassword"
    ).set_query(custom_query)
    
    runner = sf.BinanceRunner(
        stream_input=sf.DataInput(type="kline", symbols=["BTCUSDT","ETHUSDT","SOLUSDT"], timeframe="1m")
    )
    runner.register_emitter(emitter)
    
    await runner.run()


async def main():
    """
    When to use custom queries vs ORM:
    
    Use Custom Queries when:
    ✓ Need database-specific features
    ✓ Complex upsert logic
    ✓ In-database calculations
    ✓ Performance critical operations
    
    Use ORM when:
    ✓ Simple insert/upsert
    ✓ Want database portability
    ✓ Using SQLAlchemy features
    ✓ Standard CRUD operations
    """
    print("""
╔══════════════════════════════════════════════════════════════╗
║        PostgreSQL Emitter: Custom SQL Queries               ║
╚══════════════════════════════════════════════════════════════╝

Available patterns:
1. basic_custom_query() - Simple raw SQL
2. custom_query_with_upsert() - Custom upsert logic
3. custom_query_with_calculation() - SQL calculations
4. custom_query_conditional_upsert() - Conditional updates
5. custom_query_with_trigger() - Add metadata

Choose one pattern below:
""")
    
    # Uncomment ONE pattern to run:
    # await basic_custom_query()
    await custom_query_with_upsert()
    # await custom_query_with_calculation()
    # await custom_query_conditional_upsert()
    # await custom_query_with_trigger()


if __name__ == "__main__":
    asyncio.run(main())

