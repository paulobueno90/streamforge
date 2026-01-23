"""
Warmup Configurations - Understanding Historical Data Loading
=============================================================

Warmup is the process of loading historical data before starting live streaming.
It's essential for timeframe aggregation and ensuring smooth data flow.

Key Concepts:
- active_warmup: Whether to load historical data
- emit_warmup: Whether to save historical data to outputs
- aggregate_list: Higher timeframes to calculate from base timeframe

Prerequisites:
- streamforge installed

Run:
    python warmup_configs.py
"""

import asyncio
import streamforge as sf

sf.show_logs()


async def scenario1_no_warmup():
    """
    Scenario 1: No Warmup
    
    Start fresh without any historical data.
    
    When to use:
    - No aggregation needed
    - Only care about future data
    - Want fastest startup
    
    Behavior:
    - Starts immediately
    - No historical context
    - Aggregation won't work properly
    """
    print("\n" + "="*60)
    print("Scenario 1: No Warmup")
    print("="*60)
    
    runner = sf.BinanceRunner(
        stream_input=sf.DataInput(
            type="kline",
            symbols=["BTCUSDT"],
            timeframe="1m"
        ),
        active_warmup=False  # No historical data
    )
    # Internal logging is handled by sf.config.logger
    
    print("✓ Configuration:")
    print("  - active_warmup=False")
    print("  - Starts immediately")
    print("  - No historical context")
    print("\n⚠️  DON'T use this with aggregation!")
    
    await runner.run()


async def scenario2_warmup_no_emit():
    """
    Scenario 2: Warmup but Don't Emit (DEFAULT)
    
    Load historical data for aggregation context, but don't save it.
    
    When to use:
    - Need aggregation to work correctly
    - Don't want to backfill historical data
    - Most common scenario for live streaming
    
    Behavior:
    - Loads recent historical data
    - Uses it for aggregation calculations
    - Doesn't save historical data to outputs
    - Only emits new live data
    """
    print("\n" + "="*60)
    print("Scenario 2: Warmup but Don't Emit (Recommended)")
    print("="*60)
    
    runner = sf.BinanceRunner(
        stream_input=sf.DataInput(
            type="kline",
            symbols=["BTCUSDT"],
            timeframe="1m",
            aggregate_list=["5m", "15m", "1h"]  # Need warmup for this!
        ),
        active_warmup=True,   # Load historical data
        emit_warmup=False     # Don't save it (DEFAULT)
    )
    
    # Internal logging is handled by sf.config.logger
    
    print("✓ Configuration:")
    print("  - active_warmup=True")
    print("  - emit_warmup=False (default)")
    print("  - Loads historical data for context")
    print("  - Only emits new live data")
    print("\n✅ This is the recommended setup for live streaming with aggregation")
    
    await runner.run()


async def scenario3_warmup_and_emit():
    """
    Scenario 3: Warmup AND Emit
    
    Load historical data AND save it to outputs.
    
    When to use:
    - Want to backfill recent history
    - Starting fresh database
    - Need both historical and live data
    
    Behavior:
    - Loads recent historical data
    - Saves historical data to outputs
    - Continues with live data
    """
    print("\n" + "="*60)
    print("Scenario 3: Warmup AND Emit (Backfill Mode)")
    print("="*60)
    
    runner = sf.BinanceRunner(
        stream_input=sf.DataInput(
            type="kline",
            symbols=["BTCUSDT"],
            timeframe="1m",
            aggregate_list=["5m", "15m"]
        ),
        active_warmup=True,   # Load historical data
        emit_warmup=True      # Save it too!
    )
    
    # Internal logging is handled by sf.config.logger
    
    print("✓ Configuration:")
    print("  - active_warmup=True")
    print("  - emit_warmup=True")
    print("  - Loads AND saves historical data")
    print("  - Then continues with live data")
    print("\n⭐ Good for initial database population")
    
    await runner.run()


async def scenario4_auto_warmup():
    """
    Scenario 4: Automatic Warmup Decision
    
    StreamForge automatically decides if warmup is needed.
    
    Logic:
    - If aggregate_list is specified → warmup enabled
    - If no aggregation → warmup disabled (unless forced)
    """
    print("\n" + "="*60)
    print("Scenario 4: Automatic Warmup Decision")
    print("="*60)
    
    # With aggregation → warmup automatically enabled
    runner = sf.BinanceRunner(
        stream_input=sf.DataInput(
            type="kline",
            symbols=["BTCUSDT"],
            timeframe="1m",
            aggregate_list=["5m"]  # This triggers auto-warmup
        )
        # active_warmup not specified → automatic!
    )
    
    # Internal logging is handled by sf.config.logger
    
    print("✓ Configuration:")
    print("  - active_warmup not specified")
    print("  - aggregate_list=['5m'] specified")
    print("  - Warmup automatically enabled")
    print("\n✅ StreamForge is smart about warmup!")
    
    await runner.run()


async def scenario5_warmup_comparison():
    """
    Scenario 5: Side-by-Side Comparison
    
    See the difference between warmup and no warmup
    """
    print("\n" + "="*60)
    print("Scenario 5: Warmup Comparison")
    print("="*60)
    
    # Runner 1: With warmup
    runner_with_warmup = sf.BinanceRunner(
        stream_input=sf.DataInput(
            type="kline",
            symbols=["BTCUSDT"],
            timeframe="1m",
            aggregate_list=["5m"]
        ),
        active_warmup=True,
        emit_warmup=False
    )
    # Internal logging is handled by sf.config.logger
    
    # Runner 2: Without warmup
    runner_without_warmup = sf.BinanceRunner(
        stream_input=sf.DataInput(
            type="kline",
            symbols=["ETHUSDT"],
            timeframe="1m",
            aggregate_list=["5m"]
        ),
        active_warmup=False
    )
    # Internal logging is handled by sf.config.logger
    
    print("✓ Running two runners side by side:")
    print("  - BTCUSDT WITH warmup")
    print("  - ETHUSDT WITHOUT warmup")
    print("\n⚠️  Watch how NO-WARMUP 5m aggregation is incomplete at first!")
    
    # Run both in parallel
    await asyncio.gather(
        runner_with_warmup.run(),
        runner_without_warmup.run()
    )


async def scenario6_production_setup():
    """
    Scenario 6: Production Best Practices
    
    Recommended warmup configuration for production
    """
    print("\n" + "="*60)
    print("Scenario 6: Production Best Practices")
    print("="*60)
    
    from sqlalchemy.orm import declarative_base
    from sqlalchemy import Column, String, Float, BigInteger
    
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
    
    # Production setup
    runner = sf.BinanceRunner(
        stream_input=sf.DataInput(
            type="kline",
            symbols=["BTCUSDT", "ETHUSDT", "SOLUSDT"],
            timeframe="1m",
            aggregate_list=["5m", "15m", "1h", "4h"]
        ),
        active_warmup=True,          # ✓ Enable warmup for aggregation
        emit_warmup=False,           # ✓ Don't duplicate historical data
        emit_only_closed_candles=True  # ✓ Only emit completed candles
    )
    
    # Database with upsert (handle any duplicates gracefully)
    emitter = (sf.PostgresEmitter(
            host="localhost",
            dbname="crypto_production",
            user="postgres",
            password="mysecretpassword"
        )
        .set_model(KlineTable)
        .on_conflict(["source", "symbol", "timeframe", "open_ts"])
    )
    
    runner.register_emitter(emitter)
    
    print("✓ Production Configuration:")
    print("  - active_warmup=True (for aggregation)")
    print("  - emit_warmup=False (no duplicate historical data)")
    print("  - emit_only_closed_candles=True (complete data only)")
    print("  - upsert enabled (handle duplicates gracefully)")
    print("\n✅ This is the recommended production setup!")
    
    await runner.run()


async def main():
    """
    Warmup Decision Guide:
    
    No aggregation needed?
      → active_warmup=False
    
    Need aggregation for live streaming?
      → active_warmup=True, emit_warmup=False (DEFAULT)
    
    Starting fresh database?
      → active_warmup=True, emit_warmup=True
    
    Not sure?
      → Don't specify, let StreamForge decide!
    """
    print("""
╔══════════════════════════════════════════════════════════════╗
║           Warmup Configuration Examples                     ║
╚══════════════════════════════════════════════════════════════╝

What is Warmup?
- Loading recent historical data before streaming
- Essential for timeframe aggregation
- Provides context for calculations

Available scenarios:
1. scenario1_no_warmup() - No historical data
2. scenario2_warmup_no_emit() - Load history, don't save (RECOMMENDED) ⭐
3. scenario3_warmup_and_emit() - Load AND save history
4. scenario4_auto_warmup() - Let StreamForge decide
5. scenario5_warmup_comparison() - See the difference
6. scenario6_production_setup() - Production best practices ⭐

Choose one scenario below:
""")
    
    # Uncomment ONE scenario to run:
    # await scenario1_no_warmup()
    await scenario2_warmup_no_emit()
    # await scenario3_warmup_and_emit()
    # await scenario4_auto_warmup()
    # await scenario5_warmup_comparison()
    # await scenario6_production_setup()


if __name__ == "__main__":
    asyncio.run(main())

