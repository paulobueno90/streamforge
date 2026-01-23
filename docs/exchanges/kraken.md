# Kraken

Complete guide to using StreamForge with Kraken, a trusted US-based cryptocurrency exchange.

---

## Quick Start

```python
import asyncio
import streamforge as sf

async def main():
    runner = sf.KrakenRunner(
        stream_input=sf.DataInput(
            type="ohlc",
            symbols=["BTC/USD", "ETH/USD"],
            timeframe="1m"
        )
    )
    
    
    await runner.run()

asyncio.run(main())
```

---

## Symbol Format

Kraken uses **forward slash** (/) separator between base and quote currencies:

| Asset Pair | Kraken Symbol |
|------------|---------------|
| Bitcoin/USD | `BTC/USD` |
| Ethereum/USD | `ETH/USD` |
| Solana/USD | `SOL/USD` |
| Bitcoin/EUR | `BTC/EUR` |
| Ethereum/BTC | `ETH/BTC` |

### Common Symbols

```python
symbols = [
    "BTC/USD",    # Bitcoin/USD
    "ETH/USD",    # Ethereum/USD
    "SOL/USD",    # Solana/USD
    "ADA/USD",    # Cardano/USD
    "XRP/USD",    # Ripple/USD
    "DOT/USD",    # Polkadot/USD
    "MATIC/USD",  # Polygon/USD
    "AVAX/USD",   # Avalanche/USD
    "BTC/EUR",    # Bitcoin/EUR
    "ETH/EUR"     # Ethereum/EUR
]
```

!!! note "Symbol Variants"
    Kraken sometimes uses variants like `XBT/USD` for Bitcoin. StreamForge normalizes these automatically.

---

## Supported Timeframes

Kraken supports these timeframe intervals:

| Timeframe | Description | API Value |
|-----------|-------------|-----------|
| `1m` | 1 minute | ✓ |
| `5m` | 5 minutes | ✓ |
| `15m` | 15 minutes | ✓ |
| `30m` | 30 minutes | ✓ |
| `1h` | 1 hour | ✓ |
| `4h` | 4 hours | ✓ |
| `1d` | 1 day | ✓ |
| `1w` | 1 week | ✓ |
| `15d` | 15 days | ✓ |

### Usage

```python
# 1-minute candles
stream = sf.DataInput(type="ohlc", symbols=["BTC/USD"], timeframe="1m")

# 1-hour candles
stream = sf.DataInput(type="ohlc", symbols=["BTC/USD"], timeframe="1h")

# Daily candles
stream = sf.DataInput(type="ohlc", symbols=["BTC/USD"], timeframe="1d")
```

---

## Data Types

### OHLC (Candlestick)

Use `type="ohlc"` for candlestick data:

```python
stream = sf.DataInput(
    type="ohlc",
    symbols=["BTC/USD"],
    timeframe="1m"
)
```

**Data format:**

```python
{
    "source": "Kraken",
    "symbol": "BTC/USD",
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

async def kraken_stream():
    runner = sf.KrakenRunner(
        stream_input=sf.DataInput(
            type="ohlc",
            symbols=["BTC/USD"],
            timeframe="1m"
        )
    )
    
    
    await runner.run()

asyncio.run(kraken_stream())
```

### Multiple Symbols

```python
runner = sf.KrakenRunner(
    stream_input=sf.DataInput(
        type="ohlc",
        symbols=["BTC/USD", "ETH/USD", "SOL/USD"],  # Multiple!
        timeframe="1m"
    )
)
```

### With Aggregation

```python
runner = sf.KrakenRunner(
    stream_input=sf.DataInput(
        type="ohlc",
        symbols=["BTC/USD"],
        timeframe="1m",
        aggregate_list=["5m", "15m", "1h"]
    ),
    active_warmup=True  # Required for aggregation
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
    __tablename__ = 'kraken_klines'
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
    
    runner = sf.KrakenRunner(
        stream_input=sf.DataInput(
            type="ohlc",
            symbols=["BTC/USD", "ETH/USD"],
            timeframe="1m"
        )
    )
    
    runner.register_emitter(postgres)
    
    
    await runner.run()

asyncio.run(main())
```

### Example 2: CSV Output

```python
import asyncio
import streamforge as sf

async def kraken_to_csv():
    csv_emitter = sf.CSVEmitter(
        source="Kraken",
        symbol="BTC/USD",
        timeframe="1h",
        file_path="kraken_btc_1h.csv"
    )
    
    runner = sf.KrakenRunner(
        stream_input=sf.DataInput(
            type="ohlc",
            symbols=["BTC/USD"],
            timeframe="1h"
        )
    )
    
    runner.register_emitter(csv_emitter)
    
    
    await runner.run()

asyncio.run(kraken_to_csv())
```

---

## Kraken-Specific Notes

### Symbol Naming

Kraken uses some unique symbol names:

| Common Name | Kraken Symbol |
|-------------|---------------|
| Bitcoin | `BTC/USD` or `XBT/USD` |
| Ethereum | `ETH/USD` |
| USDT | `USDT/USD` |

StreamForge handles these variations automatically.

### Timeframe Differences

Kraken's timeframe options differ from other exchanges:

- ✓ Has: `15d` (15 days)
- ✗ Doesn't have: `3m`, `2h`, `6h`, `8h`, `12h`, `3d`

### Update Frequency

Kraken WebSocket updates:

- **1m timeframe:** Updates approximately every second during active trading
- **Higher timeframes:** Less frequent updates

---

## Rate Limits

### WebSocket Limits

- **Connections:** Reasonable limits (not publicly specified)
- **Subscriptions:** Multiple subscriptions per connection
- **Messages:** No explicit rate limit

StreamForge manages connections automatically.

---

## Best Practices

### 1. Use Correct Symbol Format

```python
# ✓ Correct - forward slash
symbols = ["BTC/USD", "ETH/USD"]

# ✗ Wrong - no separator (Binance format)
symbols = ["BTCUSD", "ETHUSD"]

# ✗ Wrong - dash (OKX format)
symbols = ["BTC-USD", "ETH-USD"]
```

### 2. Choose Supported Timeframes

```python
# ✓ Supported by Kraken
timeframe = "1m"   # ✓
timeframe = "5m"   # ✓
timeframe = "1h"   # ✓
timeframe = "1d"   # ✓

# ✗ NOT supported by Kraken
timeframe = "3m"   # ✗
timeframe = "2h"   # ✗
```

### 3. Enable Warmup for Aggregation

```python
# ✓ Required for aggregation
runner = sf.KrakenRunner(
    stream_input=stream,
    active_warmup=True
)
```

---

## Comparison with Other Exchanges

| Feature | Binance | Kraken | OKX |
|---------|---------|--------|-----|
| **Symbol Format** | `BTCUSDT` | `BTC/USD` | `BTC-USDT` |
| **Type Name** | `kline` | `ohlc` | `candle` |
| **1m Timeframe** | ✓ | ✓ | ✓ |
| **3m Timeframe** | ✓ | ✗ | ✓ |
| **15d Timeframe** | ✗ | ✓ | ✗ |
| **Backfilling** | ✓ | ⚠️ Limited | ✓ |

---

## Troubleshooting

### Symbol Format Errors

**Problem:** `Invalid symbol format` error.

**Solution:** Use forward slash:

```python
# ✓ Correct
symbols = ["BTC/USD"]

# ✗ Wrong
symbols = ["BTCUSD"]
```

### Timeframe Not Supported

**Problem:** Timeframe not available.

**Solution:** Use supported timeframes:

```python
# ✓ Supported
timeframe = "1m"  # or 5m, 15m, 30m, 1h, 4h, 1d, 1w, 15d
```

### Connection Issues

**Problem:** Can't connect to Kraken WebSocket.

**Solutions:**

1. Check Kraken status page
2. Verify firewall allows WebSocket connections
3. Try different symbol

---

## Resources

- **Kraken API Documentation:** [https://docs.kraken.com/websockets/](https://docs.kraken.com/websockets/)
- **Symbol Information:** [Kraken Markets](https://www.kraken.com/prices)
- **API Status:** [Kraken Status](https://status.kraken.com/)

---

## Next Steps

- [Binance Guide →](binance.md) - Learn about Binance integration
- [OKX Guide →](okx.md) - Learn about OKX integration
- [Multi-Exchange →](../user-guide/multi-exchange.md) - Merge multiple exchanges
- [Examples →](../examples/index.md) - See more examples

