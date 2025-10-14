# Backfilling

Load historical data from exchanges to populate databases or create datasets. Backfilling is essential for initializing databases, analysis, and backtesting.

---

## What is Backfilling?

Backfilling downloads historical OHLC/Kline data from exchange APIs:

```python
backfiller = sf.BinanceBackfilling(
    symbol="BTCUSDT",
    timeframe="1m",
    from_date="2024-01-01",
    to_date="2024-12-31"
)

backfiller.run()  # Downloads year of data
```

**Key Differences from Streaming:**

| Feature | Streaming | Backfilling |
|---------|-----------|-------------|
| **Data Source** | WebSocket | REST API |
| **Execution** | `async` | Sync |
| **Speed** | Real-time | Batch download |
| **Purpose** | Live data | Historical data |
| **Method** | `runner.run()` | `backfiller.run()` |

---

## Basic Usage

### Binance Backfilling

```python
import streamforge as sf

backfiller = sf.BinanceBackfilling(
    symbol="BTCUSDT",
    timeframe="1m",
    from_date="2024-10-01",
    to_date="2024-10-31"
)

# Defaults to CSV if no emitter registered
backfiller.run()
```

**Output:** `Binance-BTCUSDT-1m-2024-10-01_2024-10-31.csv`

### OKX Backfilling

```python
backfiller = sf.OkxBackfilling(
    symbol="BTC-USDT",      # OKX format
    timeframe="1m",
    from_date="2024-10-01",
    to_date="2024-10-31"
)

backfiller.run()
```

---

## Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `symbol` | `str` | Trading pair | `"BTCUSDT"` |
| `timeframe` | `str` | Candle interval | `"1m"`, `"1h"`, `"1d"` |
| `from_date` | `str` | Start date | `"2024-01-01"` |
| `to_date` | `str` | End date | `"2024-12-31"` or `"now"` |

### Date Formats

Flexible date formats:

```python
# YYYY-MM-DD
from_date="2024-01-01"

# YYYY-MM-DD HH:MM:SS
from_date="2024-01-01 12:00:00"

# Special: "now"
to_date="now"  # Until present
```

---

## Output Destinations

### Default: CSV

If no emitter is registered, defaults to CSV:

```python
backfiller = sf.BinanceBackfilling(
    symbol="BTCUSDT",
    timeframe="1h",
    from_date="2024-01-01",
    to_date="2024-12-31"
)

backfiller.run()
# Creates: Binance-BTCUSDT-1h-2024-01-01_2024-12-31.csv
```

### PostgreSQL

Load directly into database:

```python
import streamforge as sf
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

# Create emitter with upsert
postgres = (sf.PostgresEmitter(
        host="localhost",
        dbname="crypto",
        user="postgres",
        password="secret"
    )
    .set_model(KlineTable)
    .on_conflict(["source", "symbol", "timeframe", "open_ts"])  # Important!
)

# Backfill
backfiller = sf.BinanceBackfilling(
    symbol="BTCUSDT",
    timeframe="1m",
    from_date="2024-01-01",
    to_date="2024-12-31"
)

backfiller.register_emitter(postgres)
backfiller.run()
```

!!! warning "Always Use Upsert"
    Always enable `on_conflict()` when backfilling to PostgreSQL. This allows safe re-running without duplicates.

### Custom Path for CSV

```python
backfiller = sf.BinanceBackfilling(
    symbol="BTCUSDT",
    timeframe="1m",
    from_date="2024-01-01",
    to_date="2024-12-31",
    file_path="my_custom_name.csv"  # Custom filename
)

backfiller.run()
```

---

## Complete Examples

### Example 1: Simple CSV Backfill

```python
import streamforge as sf

def backfill_to_csv():
    """Backfill BTC data to CSV"""
    
    backfiller = sf.BinanceBackfilling(
        symbol="BTCUSDT",
        timeframe="1h",
        from_date="2024-01-01",
        to_date="2024-12-31"
    )
    
    print("Starting backfill...")
    backfiller.run()
    print("✓ Backfill complete!")

if __name__ == "__main__":
    backfill_to_csv()
```

### Example 2: PostgreSQL Backfill

```python
import streamforge as sf
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

def backfill_to_postgres():
    """Backfill to PostgreSQL database"""
    
    # Create emitter
    postgres = (sf.PostgresEmitter(
            host="localhost",
            dbname="crypto",
            user="postgres",
            password="mysecretpassword"
        )
        .set_model(KlineTable)
        .on_conflict(["source", "symbol", "timeframe", "open_ts"])
    )
    
    # Backfill
    backfiller = sf.BinanceBackfilling(
        symbol="BTCUSDT",
        timeframe="1m",
        from_date="2024-10-01",
        to_date="2024-10-31"
    )
    
    backfiller.register_emitter(postgres)
    
    print("Backfilling to PostgreSQL...")
    backfiller.run()
    print("✓ Done!")

if __name__ == "__main__":
    backfill_to_postgres()
```

### Example 3: Multiple Symbols

Backfill multiple cryptocurrencies:

```python
import streamforge as sf
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

def backfill_multiple_symbols():
    """Backfill multiple symbols to database"""
    
    symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "ADAUSDT"]
    
    postgres = (sf.PostgresEmitter(
            host="localhost",
            dbname="crypto",
            user="postgres",
            password="secret"
        )
        .set_model(KlineTable)
        .on_conflict(["source", "symbol", "timeframe", "open_ts"])
    )
    
    for symbol in symbols:
        print(f"\n📊 Backfilling {symbol}...")
        
        backfiller = sf.BinanceBackfilling(
            symbol=symbol,
            timeframe="1h",
            from_date="2024-01-01",
            to_date="2024-12-31"
        )
        
        backfiller.register_emitter(postgres)
        backfiller.run()
        
        print(f"✓ {symbol} complete!")
    
    print("\n✓ All symbols backfilled!")

if __name__ == "__main__":
    backfill_multiple_symbols()
```

### Example 4: With Transformer

Transform data during backfilling:

```python
import streamforge as sf

def price_transformer(data: dict) -> dict:
    """Add computed fields"""
    return {
        **data,
        "price_change_pct": ((data["close"] - data["open"]) / data["open"]) * 100,
        "is_bullish": data["close"] > data["open"],
        "price_range": data["high"] - data["low"]
    }

def backfill_with_transformation():
    """Backfill with data transformation"""
    
    backfiller = sf.BinanceBackfilling(
        symbol="BTCUSDT",
        timeframe="1h",
        from_date="2024-01-01",
        to_date="2024-12-31",
        file_path="btc_with_indicators.csv"
    )
    
    backfiller.set_transformer(price_transformer)
    
    print("Backfilling with transformation...")
    backfiller.run()
    print("✓ Done!")

if __name__ == "__main__":
    backfill_with_transformation()
```

---

## Backfill to Present

Use `"now"` to backfill until the current time:

```python
backfiller = sf.BinanceBackfilling(
    symbol="BTCUSDT",
    timeframe="1m",
    from_date="2024-01-01",
    to_date="now"  # Until now
)

backfiller.run()
```

This is useful for:

- Initial database population
- Catching up after downtime
- Continuous backfilling

---

## Time Periods

### Short Period (Days)

```python
# 7 days
backfiller = sf.BinanceBackfilling(
    symbol="BTCUSDT",
    timeframe="1m",
    from_date="2024-10-01",
    to_date="2024-10-07"
)
```

### Medium Period (Months)

```python
# 3 months
backfiller = sf.BinanceBackfilling(
    symbol="BTCUSDT",
    timeframe="1h",
    from_date="2024-07-01",
    to_date="2024-09-30"
)
```

### Long Period (Years)

```python
# 2 years
backfiller = sf.BinanceBackfilling(
    symbol="BTCUSDT",
    timeframe="1d",
    from_date="2023-01-01",
    to_date="2024-12-31"
)
```

!!! tip "Timeframe Choice"
    For long periods, use higher timeframes (1h, 1d) to reduce:
    
    - API calls
    - Download time
    - Storage requirements

---

## Rate Limiting

StreamForge handles rate limiting automatically:

```python
# Automatic rate limiting - no configuration needed
backfiller = sf.BinanceBackfilling(...)
backfiller.run()  # Respects exchange rate limits
```

For very large backfills, the process may take time:

| Timeframe | Period | Approximate Time |
|-----------|--------|------------------|
| 1m | 1 day | ~1 minute |
| 1m | 1 month | ~30 minutes |
| 1m | 1 year | ~6 hours |
| 1h | 1 year | ~15 minutes |
| 1d | 1 year | ~1 minute |

---

## Safe Re-Running

Backfilling is safe to re-run when using upsert:

```python
postgres = (sf.PostgresEmitter(...)
    .set_model(KlineTable)
    .on_conflict(["source", "symbol", "timeframe", "open_ts"])  # Upsert!
)

# Run once
backfiller.register_emitter(postgres)
backfiller.run()

# Run again - no duplicates, updates existing records
backfiller.run()
```

**Without upsert:**
```python
# ✗ Will create duplicates
postgres.set_model(KlineTable)  # No on_conflict()

backfiller.register_emitter(postgres)
backfiller.run()  # First run
backfiller.run()  # Second run - DUPLICATES!
```

---

## Gap Filling

Fill gaps in existing data:

```python
# You have data for Jan-Mar and Jul-Dec
# Fill the Apr-Jun gap:

backfiller = sf.BinanceBackfilling(
    symbol="BTCUSDT",
    timeframe="1h",
    from_date="2024-04-01",  # Gap start
    to_date="2024-06-30"     # Gap end
)

backfiller.register_emitter(postgres_with_upsert)
backfiller.run()
```

---

## Best Practices

### 1. Always Use Upsert for PostgreSQL

```python
# ✓ Safe to re-run
postgres.on_conflict(["source", "symbol", "timeframe", "open_ts"])

# ✗ Will create duplicates
postgres.set_model(KlineTable)  # No upsert
```

### 2. Choose Appropriate Timeframe

```python
# ✓ Good - 1h for analysis
backfiller = sf.BinanceBackfilling(
    timeframe="1h",
    from_date="2023-01-01",
    to_date="2024-12-31"
)

# ⚠️ Slower - 1m for 2 years
backfiller = sf.BinanceBackfilling(
    timeframe="1m",  # Lots of data!
    from_date="2023-01-01",
    to_date="2024-12-31"
)
```

### 3. Batch Large Backfills

For very large periods, split into chunks:

```python
import pandas as pd

# Generate date ranges
date_ranges = pd.date_range(
    start="2020-01-01",
    end="2024-12-31",
    freq="3MS"  # 3-month intervals
)

# Backfill in chunks
for i in range(len(date_ranges) - 1):
    from_date = date_ranges[i].strftime("%Y-%m-%d")
    to_date = date_ranges[i + 1].strftime("%Y-%m-%d")
    
    print(f"Backfilling {from_date} to {to_date}...")
    
    backfiller = sf.BinanceBackfilling(
        symbol="BTCUSDT",
        timeframe="1h",
        from_date=from_date,
        to_date=to_date
    )
    
    backfiller.register_emitter(postgres)
    backfiller.run()
```

### 4. Test with Small Ranges First

```python
# ✓ Test first
backfiller = sf.BinanceBackfilling(
    symbol="BTCUSDT",
    timeframe="1h",
    from_date="2024-10-01",
    to_date="2024-10-02"  # Just 1 day
)

# Then scale up
backfiller = sf.BinanceBackfilling(
    symbol="BTCUSDT",
    timeframe="1h",
    from_date="2024-01-01",
    to_date="2024-12-31"  # Full year
)
```

---

## Common Patterns

### Pattern 1: Initial Database Population

```python
# Populate fresh database
symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]

for symbol in symbols:
    backfiller = sf.BinanceBackfilling(
        symbol=symbol,
        timeframe="1h",
        from_date="2024-01-01",
        to_date="now"
    )
    backfiller.register_emitter(postgres_with_upsert)
    backfiller.run()
```

### Pattern 2: Daily Update

```python
from datetime import datetime, timedelta

# Backfill yesterday's data
yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
today = datetime.now().strftime("%Y-%m-%d")

backfiller = sf.BinanceBackfilling(
    symbol="BTCUSDT",
    timeframe="1m",
    from_date=yesterday,
    to_date=today
)

backfiller.register_emitter(postgres_with_upsert)
backfiller.run()
```

### Pattern 3: Multi-Exchange Backfill

```python
# Backfill same symbol from multiple exchanges
symbols_by_exchange = {
    "Binance": "BTCUSDT",
    "OKX": "BTC-USDT"
}

# Binance
binance_backfiller = sf.BinanceBackfilling(
    symbol="BTCUSDT",
    timeframe="1h",
    from_date="2024-01-01",
    to_date="2024-12-31"
)
binance_backfiller.register_emitter(postgres)
binance_backfiller.run()

# OKX
okx_backfiller = sf.OkxBackfilling(
    symbol="BTC-USDT",
    timeframe="1h",
    from_date="2024-01-01",
    to_date="2024-12-31"
)
okx_backfiller.register_emitter(postgres)
okx_backfiller.run()
```

---

## Troubleshooting

### No Data Downloaded

**Problem:** Backfiller runs but no data appears.

**Solutions:**

1. Check date range is valid
2. Verify symbol format for exchange
3. Ensure exchange has data for that period

### Duplicate Data

**Problem:** Duplicate rows in database.

**Solution:** Enable upsert:

```python
postgres.on_conflict(["source", "symbol", "timeframe", "open_ts"])
```

### Slow Backfill

**Problem:** Backfill takes very long.

**Solutions:**

1. Use higher timeframe (1h instead of 1m)
2. Reduce date range
3. This is normal for large datasets

---

## Next Steps

- [Multi-Exchange →](multi-exchange.md) - Merge multiple exchanges
- [Examples →](../examples/data_emitters.md) - See backfilling examples
- [API Reference →](../api-reference/backfilling.md) - Complete API docs

