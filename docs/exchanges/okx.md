# OKX

Complete guide to using StreamForge with OKX, a leading global cryptocurrency exchange.

---

## Quick Start

```python
import asyncio
import streamforge as sf

async def main():
    runner = sf.OKXRunner(
        stream_input=sf.DataInput(
            type="candle",
            symbols=["BTC-USDT", "ETH-USDT"],
            timeframe="1m"
        )
    )
    
    
    await runner.run()

asyncio.run(main())
```

---

## Symbol Format

OKX uses **dash** (-) separator between base and quote currencies:

| Asset Pair | OKX Symbol |
|------------|------------|
| Bitcoin/USDT | `BTC-USDT` |
| Ethereum/USDT | `ETH-USDT` |
| Solana/USDT | `SOL-USDT` |
| Bitcoin/USDC | `BTC-USDC` |
| Ethereum/BTC | `ETH-BTC` |

### Common Symbols

```python
symbols = [
    "BTC-USDT",    # Bitcoin/USDT
    "ETH-USDT",    # Ethereum/USDT
    "SOL-USDT",    # Solana/USDT
    "ADA-USDT",    # Cardano/USDT
    "XRP-USDT",    # Ripple/USDT
    "DOT-USDT",    # Polkadot/USDT
    "MATIC-USDT",  # Polygon/USDT
    "AVAX-USDT",   # Avalanche/USDT
    "DOGE-USDT",   # Dogecoin/USDT
    "LINK-USDT"    # Chainlink/USDT
]
```

---

## Supported Timeframes

OKX supports these timeframe intervals:

| Timeframe | Description | API Value |
|-----------|-------------|-----------|
| `1m` | 1 minute | ✓ |
| `3m` | 3 minutes | ✓ |
| `5m` | 5 minutes | ✓ |
| `15m` | 15 minutes | ✓ |
| `30m` | 30 minutes | ✓ |
| `1h` | 1 hour | ✓ |
| `2h` | 2 hours | ✓ |
| `4h` | 4 hours | ✓ |
| `6h` | 6 hours | ✓ |
| `12h` | 12 hours | ✓ |
| `1d` | 1 day | ✓ |
| `1w` | 1 week | ✓ |
| `1M` | 1 month | ✓ |

### Usage

```python
# 5-minute candles
stream = sf.DataInput(type="candle", symbols=["BTC-USDT"], timeframe="5m")

# 1-hour candles
stream = sf.DataInput(type="candle", symbols=["BTC-USDT"], timeframe="1h")

# Daily candles
stream = sf.DataInput(type="candle", symbols=["BTC-USDT"], timeframe="1d")
```

---

## Data Types

### Candle/Candlestick

Use `type="candle"` for OHLC data:

```python
stream = sf.DataInput(
    type="candle",
    symbols=["BTC-USDT"],
    timeframe="1m"
)
```

**Data format:**

```python
{
    "source": "OKX",
    "symbol": "BTC-USDT",
    "timeframe": "1m",
    "open_ts": 1735689600000,      # Unix timestamp (ms)
    "end_ts": 1735689659999,       # Unix timestamp (ms)
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

async def okx_stream():
    runner = sf.OKXRunner(
        stream_input=sf.DataInput(
            type="candle",
            symbols=["BTC-USDT"],
            timeframe="1m"
        )
    )
    
    
    await runner.run()

asyncio.run(okx_stream())
```

### Multiple Symbols

```python
runner = sf.OKXRunner(
    stream_input=sf.DataInput(
        type="candle",
        symbols=["BTC-USDT", "ETH-USDT", "SOL-USDT"],  # Multiple!
        timeframe="1m"
    )
)
```

### With Aggregation

```python
runner = sf.OKXRunner(
    stream_input=sf.DataInput(
        type="candle",
        symbols=["BTC-USDT"],
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

backfiller = sf.OkxBackfilling(
    symbol="BTC-USDT",
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

backfiller = sf.OkxBackfilling(
    symbol="BTC-USDT",
    timeframe="1h",
    from_date="2024-01-01",
    to_date="2024-12-31"
)

backfiller.register_emitter(postgres)
backfiller.run()
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
    __tablename__ = 'okx_klines'
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
    
    runner = sf.OKXRunner(
        stream_input=sf.DataInput(
            type="candle",
            symbols=["BTC-USDT", "ETH-USDT"],
            timeframe="1m"
        )
    )
    
    runner.register_emitter(postgres)
    
    
    await runner.run()

asyncio.run(main())
```

### Example 2: Multi-Timeframe

```python
import asyncio
import streamforge as sf

async def multi_timeframe():
    runner = sf.OKXRunner(
        stream_input=sf.DataInput(
            type="candle",
            symbols=["BTC-USDT"],
            timeframe="1m",
            aggregate_list=["5m", "15m", "1h", "4h"]
        ),
        active_warmup=True
    )
    
    
    
    await runner.run()

asyncio.run(multi_timeframe())
```

---

## Rate Limits

OKX has WebSocket and API rate limits:

### WebSocket Limits

- **Connection limit:** Reasonable limits for personal use
- **Subscriptions:** Multiple subscriptions per connection
- **Message rate:** No explicit public limit

StreamForge handles these automatically.

### API Limits (Backfilling)

OKX implements rate limiting for API calls. StreamForge respects these limits automatically during backfilling.

---

## Best Practices

### 1. Use Correct Symbol Format

```python
# ✓ Correct - dash separator
symbols = ["BTC-USDT", "ETH-USDT"]

# ✗ Wrong - no separator (Binance format)
symbols = ["BTCUSDT", "ETHUSDT"]

# ✗ Wrong - slash (Kraken format)
symbols = ["BTC/USDT", "ETH/USDT"]
```

### 2. Enable Warmup for Aggregation

```python
# ✓ Required for aggregation
runner = sf.OKXRunner(
    stream_input=stream,
    active_warmup=True
)
```

### 3. Use Upsert for Backfilling

```python
# ✓ Safe to re-run
postgres.on_conflict(["source", "symbol", "timeframe", "open_ts"])
```

---

## Comparison with Other Exchanges

| Feature | Binance | Kraken | OKX |
|---------|---------|--------|-----|
| **Symbol Format** | `BTCUSDT` | `BTC/USD` | `BTC-USDT` |
| **Type Name** | `kline` | `ohlc` | `candle` |
| **Timeframes** | 15 options | 9 options | 13 options |
| **Backfilling** | ✓ Full | ⚠️ Limited | ✓ Full |
| **Spot Trading** | ✓ | ✓ | ✓ |
| **Derivatives** | ✓ | ✓ | ✓ |

---

## Troubleshooting

### Symbol Format Errors

**Problem:** `Invalid symbol format` error.

**Solution:** Use dash separator:

```python
# ✓ Correct
symbols = ["BTC-USDT"]

# ✗ Wrong
symbols = ["BTCUSDT"]
```

### Connection Issues

**Problem:** Can't connect to OKX WebSocket.

**Solutions:**

1. Check OKX status page
2. Verify internet connection
3. Check firewall settings

### No Data Streaming

**Problem:** Connected but no data appears.

**Solutions:**

1. Verify you registered an emitter
2. Check symbol is actively traded
3. Ensure timeframe is valid

---

## Resources

- **OKX API Documentation:** [https://www.okx.com/docs-v5/](https://www.okx.com/docs-v5/)
- **Symbol Information:** [OKX Markets](https://www.okx.com/markets/prices)
- **API Status:** Check OKX official channels

---

## Next Steps

- [Binance Guide →](binance.md) - Learn about Binance integration
- [Kraken Guide →](kraken.md) - Learn about Kraken integration
- [Multi-Exchange →](../user-guide/multi-exchange.md) - Merge multiple exchanges
- [Examples →](../examples/index.md) - See more examples

