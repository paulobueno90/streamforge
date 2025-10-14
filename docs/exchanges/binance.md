# Binance

Complete guide to using StreamForge with Binance, the world's largest cryptocurrency exchange.

---

## Quick Start

```python
import asyncio
import streamforge as sf

async def main():
    runner = sf.BinanceRunner(
        stream_input=sf.DataInput(
            type="kline",
            symbols=["BTCUSDT", "ETHUSDT"],
            timeframe="1m"
        )
    )
    
    runner.register_emitter(sf.Logger(prefix="Binance"))
    await runner.run()

asyncio.run(main())
```

---

## Symbol Format

Binance uses **no separator** between base and quote currencies:

| Asset Pair | Binance Symbol |
|------------|----------------|
| Bitcoin/USDT | `BTCUSDT` |
| Ethereum/USDT | `ETHUSDT` |
| Solana/USDT | `SOLUSDT` |
| Bitcoin/BTC | `ETHBTC` |
| BNB/USDT | `BNBUSDT` |

### Common Symbols

```python
symbols = [
    "BTCUSDT",    # Bitcoin
    "ETHUSDT",    # Ethereum
    "BNBUSDT",    # Binance Coin
    "SOLUSDT",    # Solana
    "ADAUSDT",    # Cardano
    "XRPUSDT",    # Ripple
    "DOGEUSDT",   # Dogecoin
    "DOTUSDT",    # Polkadot
    "MATICUSDT",  # Polygon
    "AVAXUSDT"    # Avalanche
]
```

---

## Supported Timeframes

StreamForge supports these timeframe intervals for Binance:

| Timeframe | Description | API Value |
|-----------|-------------|-----------|
| `1m` | 1 minute | ✓ |
| `5m` | 5 minutes | ✓ |
| `15m` | 15 minutes | ✓ |
| `30m` | 30 minutes | ✓ |
| `1h` | 1 hour | ✓ |
| `4h` | 4 hours | ✓ |
| `1d` | 1 day | ✓ |

### Usage

```python
# 5-minute candles
stream = sf.DataInput(type="kline", symbols=["BTCUSDT"], timeframe="5m")

# 1-hour candles
stream = sf.DataInput(type="kline", symbols=["BTCUSDT"], timeframe="1h")

# Daily candles
stream = sf.DataInput(type="kline", symbols=["BTCUSDT"], timeframe="1d")
```

---

## Data Types

### Kline/Candlestick

Use `type="kline"` for OHLC data:

```python
stream = sf.DataInput(
    type="kline",
    symbols=["BTCUSDT"],
    timeframe="1m"
)
```

**Data format:**

```python
{
    "source": "Binance",
    "symbol": "BTCUSDT",
    "timeframe": "1m",
    "open_ts": 1735689600,      
    "end_ts": 1735689659,
    "open": 43250.00,
    "high": 43275.00,
    "low": 43240.00,
    "close": 43260.00,
    "volume": 12.45
}
```

---

## Real-Time Streaming

### Basic Streaming

```python
import asyncio
import streamforge as sf

async def binance_stream():
    runner = sf.BinanceRunner(
        stream_input=sf.DataInput(
            type="kline",
            symbols=["BTCUSDT"],
            timeframe="1m"
        )
    )
    
    runner.register_emitter(sf.Logger(prefix="Binance"))
    await runner.run()

asyncio.run(binance_stream())
```

### Multiple Symbols

```python
runner = sf.BinanceRunner(
    stream_input=sf.DataInput(
        type="kline",
        symbols=["BTCUSDT", "ETHUSDT", "SOLUSDT"],  # Multiple!
        timeframe="1m"
    )
)
```

### With Aggregation

```python
runner = sf.BinanceRunner(
    stream_input=sf.DataInput(
        type="kline",
        symbols=["BTCUSDT","ETHUSDT", "SOLUSDT"],
        timeframe="1m",
        aggregate_list=["5m", "15m", "1h"]
    ),
    active_warmup=True  # Required for aggregation
)
```

---

## Historical Backfilling

### Basic Backfill

```python
import streamforge as sf

backfiller = sf.BinanceBackfilling(
    symbol="BTCUSDT",
    timeframe="1h",
    from_date="2024-01-01",
    to_date="2024-12-31"
)

backfiller.run()  # Saves to CSV by default
```

### Backfill to PostgreSQL

```python
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

postgres = (sf.PostgresEmitter(host="localhost", dbname="crypto")
    .set_model(KlineTable)
    .on_conflict(["source", "symbol", "timeframe", "open_ts"]))

backfiller = sf.BinanceBackfilling(
    symbol="BTCUSDT",
    timeframe="1h",
    from_date="2024-01-01",
    to_date="2024-12-31"
)

backfiller.register_emitter(postgres)
backfiller.run()
```

### Date Ranges

```python
# Specific period
backfiller = sf.BinanceBackfilling(
    symbol="BTCUSDT",
    timeframe="1h",
    from_date="2024-01-01",
    to_date="2024-01-31"
)

# Until present
backfiller = sf.BinanceBackfilling(
    symbol="BTCUSDT",
    timeframe="1h",
    from_date="2024-01-01",
    to_date="now"  # Until current time
)
```

---

## Complete Examples

### Example 1: Stream to PostgreSQL

```python
import asyncio
import streamforge as sf
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String, Float, BigInteger

Base = declarative_base()

class KlineTable(Base):
    __tablename__ = 'binance_klines'
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

async def main():
    postgres = (sf.PostgresEmitter(
            host="localhost",
            dbname="crypto",
            user="postgres",
            password="secret"
        )
        .set_model(KlineTable)
        .on_conflict(["source", "symbol", "timeframe", "open_ts"])
    )
    
    runner = sf.BinanceRunner(
        stream_input=sf.DataInput(
            type="kline",
            symbols=["BTCUSDT", "ETHUSDT"],
            timeframe="1m"
        )
    )
    
    runner.register_emitter(postgres)
    runner.register_emitter(sf.Logger(prefix="Binance→DB"))
    
    await runner.run()

asyncio.run(main())
```

### Example 2: Multi-Timeframe CSV

```python
import asyncio
import streamforge as sf

print("\n" + "="*60)
print("Example 5: Separate Files Per Timeframe")
print("="*60)

# Create emitters for each timeframe
emitters = {
    "1m": sf.CSVEmitter(
        source="Binance", symbol="BTCUSDT", timeframe="1m",
        file_path="btc_1m.csv"
    ),
    "5m": sf.CSVEmitter(
        source="Binance", symbol="BTCUSDT", timeframe="5m",
        file_path="btc_5m.csv"
    ),
    "15m": sf.CSVEmitter(
        source="Binance", symbol="BTCUSDT", timeframe="15m",
        file_path="btc_15m.csv"
    ),
    "1h": sf.CSVEmitter(
        source="Binance", symbol="BTCUSDT", timeframe="1h",
        file_path="btc_1h.csv"
    ),
}


runner = sf.BinanceRunner(
    stream_input=sf.DataInput(
        type="kline",
        symbols=["BTCUSDT"],
        timeframe="1m",
        aggregate_list=["5m", "15m", "1h"]
    ),
    active_warmup=True
)

print("✓ Creating separate files:")
print("  - btc_1m.csv")
print("  - btc_5m.csv")
print("  - btc_15m.csv")
print("  - btc_1h.csv")

# Stream and route to appropriate file
async for kline in runner.stream():
    timeframe = kline.timeframe
    if timeframe in emitters:
        await emitters[timeframe].emit(kline.model_dump())
        print(f"  Saved {timeframe} candle to btc_{timeframe}.csv")
```

---

## Rate Limits

Binance has WebSocket and API rate limits:

### WebSocket Limits

- **Connection limit:** 300 connections per 5 minutes
- **Message rate:** No explicit limit, but don't spam
- **Subscriptions:** Up to 200 streams per connection

StreamForge handles these automatically.

### API Limits (Backfilling)

- **Weight limit:** 1200 per minute
- **Order limit:** 50 orders per 10 seconds

StreamForge implements automatic rate limiting for backfilling.

---

## Best Practices

### 1. Use Appropriate Timeframes

```python
# ✓ Good for day trading
timeframe="1m"

# ✓ Good for swing trading
timeframe="1h"

# ✓ Good for long-term analysis
timeframe="1d"
```

### 2. Enable Warmup for Aggregation

```python
# ✓ Always use warmup with aggregate_list
runner = sf.BinanceRunner(
    stream_input=stream,
    active_warmup=True
)
```

### 3. Use Upsert for Backfilling

```python
# ✓ Safe to re-run
postgres.on_conflict(["source", "symbol", "timeframe", "open_ts"])
```

### 4. Monitor Multiple Symbols

```python
# ✓ Efficient - one connection
symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]

# ✗ Inefficient - multiple connections
# Don't create separate runners for each symbol
```

---

## Troubleshooting

### Connection Errors

**Problem:** Can't connect to Binance WebSocket.

**Solutions:**

1. Check internet connection
2. Verify Binance is not experiencing downtime
3. Check firewall settings

### Symbol Not Found

**Problem:** `Symbol 'XYZ' not found` error.

**Solutions:**

1. Verify symbol format (no separator): `BTCUSDT` not `BTC-USDT`
2. Check if symbol exists on Binance
3. Ensure correct spelling

### No Data Streaming

**Problem:** Connected but no data appears.

**Solutions:**

1. Verify you registered an emitter
2. Check symbol is actively traded
3. Ensure timeframe is valid

---

## Resources

- **Binance Official Documentation:** [https://binance-docs.github.io/apidocs/](https://binance-docs.github.io/apidocs/)
- **Symbol Information:** Check [Binance Market Page](https://www.binance.com/en/markets)
- **API Status:** [Binance Status Page](https://www.binance.com/en/support/announcement)

---

## Next Steps

- [Kraken Guide →](kraken.md) - Learn about Kraken integration
- [OKX Guide →](okx.md) - Learn about OKX integration  
- [User Guide →](../user-guide/emitters.md) - Deep dive into emitters
- [Examples →](../examples/index.md) - See more examples

