"""
PostgreSQL Emitter - Method Chaining vs Inplace
==============================================

Understanding the difference between method chaining and inplace modifications.

Key Concept:
- inplace=False (default): Returns self, enables method chaining
- inplace=True: Returns None, modifies object directly

When to use which:
- Method chaining: Cleaner, more functional style
- Inplace: When you need to configure step-by-step or conditionally

Prerequisites:
- PostgreSQL server running
- streamforge installed

Run:
    python postgres_method_chaining.py
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
    identifier = Column(String)


def example_transformer(data: dict):
    """Example transformer function"""
    identifier = ""
    identifier += data.get('source', 'unknown')
    identifier += "-"
    identifier += data.get('symbol', 'unknown')
    identifier += "-"
    identifier += data.get('timeframe', 'unknown')
    
    return {
        **data,
        "identifier": identifier,
    }


async def pattern1_method_chaining():
    """
    Pattern 1: Method Chaining (inplace=False - default)
    
    ✅ Pros:
    - Clean, fluent interface
    - All configuration in one expression
    - Functional programming style
    
    ⚠️ Cons:
    - Can become hard to read if too many methods
    - Can't conditionally configure
    """
    print("\n" + "="*60)
    print("PATTERN 1: Method Chaining (inplace=False)")
    print("="*60)
    
    # All methods return self, so we can chain them
    emitter = (sf.PostgresEmitter(
            host="localhost",
            dbname="crypto",
            user="postgres",
            password="mysecretpassword"
        )
        .set_model(KlineTable)  # Returns self
        .on_conflict(["source", "symbol", "timeframe", "open_ts"])  # Returns self
        .set_transformer(example_transformer)  # Returns self
    )
    
    # emitter is ready to use
    runner = sf.BinanceRunner(
        stream_input=sf.DataInput(type="kline", symbols=["BTCUSDT","ETHUSDT","SOLUSDT"], timeframe="1m")
    )
    runner.register_emitter(emitter)
    
    print("✓ Emitter configured with method chaining")
    await runner.run()


async def pattern2_inplace():
    """
    Pattern 2: Inplace Modification (inplace=True)
    
    ✅ Pros:
    - Clear step-by-step configuration
    - Easy to add conditional logic
    - Good for complex setups
    
    ⚠️ Cons:
    - More verbose
    - Methods return None (no chaining)
    """
    print("\n" + "="*60)
    print("PATTERN 2: Inplace Modification (inplace=True)")
    print("="*60)
    
    # Create emitter
    emitter = sf.PostgresEmitter(
        host="localhost",
        dbname="crypto",
        user="postgres",
        password="mysecretpassword"
    )
    
    # Configure step by step - each returns None
    emitter.set_model(KlineTable, inplace=True)
    emitter.on_conflict(["source", "symbol", "timeframe", "open_ts"], inplace=True)
    emitter.set_transformer(example_transformer, inplace=True)
    
    # emitter is ready to use
    runner = sf.BinanceRunner(
        stream_input=sf.DataInput(type="kline", symbols=["BTCUSDT","ETHUSDT","SOLUSDT"], timeframe="1m")
    )
    runner.register_emitter(emitter)
    
    print("✓ Emitter configured with inplace modifications")
    await runner.run()


async def pattern3_conditional():
    """
    Pattern 3: Conditional Configuration
    
    Best use case for inplace=True: When you need conditional logic
    """
    print("\n" + "="*60)
    print("PATTERN 3: Conditional Configuration")
    print("="*60)
    
    # Configuration variables
    USE_UPSERT = True
    USE_TRANSFORMER = False
    ENVIRONMENT = "production"
    
    # Create emitter
    emitter = sf.PostgresEmitter(
        host="localhost",
        dbname="crypto" if ENVIRONMENT == "production" else "crypto_dev",
        user="postgres",
        password="mysecretpassword"
    )
    
    # Always set model
    emitter.set_model(KlineTable, inplace=True)
    
    # Conditionally enable upsert
    if USE_UPSERT:
        print("✓ Enabling upsert mode")
        emitter.on_conflict(["source", "symbol", "timeframe", "open_ts"], inplace=True)
    
    # Conditionally add transformer
    if USE_TRANSFORMER:
        print("✓ Adding transformer")
        emitter.set_transformer(example_transformer, inplace=True)
    
    runner = sf.BinanceRunner(
        stream_input=sf.DataInput(type="kline", symbols=["BTCUSDT","ETHUSDT","SOLUSDT"], timeframe="1m")
    )
    runner.register_emitter(emitter)
    
    print("✓ Emitter configured conditionally")
    await runner.run()


async def pattern4_mixed():
    """
    Pattern 4: Mixed Approach
    
    You can mix both styles! Start with chaining, finish with inplace
    """
    print("\n" + "="*60)
    print("PATTERN 4: Mixed Approach")
    print("="*60)
    
    # Initial setup with chaining
    emitter = (sf.PostgresEmitter(
            host="localhost",
            dbname="crypto",
            user="postgres",
            password="mysecretpassword"
        )
        .set_model(KlineTable)
        .on_conflict(["source", "symbol", "timeframe", "open_ts"])
    )
    
    # Later, add transformer with inplace
    USE_TRANSFORMER = True
    if USE_TRANSFORMER:
        emitter.set_transformer(example_transformer, inplace=True)
    
    runner = sf.BinanceRunner(
        stream_input=sf.DataInput(type="kline", symbols=["BTCUSDT","ETHUSDT","SOLUSDT"], timeframe="1m")
    )
    runner.register_emitter(emitter)
    
    print("✓ Emitter configured with mixed approach")
    await runner.run()


async def main():
    """
    Summary:
    
    Use Method Chaining (inplace=False) when:
    - You know all configuration upfront
    - You want clean, concise code
    - Configuration is static
    
    Use Inplace (inplace=True) when:
    - Configuration is conditional
    - You need step-by-step setup
    - Configuration happens in different places
    """
    print("""
╔══════════════════════════════════════════════════════════════╗
║      PostgreSQL Emitter: Method Chaining vs Inplace         ║
╚══════════════════════════════════════════════════════════════╝

Available patterns:
1. pattern1_method_chaining() - Fluent interface
2. pattern2_inplace() - Step-by-step configuration
3. pattern3_conditional() - Conditional logic
4. pattern4_mixed() - Combining both styles

Choose one pattern below:
""")
    
    # Uncomment ONE pattern to run:
    await pattern1_method_chaining()
    # await pattern2_inplace()
    # await pattern3_conditional()
    # await pattern4_mixed()


if __name__ == "__main__":
    asyncio.run(main())

