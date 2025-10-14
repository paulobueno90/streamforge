"""
Advanced Transformer - Complex Data Transformations
===================================================

Advanced transformer patterns for real-world scenarios.

Prerequisites:
- streamforge installed

Run:
    python advanced_transformer.py
"""

import asyncio
import time
from datetime import datetime
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String, Float, BigInteger, Boolean
import streamforge as sf




def metadata_enrichment_transformer(data: dict) -> dict:
    """
    Metadata Enrichment: Add System Metadata
    
    Add information about the ingestion process
    """
    return {
        **data,
        "ingestion_timestamp": int(time.time() * 1000),
        "ingestion_date": datetime.now().isoformat(),
        "pipeline_version": "v2.0",
        "data_quality_score": 100.0,
        "processing_latency_ms": 0,  # Would calculate actual latency in production
    }


async def example_1_metadata():
    """
    Example 1: Metadata Enrichment
    
    Add system metadata to track data lineage
    """
    print("\n" + "="*60)
    print("Example 1: Metadata Enrichment")
    print("="*60)
    
    csv_emitter = sf.CSVEmitter(
        source="Binance",
        symbol="BTCUSDT",
        timeframe="1m",
        file_path="btc_with_metadata.csv",
        transformer_function=metadata_enrichment_transformer
    )
    
    runner = sf.BinanceRunner(
        stream_input=sf.DataInput(
            type="kline",
            symbols=["BTCUSDT", "ETHUSDT", "SOLUSDT"],
            timeframe="1m"
        )
    )
    
    runner.register_emitter(csv_emitter)
    
    print("✓ Adding metadata:")
    print("  - ingestion_timestamp")
    print("  - pipeline_version")
    print("  - data_quality_score")
    
    await runner.run()


def conditional_transformer(data: dict) -> dict:
    """
    Conditional Transformer: Different Logic Based on Conditions
    
    Apply different transformations based on data values
    """
    price_change_pct = ((data["close"] - data["open"]) / data["open"]) * 100
    
    # Flag significant movements
    if abs(price_change_pct) > 1.0:
        movement_type = "significant"
        alert = True
    elif abs(price_change_pct) > 0.5:
        movement_type = "moderate"
        alert = False
    else:
        movement_type = "minimal"
        alert = False
    
    # Add volume category
    if data["volume"] > 1000:
        volume_category = "high"
    elif data["volume"] > 500:
        volume_category = "medium"
    else:
        volume_category = "low"
    
    return {
        **data,
        "price_change_pct": price_change_pct,
        "movement_type": movement_type,
        "alert": alert,
        "volume_category": volume_category,
    }


async def example_2_conditional():
    """
    Example 2: Conditional Transformation
    
    Different logic based on data values
    """
    print("\n" + "="*60)
    print("Example 2: Conditional Transformation")
    print("="*60)
    
    csv_emitter = sf.CSVEmitter(
        source="Binance",
        symbol="BTCUSDT",
        timeframe="1m",
        file_path="btc_categorized.csv",
        transformer_function=conditional_transformer
    )
    
    runner = sf.BinanceRunner(
        stream_input=sf.DataInput(
            type="kline",
            symbols=["BTCUSDT", "ETHUSDT", "SOLUSDT"],
            timeframe="1m"
        )
    )
    
    runner.register_emitter(csv_emitter)
    
    print("✓ Categorizing data:")
    print("  - movement_type (significant/moderate/minimal)")
    print("  - alert (True/False)")
    print("  - volume_category (high/medium/low)")
    
    await runner.run()


def technical_indicators_transformer(data: dict) -> dict:
    """
    Technical Indicators: Calculate Trading Indicators
    
    Add common technical analysis metrics
    """
    open_price = data["open"]
    high = data["high"]
    low = data["low"]
    close = data["close"]
    
    # True Range (for ATR calculation)
    true_range = high - low
    
    # Typical Price
    typical_price = (high + low + close) / 3
    
    # Candle body and wicks
    body = abs(close - open_price)
    upper_wick = high - max(open_price, close)
    lower_wick = min(open_price, close) - low
    
    # Candle patterns
    is_doji = body < (true_range * 0.1)  # Small body
    is_hammer = lower_wick > (body * 2) and upper_wick < body
    is_shooting_star = upper_wick > (body * 2) and lower_wick < body
    
    return {
        **data,
        "true_range": true_range,
        "typical_price": typical_price,
        "body_size": body,
        "upper_wick": upper_wick,
        "lower_wick": lower_wick,
        "is_doji": is_doji,
        "is_hammer": is_hammer,
        "is_shooting_star": is_shooting_star,
        "body_to_range_ratio": body / true_range if true_range > 0 else 0,
    }


async def example_3_technical_indicators():
    """
    Example 3: Technical Indicators
    
    Calculate trading indicators from OHLC data
    """
    print("\n" + "="*60)
    print("Example 3: Technical Indicators")
    print("="*60)
    
    csv_emitter = sf.CSVEmitter(
        source="Binance",
        symbol="BTCUSDT",
        timeframe="1m",
        file_path="btc_with_indicators.csv",
        transformer_function=technical_indicators_transformer
    )
    
    runner = sf.BinanceRunner(
        stream_input=sf.DataInput(
            type="kline",
            symbols=["BTCUSDT", "ETHUSDT", "SOLUSDT"],
            timeframe="1m"
        )
    )
    
    runner.register_emitter(csv_emitter)
    
    print("✓ Calculating indicators:")
    print("  - true_range")
    print("  - typical_price")
    print("  - candle patterns (doji, hammer, shooting_star)")
    print("  - body_to_range_ratio")
    
    await runner.run()


def normalization_transformer(data: dict) -> dict:
    """
    Data Normalization: Ensure Data Quality
    
    Validate and normalize data before saving
    """
    # Round prices to reasonable precision
    precision = 2
    
    # Ensure no negative values
    volume = max(0, data.get("volume", 0))
    
    # Ensure OHLC relationships are valid
    open_price = round(data["open"], precision)
    high = round(max(data["high"], open_price, data["close"]), precision)
    low = round(min(data["low"], open_price, data["close"]), precision)
    close = round(data["close"], precision)
    
    return {
        **data,
        "open": open_price,
        "high": high,
        "low": low,
        "close": close,
        "volume": round(volume, 6),
        "data_validated": True,
    }


async def example_4_normalization():
    """
    Example 4: Data Normalization
    
    Validate and clean data before saving
    """
    print("\n" + "="*60)
    print("Example 4: Data Normalization")
    print("="*60)
    
    csv_emitter = sf.CSVEmitter(
        source="Binance",
        symbol="BTCUSDT",
        timeframe="1m",
        file_path="btc_normalized.csv",
        transformer_function=normalization_transformer
    )
    
    runner = sf.BinanceRunner(
        stream_input=sf.DataInput(
            type="kline",
            symbols=["BTCUSDT", "ETHUSDT", "SOLUSDT"],
            timeframe="1m"
        )
    )
    
    runner.register_emitter(csv_emitter)
    
    print("✓ Normalizing data:")
    print("  - Rounding to 2 decimal places")
    print("  - Ensuring valid OHLC relationships")
    print("  - Removing negative volumes")
    
    await runner.run()


def chained_transformers(data: dict) -> dict:
    """
    Chained Transformers: Apply Multiple Transformations
    
    Combine multiple transformations in sequence
    """
    # Step 1: Add computed fields
    data = add_computed_fields_transformer(data)
    
    # Step 2: Add metadata
    data = metadata_enrichment_transformer(data)
    
    # Step 3: Normalize
    data = normalization_transformer(data)
    
    return data


def add_computed_fields_transformer(data: dict) -> dict:
    """Helper: Add computed fields"""
    return {
        **data,
        "price_change_pct": ((data["close"] - data["open"]) / data["open"]) * 100,
        "is_bullish": data["close"] > data["open"],
    }


async def example_5_chained():
    """
    Example 5: Chained Transformers
    
    Apply multiple transformations in sequence
    """
    print("\n" + "="*60)
    print("Example 5: Chained Transformers")
    print("="*60)
    
    csv_emitter = sf.CSVEmitter(
        source="Binance",
        symbol="BTCUSDT",
        timeframe="1m",
        file_path="btc_fully_processed.csv",
        transformer_function=chained_transformers
    )
    
    runner = sf.BinanceRunner(
        stream_input=sf.DataInput(
            type="kline",
            symbols=["BTCUSDT", "ETHUSDT", "SOLUSDT"],
            timeframe="1m"
        )
    )
    
    runner.register_emitter(csv_emitter)
    
    print("✓ Applying chained transformations:")
    print("  1. Computed fields")
    print("  2. Metadata enrichment")
    print("  3. Data normalization")
    
    await runner.run()


async def main():
    """
    Advanced Transformer Patterns:
    
    ✓ Stateful transformations
    ✓ Metadata enrichment
    ✓ Conditional logic
    ✓ Technical indicators
    ✓ Data normalization
    ✓ Chained transformations
    """
    print("""
╔══════════════════════════════════════════════════════════════╗
║           Advanced Transformer Examples                     ║
╚══════════════════════════════════════════════════════════════╝

Available examples:
1. example_1_metadata() - Track state across candles
2. example_     2_metadata() - Add system metadata
3. example3_conditional() - Conditional logic
4. example4_technical_indicators() - Trading indicators
5. example5_normalization() - Data validation
6. example6_chained() - Multiple transformations

Choose one example below:
""")
    
    # Uncomment ONE example to run:
    # await example1_stateful()
    # await example_1_metadata()
    await example_2_conditional()
    # await example_3_technical_indicators()
    # await example_4_normalization()
    # await example_5_chained()


if __name__ == "__main__":
    asyncio.run(main())

