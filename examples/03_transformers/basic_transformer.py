"""
Basic Transformer - Transform Data Before Saving
================================================

Transformers allow you to modify data before it's emitted to outputs.

Use Cases:
✓ Rename columns to match your database schema
✓ Convert units (e.g., satoshis to BTC)
✓ Add computed fields
✓ Filter fields
✓ Format timestamps

Prerequisites:
- streamforge installed

Run:
    python basic_transformer.py
"""

import asyncio
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String, Float, BigInteger
import streamforge as sf


Base = declarative_base()


# Database table with DIFFERENT column names
class CustomKlineTable(Base):
    __tablename__ = 'custom_klines'
    
    # Different naming convention from default Kline model
    exchange = Column(String, primary_key=True)      # instead of 'source'
    ticker = Column(String, primary_key=True)        # instead of 'symbol'
    tf = Column(String, primary_key=True)            # instead of 'timeframe'
    timestamp = Column(BigInteger, primary_key=True) # instead of 'open_ts'
    
    # Short OHLCV names
    o = Column(Float)  # instead of 'open'
    h = Column(Float)  # instead of 'high'
    l = Column(Float)  # instead of 'low'
    c = Column(Float)  # instead of 'close'
    v = Column(Float)  # instead of 'volume'


def basic_rename_transformer(data: dict) -> dict:
    """
    Basic Transformer: Rename Fields
    
    Map StreamForge's default field names to your database schema
    """
    return {
        "exchange": data["source"],
        "ticker": data["symbol"],
        "tf": data["timeframe"],
        "timestamp": data["open_ts"],
        "o": data["open"],
        "h": data["high"],
        "l": data["low"],
        "c": data["close"],
        "v": data["volume"]
    }


async def example1_basic_transform():
    """
    Example 1: Basic Field Renaming
    
    Your database has different column names than StreamForge's defaults
    """
    print("\n" + "="*60)
    print("Example 1: Basic Field Renaming")
    print("="*60)
    
    emitter = (sf.PostgresEmitter(
            host="localhost",
            dbname="crypto",
            user="postgres",
            password="mysecretpassword"
        )
        .set_model(CustomKlineTable)
        .set_transformer(basic_rename_transformer)
        .on_conflict(["exchange", "ticker", "tf", "timestamp"])
    )
    
    runner = sf.BinanceRunner(
        stream_input=sf.DataInput(
            type="kline",
            symbols=["BTCUSDT"],
            timeframe="1m"
        )
    )
    
    runner.register_emitter(emitter)
    
    print("✓ Transformer will rename fields:")
    print("  source → exchange")
    print("  symbol → ticker")
    print("  timeframe → tf")
    print("  open_ts → timestamp")
    print("  open/high/low/close/volume → o/h/l/c/v")
    
    await runner.run()


def filter_fields_transformer(data: dict) -> dict:
    """
    Filter Transformer: Only Keep Specific Fields
    
    Remove unnecessary fields to save space
    """
    return {
        "source": data["source"],
        "symbol": data["symbol"],
        "timeframe": data["timeframe"],
        "open_ts": data["open_ts"],
        "close": data["close"],  # Only keep close price
        "volume": data["volume"]  # Only keep volume
        # Removed: open, high, low, end_ts
    }


async def example2_filter_fields():
    """
    Example 2: Filter Fields
    
    Only save specific fields (e.g., just close price and volume)
    """
    print("\n" + "="*60)
    print("Example 2: Filter Fields")
    print("="*60)
    
    # For CSV
    csv_emitter = sf.CSVEmitter(
        source="Binance",
        symbol="BTCUSDT",
        timeframe="1m",
        file_path="btc_close_volume_only.csv",
        transformer_function=filter_fields_transformer
    )
    
    runner = sf.BinanceRunner(
        stream_input=sf.DataInput(
            type="kline",
            symbols=["BTCUSDT"],
            timeframe="1m"
        )
    )
    
    runner.register_emitter(csv_emitter)
    
    print("✓ Only saving: source, symbol, timeframe, open_ts, close, volume")
    print("✓ Filtered out: open, high, low, end_ts")
    
    await runner.run()


def add_computed_fields_transformer(data: dict) -> dict:
    """
    Computed Fields Transformer: Add Calculated Values
    
    Add new fields based on existing data
    """
    return {
        **data,  # Keep all original fields
        # Add computed fields
        "price_range": data["high"] - data["low"],
        "price_change": data["close"] - data["open"],
        "price_change_pct": ((data["close"] - data["open"]) / data["open"]) * 100,
        "is_green": data["close"] > data["open"],
        "body_size": abs(data["close"] - data["open"]),
        "upper_wick": data["high"] - max(data["open"], data["close"]),
        "lower_wick": min(data["open"], data["close"]) - data["low"],
    }


async def example3_computed_fields():
    """
    Example 3: Add Computed Fields
    
    Calculate additional metrics before saving
    """
    print("\n" + "="*60)
    print("Example 3: Add Computed Fields")
    print("="*60)
    
    csv_emitter = sf.CSVEmitter(
        source="Binance",
        symbol="BTCUSDT",
        timeframe="1m",
        file_path="btc_with_indicators.csv",
        transformer_function=add_computed_fields_transformer
    )
    
    runner = sf.BinanceRunner(
        stream_input=sf.DataInput(
            type="kline",
            symbols=["BTCUSDT"],
            timeframe="1m"
        )
    )
    
    runner.register_emitter(csv_emitter)
    
    print("✓ Adding computed fields:")
    print("  - price_range")
    print("  - price_change")
    print("  - price_change_pct")
    print("  - is_green (bullish/bearish)")
    print("  - body_size")
    print("  - upper_wick")
    print("  - lower_wick")
    
    await runner.run()


def convert_units_transformer(data: dict) -> dict:
    """
    Unit Conversion Transformer
    
    Convert to different units or scale
    """
    return {
        **data,
        # Convert volume to millions
        "volume": data["volume"] / 1_000_000,
        "volume_unit": "millions",
        # Add USD value estimates
        "volume_usd": data["volume"] * data["close"],
    }


async def example4_unit_conversion():
    """
    Example 4: Unit Conversion
    
    Convert values to different units
    """
    print("\n" + "="*60)
    print("Example 4: Unit Conversion")
    print("="*60)
    
    csv_emitter = sf.CSVEmitter(
        source="Binance",
        symbol="BTCUSDT",
        timeframe="1m",
        file_path="btc_converted_units.csv",
        transformer_function=convert_units_transformer
    )
    
    runner = sf.BinanceRunner(
        stream_input=sf.DataInput(
            type="kline",
            symbols=["BTCUSDT"],
            timeframe="1m"
        )
    )
    
    runner.register_emitter(csv_emitter)
    
    print("✓ Converting units:")
    print("  - volume → millions")
    print("  - adding volume_usd")
    
    await runner.run()


async def main():
    """
    Transformer Benefits:
    
    ✓ Adapt data to your schema
    ✓ Add computed fields
    ✓ Filter unnecessary data
    ✓ Convert units
    ✓ Enrich data
    """
    print("""
╔══════════════════════════════════════════════════════════════╗
║              Basic Transformer Examples                     ║
╚══════════════════════════════════════════════════════════════╝

Available examples:
1. example1_basic_transform() - Rename fields
2. example2_filter_fields() - Keep only specific fields
3. example3_computed_fields() - Add calculated values
4. example4_unit_conversion() - Convert units

Choose one example below:
""")
    
    # Uncomment ONE example to run:
    await example1_basic_transform()
    # await example2_filter_fields()
    # await example3_computed_fields()
    # await example4_unit_conversion()


if __name__ == "__main__":
    asyncio.run(main())

