"""
Multi-Output Pipeline - Stream to Multiple Destinations
=======================================================

One of StreamForge's most powerful features: send the same data stream
to multiple outputs simultaneously.

Use Cases:
✓ Backup to CSV while saving to database
✓ Send to Kafka for real-time + PostgreSQL for history
✓ Debug with Logger while saving to production database
✓ Store in multiple databases (main + archive)

Prerequisites:
- streamforge installed
- PostgreSQL (optional)
- Kafka (optional)

Run:
    python multi_output_pipeline.py
"""

import asyncio
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String, Float, BigInteger
import streamforge as sf


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


async def pattern1_csv_and_logger():
    """
    Pattern 1: CSV + Logger
    
    Save to file AND print to console
    """
    print("\n" + "="*60)
    print("PATTERN 1: CSV + Logger")
    print("="*60)
    
    runner = sf.BinanceRunner(
        stream_input=sf.DataInput(
            type="kline",
            symbols=["BTCUSDT","ETHUSDT","SOLUSDT"],
            timeframe="1m"
        )
    )
    
    # Emitter 1: Save to CSV
    csv_emitter = sf.CSVEmitter(
        source="Binance",
        symbol="BTCUSDT",
        timeframe="1m",
        file_path="btc_backup.csv"
    )
    
    # Emitter 2: Print to console
    logger = sf.Logger(prefix="DEBUG")
    
    # Register both - data goes to both destinations!
    runner.register_emitter(csv_emitter)
    runner.register_emitter(logger)
    
    print("✓ Data will be:")
    print("  1. Saved to btc_backup.csv")
    print("  2. Printed to console")
    
    await runner.run()


async def pattern2_postgres_and_kafka():
    """
    Pattern 2: PostgreSQL + Kafka
    
    Store in database AND stream to Kafka for real-time processing
    """
    print("\n" + "="*60)
    print("PATTERN 2: PostgreSQL + Kafka")
    print("="*60)
    
    runner = sf.BinanceRunner(
        stream_input=sf.DataInput(
            type="kline",
            symbols=["BTCUSDT", "ETHUSDT","SOLUSDT"],
            timeframe="1m"
        )
    )
    
    # Emitter 1: PostgreSQL (historical storage)
    postgres_emitter = (sf.PostgresEmitter(
            host="localhost",
            dbname="crypto",
            user="postgres",
            password="mysecretpassword"
        )
        .set_model(KlineTable)
        .on_conflict(["source", "symbol", "timeframe", "open_ts"])
    )
    
    # Emitter 2: Kafka (real-time stream)
    kafka_emitter = sf.KafkaEmitter(
        topic="crypto-realtime",
        bootstrap_servers="localhost:9092"
    )
    
    # Register both
    runner.register_emitter(postgres_emitter)
    runner.register_emitter(kafka_emitter)
    
    print("✓ Data will be:")
    print("  1. Stored in PostgreSQL (historical)")
    print("  2. Streamed to Kafka (real-time)")
    
    await runner.run()


async def pattern3_triple_output():
    """
    Pattern 3: CSV + PostgreSQL + Logger
    
    Three outputs: backup file, database, and console
    """
    print("\n" + "="*60)
    print("PATTERN 3: CSV + PostgreSQL + Logger")
    print("="*60)
    
    runner = sf.BinanceRunner(
        stream_input=sf.DataInput(
            type="kline",
            symbols=["BTCUSDT","ETHUSDT","SOLUSDT"],
            timeframe="1m",
            aggregate_list=["5m", "15m"]
        )
    )
    
    # Emitter 1: CSV backup
    csv_emitter = sf.CSVEmitter(
        source="Binance",
        symbol="BTCUSDT",
        timeframe="1m",
        file_path="btc_backup.csv"
    )
    
    # Emitter 2: PostgreSQL
    postgres_emitter = (sf.PostgresEmitter(
            host="localhost",
            dbname="crypto",
            user="postgres",
            password="mysecretpassword"
        )
        .set_model(KlineTable)
        .on_conflict(["source", "symbol", "timeframe", "open_ts"])
    )
    
    # Emitter 3: Logger for monitoring
    logger = sf.Logger(prefix="MONITOR")
    
    # Register all three
    runner.register_emitter(csv_emitter)
    runner.register_emitter(postgres_emitter)
    runner.register_emitter(logger)
    
    print("✓ Data will be:")
    print("  1. Backed up to CSV")
    print("  2. Stored in PostgreSQL")
    print("  3. Logged to console")
    
    await runner.run()


async def pattern4_quad_output():
    """
    Pattern 4: CSV + PostgreSQL + Kafka + Logger
    
    Maximum redundancy: all four output types!
    """
    print("\n" + "="*60)
    print("PATTERN 4: ALL OUTPUTS - CSV + PostgreSQL + Kafka + Logger")
    print("="*60)
    
    runner = sf.BinanceRunner(
        stream_input=sf.DataInput(
            type="kline",
            symbols=["BTCUSDT","ETHUSDT","SOLUSDT"],
            timeframe="1m"
        )
    )
    
    # Emitter 1: CSV (backup)
    csv_emitter = sf.CSVEmitter(
        source="Binance",
        symbol="BTCUSDT",
        timeframe="1m",
        file_path="btc_complete_backup.csv"
    )
    
    # Emitter 2: PostgreSQL (main database)
    postgres_emitter = (sf.PostgresEmitter(
            host="localhost",
            dbname="crypto",
            user="postgres",
            password="mysecretpassword"
        )
        .set_model(KlineTable)
        .on_conflict(["source", "symbol", "timeframe", "open_ts"])
    )
    
    # Emitter 3: Kafka (real-time stream)
    kafka_emitter = sf.KafkaEmitter(
        topic="crypto-all",
        bootstrap_servers="localhost:9092"
    )
    
    # Emitter 4: Logger (monitoring)
    logger = sf.Logger(prefix="FULL-PIPELINE")
    
    # Register all four!
    runner.register_emitter(csv_emitter)
    runner.register_emitter(postgres_emitter)
    runner.register_emitter(kafka_emitter)
    runner.register_emitter(logger)
    
    print("✓ Data will be:")
    print("  1. Backed up to CSV")
    print("  2. Stored in PostgreSQL")
    print("  3. Streamed to Kafka")
    print("  4. Logged to console")
    print("\n  That's FOUR simultaneous outputs!")
    
    await runner.run()


async def pattern5_multi_exchange_multi_output():
    """
    Pattern 5: Multiple Exchanges, Multiple Outputs
    
    Advanced: Stream from multiple exchanges to multiple outputs
    """
    print("\n" + "="*60)
    print("PATTERN 5: Multiple Exchanges → Multiple Outputs")
    print("="*60)
    
    # Shared emitters (all exchanges will use these)
    postgres_emitter = (sf.PostgresEmitter(
            host="localhost",
            dbname="crypto",
            user="postgres",
            password="mysecretpassword"
        )
        .set_model(KlineTable)
        .on_conflict(["source", "symbol", "timeframe", "open_ts"])
    )
    
    kafka_emitter = sf.KafkaEmitter(
        topic="all-exchanges",
        bootstrap_servers="localhost:9092"
    )
    
    logger = sf.Logger(prefix="MULTI-EXCHANGE")
    
    # Binance Runner
    binance_runner = sf.BinanceRunner(
        stream_input=sf.DataInput(
            type="kline",
            symbols=["BTCUSDT","ETHUSDT","SOLUSDT"],
            timeframe="1m"
        )
    )
    binance_runner.register_emitter(postgres_emitter)
    binance_runner.register_emitter(kafka_emitter)
    binance_runner.register_emitter(logger)
    
    # OKX Runner
    okx_runner = sf.OKXRunner(
        stream_input=sf.DataInput(
            type="candle",
            symbols=["BTC-USDT","ETH-USDT","SOL-USDT"],
            timeframe="1m"
        )
    )
    okx_runner.register_emitter(postgres_emitter)
    okx_runner.register_emitter(kafka_emitter)
    okx_runner.register_emitter(logger)
    
    # Kraken Runner
    kraken_runner = sf.KrakenRunner(
        stream_input=sf.DataInput(
            type="ohlc",
            symbols=["BTC/USD","ETH/USD","SOL/USD" ],
            timeframe="1m"
        )
    )
    kraken_runner.register_emitter(postgres_emitter)
    kraken_runner.register_emitter(kafka_emitter)
    kraken_runner.register_emitter(logger)
    
    print("✓ Streaming from 3 exchanges:")
    print("  - Binance BTCUSDT")
    print("  - OKX BTC-USDT")
    print("  - Kraken BTC/USD")
    print("\n✓ To 3 outputs each:")
    print("  - PostgreSQL")
    print("  - Kafka")
    print("  - Logger")
    
    # Run all in parallel
    await asyncio.gather(
        binance_runner.run(),
        okx_runner.run(),
        kraken_runner.run()
    )


async def pattern6_conditional_outputs():
    """
    Pattern 6: Conditional Multi-Output
    
    Different outputs based on configuration/environment
    """
    print("\n" + "="*60)
    print("PATTERN 6: Conditional Multi-Output")
    print("="*60)
    
    # Configuration
    ENVIRONMENT = "production"  # or "development"
    ENABLE_BACKUP = True
    ENABLE_KAFKA = True
    ENABLE_DEBUG = ENVIRONMENT == "development"
    
    runner = sf.BinanceRunner(
        stream_input=sf.DataInput(
            type="kline",
            symbols=["BTCUSDT","ETHUSDT","SOLUSDT"],
            timeframe="1m"
        )
    )
    
    # Always enable PostgreSQL
    postgres_emitter = (sf.PostgresEmitter(
            host="localhost",
            dbname=f"crypto_{ENVIRONMENT}",
            user="postgres",
            password="mysecretpassword"
        )
        .set_model(KlineTable)
        .on_conflict(["source", "symbol", "timeframe", "open_ts"])
    )
    runner.register_emitter(postgres_emitter)
    print("✓ PostgreSQL enabled")
    
    # Conditionally enable CSV backup
    if ENABLE_BACKUP:
        csv_emitter = sf.CSVEmitter(
            source="Binance",
            symbol="BTCUSDT",
            timeframe="1m",
            file_path=f"btc_{ENVIRONMENT}_backup.csv"
        )
        runner.register_emitter(csv_emitter)
        print("✓ CSV backup enabled")
    
    # Conditionally enable Kafka
    if ENABLE_KAFKA:
        kafka_emitter = sf.KafkaEmitter(
            topic=f"crypto-{ENVIRONMENT}",
            bootstrap_servers="localhost:9092"
        )
        runner.register_emitter(kafka_emitter)
        print("✓ Kafka streaming enabled")
    
    # Conditionally enable debug logging
    if ENABLE_DEBUG:
        logger = sf.Logger(prefix=f"DEBUG-{ENVIRONMENT.upper()}")
        runner.register_emitter(logger)
        print("✓ Debug logging enabled")
    
    print(f"\nEnvironment: {ENVIRONMENT}")
    print("Starting multi-output pipeline...")
    
    await runner.run()


async def main():
    """
    Multi-Output Benefits:
    
    ✓ Data redundancy (backup)
    ✓ Different consumers (real-time + historical)
    ✓ Debugging (logger) while saving (database)
    ✓ No performance penalty (async)
    """
    print("""
╔══════════════════════════════════════════════════════════════╗
║          Multi-Output Pipeline Examples                     ║
╚══════════════════════════════════════════════════════════════╝

Available patterns:
1. pattern1_csv_and_logger() - Simple: CSV + Logger
2. pattern2_postgres_and_kafka() - Database + Real-time
3. pattern3_triple_output() - CSV + PostgreSQL + Logger
4. pattern4_quad_output() - ALL FOUR outputs! ⭐
5. pattern5_multi_exchange_multi_output() - Advanced
6. pattern6_conditional_outputs() - Environment-based

Choose one pattern below:
""")
    
    # Uncomment ONE pattern to run:
    await pattern1_csv_and_logger()
    # await pattern2_postgres_and_kafka()
    # await pattern3_triple_output()
    # await pattern4_quad_output()
    # await pattern5_multi_exchange_multi_output()
    # await pattern6_conditional_outputs()


if __name__ == "__main__":
    asyncio.run(main())

