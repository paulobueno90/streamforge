# Bybit

Complete guide to using StreamForge with Bybit, a leading global cryptocurrency derivatives exchange.

---

## Quick Start

```python
import asyncio
import streamforge as sf

async def main():
    runner = sf.BybitRunner(
        stream_input=sf.DataInput(
            type="kline",
            symbols=["BTCUSDT", "ETHUSDT"],
            timeframe="1m"
        )
    )
    
    
    await runner.run()

asyncio.run(main())
```

---

## Symbol Format

Bybit uses **no separator** between base and quote currencies (same as Binance):

| Asset Pair | Bybit Symbol |
|------------|--------------|
| Bitcoin/USDT | `BTCUSDT` |
| Ethereum/USDT | `ETHUSDT` |
| Solana/USDT | `SOLUSDT` |
| Bitcoin/USDC | `BTCUSDC` |
| Ethereum/BTC | `ETHBTC` |

### Common Symbols

```python
symbols = [
    "BTCUSDT",    # Bitcoin
    "ETHUSDT",    # Ethereum
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

## Market Types

Bybit supports three market types, all using the same API endpoint:

### Spot
Regular spot trading with immediate settlement.

```python
runner = sf.BybitRunner(
    stream_input=sf.DataInput(
        type="kline",
        symbols=["BTCUSDT"],
        timeframe="1m"
    ),
    market_type="SPOT"  # Default
)
```

### Linear (USDT/USDC Perpetual Futures)
Perpetual futures contracts settled in USDT or USDC.

```python
runner = sf.BybitRunner(
    stream_input=sf.DataInput(
        type="kline",
        symbols=["BTCUSDT"],  # Same symbol format
        timeframe="1m"
    ),
    market_type="LINEAR"  # USDT/USDC perpetuals
)
```

### Inverse (Coin-Margined Futures)
Perpetual futures contracts settled in the base currency (e.g., BTC).

```python
runner = sf.BybitRunner(
    stream_input=sf.DataInput(
        type="kline",
        symbols=["BTCUSD"],  # Note: USD for inverse
        timeframe="1m"
    ),
    market_type="INVERSE"  # Coin-margined futures
)
```

**Note:** All market types share the same rate limit pool since they use the same API endpoint.

---

## Supported Timeframes

StreamForge supports these timeframe intervals for Bybit:

| Timeframe | Description | API Value |
|-----------|-------------|-----------|
| `1m` | 1 minute | ✓ |
| `5m` | 5 minutes | ✓ |
| `15m` | 15 minutes | ✓ |
| `30m` | 30 minutes | ✓ |
| `1h` | 1 hour | ✓ |
| `2h` | 2 hours | ✓ |
| `4h` | 4 hours | ✓ |
| `1d` | 1 day | ✓ |
| `1w` | 1 week | ✓ |
| `1M` | 1 month | ✓ |

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
    "source": "bybit",
    "symbol": "BTCUSDT",
    "timeframe": "1m",
    "open_ts": 1735689600,      
    "end_ts": 1735689659,
    "open": 43250.00,
    "high": 43275.00,
    "low": 43240.00,
    "close": 43260.00,
    "volume": 12.45,
    "quote_volume": 538125.00
}
```

---

## Real-Time Streaming

### Basic Streaming

```python
import asyncio
import streamforge as sf

async def bybit_stream():
    runner = sf.BybitRunner(
        stream_input=sf.DataInput(
            type="kline",
            symbols=["BTCUSDT"],
            timeframe="1m"
        )
    )
    
    
    await runner.run()

asyncio.run(bybit_stream())
```

### Multiple Symbols

```python
runner = sf.BybitRunner(
    stream_input=sf.DataInput(
        type="kline",
        symbols=["BTCUSDT", "ETHUSDT", "SOLUSDT"],  # Multiple!
        timeframe="1m"
    )
)
```

### With Aggregation

```python
runner = sf.BybitRunner(
    stream_input=sf.DataInput(
        type="kline",
        symbols=["BTCUSDT", "ETHUSDT", "SOLUSDT"],
        timeframe="1m",
        aggregate_list=["5m", "15m", "1h"]
    ),
    active_warmup=True  # Required for aggregation
)
```

### Market Type Examples

```python
# Spot market
spot_runner = sf.BybitRunner(
    stream_input=sf.DataInput(
        type="kline",
        symbols=["BTCUSDT"],
        timeframe="1m"
    ),
    market_type="SPOT"
)

# Linear futures (USDT/USDC perpetuals)
linear_runner = sf.BybitRunner(
    stream_input=sf.DataInput(
        type="kline",
        symbols=["BTCUSDT"],
        timeframe="1m"
    ),
    market_type="LINEAR"
)

# Inverse futures (coin-margined)
inverse_runner = sf.BybitRunner(
    stream_input=sf.DataInput(
        type="kline",
        symbols=["BTCUSD"],  # Note: USD for inverse
        timeframe="1m"
    ),
    market_type="INVERSE"
)
```

---

## Historical Backfilling

### Basic Backfill

```python
import streamforge as sf

backfiller = sf.BybitBackfilling(
    symbol="BTCUSDT",
    timeframe="1h",
    from_date="2024-01-01",
    to_date="2024-12-31"
)

backfiller.run()  # Saves to CSV by default
```

### Backfill with Market Type

```python
# Spot backfilling
spot_backfiller = sf.BybitBackfilling(
    symbol="BTCUSDT",
    timeframe="1h",
    from_date="2024-01-01",
    to_date="2024-12-31",
    market_type="SPOT"  # Default
)

# Linear futures backfilling
linear_backfiller = sf.BybitBackfilling(
    symbol="BTCUSDT",
    timeframe="1h",
    from_date="2024-01-01",
    to_date="2024-12-31",
    market_type="LINEAR"
)

# Inverse futures backfilling
inverse_backfiller = sf.BybitBackfilling(
    symbol="BTCUSD",  # Note: USD for inverse
    timeframe="1h",
    from_date="2024-01-01",
    to_date="2024-12-31",
    market_type="INVERSE"
)
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

backfiller = sf.BybitBackfilling(
    symbol="BTCUSDT",
    timeframe="1h",
    from_date="2024-01-01",
    to_date="2024-12-31",
    market_type="SPOT"
)

backfiller.register_emitter(postgres)
backfiller.run()
```

### Date Ranges

```python
# Specific period
backfiller = sf.BybitBackfilling(
    symbol="BTCUSDT",
    timeframe="1h",
    from_date="2024-01-01",
    to_date="2024-01-31"
)

# Until present
backfiller = sf.BybitBackfilling(
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
    __tablename__ = 'bybit_klines'
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
    
    runner = sf.BybitRunner(
        stream_input=sf.DataInput(
            type="kline",
            symbols=["BTCUSDT", "ETHUSDT"],
            timeframe="1m"
        )
    )
    
    runner.register_emitter(postgres)
    
    
    await runner.run()

asyncio.run(main())
```

### Example 2: Multi-Market Type Streaming

```python
import asyncio
import streamforge as sf

async def stream_all_markets():
    # Spot market
    spot_runner = sf.BybitRunner(
        stream_input=sf.DataInput(
            type="kline",
            symbols=["BTCUSDT"],
            timeframe="1m"
        ),
        market_type="SPOT"
    )
    
    # Linear futures
    linear_runner = sf.BybitRunner(
        stream_input=sf.DataInput(
            type="kline",
            symbols=["BTCUSDT"],
            timeframe="1m"
        ),
        market_type="LINEAR"
    )
    
    # Run both (in practice, you'd handle them separately or merge)
    await spot_runner.run()

asyncio.run(stream_all_markets())
```

---

## Rate Limits

Bybit has unified rate limits across all market types (spot, linear, inverse) since they share the same API endpoint:

### API Limits (Backfilling)

- **Rate limit:** 500 requests per 5 seconds (conservative limit)
- **Maximum candles per request:** 1000
- **Shared limit:** All market types share the same rate limit pool

StreamForge implements automatic rate limiting for backfilling.

### WebSocket Limits

- **Connection limit:** Multiple connections supported
- **Message rate:** No explicit limit, but don't spam
- **Subscriptions:** Multiple streams per connection

StreamForge handles these automatically.

---

## Best Practices

### 1. Use Appropriate Market Type

```python
# ✓ Spot trading
market_type="SPOT"

# ✓ USDT/USDC perpetuals
market_type="LINEAR"

# ✓ Coin-margined futures
market_type="INVERSE"
```

### 2. Enable Warmup for Aggregation

```python
# ✓ Always use warmup with aggregate_list
runner = sf.BybitRunner(
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

### 5. Understand Symbol Format for Inverse

```python
# ✓ Spot/Linear: BTCUSDT
symbol = "BTCUSDT"

# ✓ Inverse: BTCUSD (note: USD not USDT)
symbol = "BTCUSD"
```

---

## Troubleshooting

### Connection Errors

**Problem:** Can't connect to Bybit WebSocket.

**Solutions:**

1. Check internet connection
2. Verify Bybit is not experiencing downtime
3. Check firewall settings

### Symbol Not Found

**Problem:** `Symbol 'XYZ' not found` error.

**Solutions:**

1. Verify symbol format (no separator): `BTCUSDT` not `BTC-USDT`
2. For inverse, use `BTCUSD` not `BTCUSDT`
3. Check if symbol exists on Bybit for the selected market type
4. Ensure correct spelling

### No Data Streaming

**Problem:** Connected but no data appears.

**Solutions:**

1. Verify you registered an emitter
2. Check symbol is actively traded
3. Ensure timeframe is valid
4. Verify market_type matches the symbol (e.g., inverse uses BTCUSD)

### Rate Limit Errors

**Problem:** Rate limit exceeded during backfilling.

**Solutions:**

1. StreamForge handles rate limiting automatically
2. If issues persist, the limit is set conservatively at 500/5s
3. All market types share the same limit - don't run multiple backfills simultaneously

---

## Resources

- **Bybit Official Documentation:** [https://bybit-exchange.github.io/docs/](https://bybit-exchange.github.io/docs/)
- **Symbol Information:** Check [Bybit Market Page](https://www.bybit.com/trade/)
- **API Status:** [Bybit Status Page](https://status.bybit.com/)

---

## Next Steps

- [Binance Guide →](binance.md) - Learn about Binance integration
- [Kraken Guide →](kraken.md) - Learn about Kraken integration
- [OKX Guide →](okx.md) - Learn about OKX integration  
- [User Guide →](../user-guide/emitters.md) - Deep dive into emitters
- [Examples →](../examples/index.md) - See more examples

