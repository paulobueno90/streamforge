# Aggregation

Stream one timeframe and automatically aggregate to higher timeframes. Get 1m, 5m, 15m, and 1h candles from a single 1m stream!

---

## What is Aggregation?

Aggregation creates higher timeframe candles from lower timeframe candles:

```
1-minute candles → Automatically create:
  - 5-minute candles (5× 1m)
  - 15-minute candles (15× 1m)
  - 1-hour candles (60× 1m)
  - 4-hour candles (240× 1m)
```

**Benefits:**

- Stream once, get multiple timeframes
- Accurate OHLCV aggregation
- Reduced API load
- Consistent timestamps

---

## Basic Usage

### Enable Aggregation

```python
import asyncio
import streamforge as sf

async def main():
    stream = sf.DataInput(
        type="kline",
        symbols=["BTCUSDT"],
        timeframe="1m",                      # Base timeframe
        aggregate_list=["5m", "15m", "1h"]  # Aggregate to these
    )
    
    runner = sf.BinanceRunner(
        stream_input=stream,
        active_warmup=True  # Required for aggregation!
    )
    
    
    
    await runner.run()

asyncio.run(main())
```

**Output:**
```
[Multi-TF] BTCUSDT 1m  | Close: $43,260.00
[Multi-TF] BTCUSDT 5m  | Close: $43,275.00  ← Aggregated from 5× 1m
[Multi-TF] BTCUSDT 15m | Close: $43,280.00  ← Aggregated from 15× 1m
[Multi-TF] BTCUSDT 1h  | Close: $43,290.00  ← Aggregated from 60× 1m
```

---

## How It Works

### Aggregation Rules

1. **Base timeframe** must be smaller than aggregate timeframes
2. **Warmup required** to initialize aggregators correctly
3. **OHLCV preserved** - mathematically accurate aggregation

### Valid Combinations

```python
# ✓ Valid - aggregate UP
timeframe="1m", aggregate_list=["5m", "1h"]

# ✓ Valid - any higher timeframes
timeframe="5m", aggregate_list=["15m", "1h", "4h"]

# ✗ Invalid - can't aggregate DOWN
timeframe="1h", aggregate_list=["5m"]
```

### OHLCV Aggregation

For aggregated candles:

- **Open** = First candle's open
- **High** = Highest high across all candles
- **Low** = Lowest low across all candles
- **Close** = Last candle's close
- **Volume** = Sum of all volumes

Example:
```python
# Input: 5× 1-minute candles
[
    {open: 100, high: 102, low: 99,  close: 101, volume: 10},
    {open: 101, high: 103, low: 100, close: 102, volume: 15},
    {open: 102, high: 104, low: 101, close: 103, volume: 12},
    {open: 103, high: 105, low: 102, close: 104, volume: 18},
    {open: 104, high: 106, low: 103, close: 105, volume: 14}
]

# Output: 1× 5-minute candle
{
    open: 100,        # First open
    high: 106,        # Highest high
    low: 99,          # Lowest low
    close: 105,       # Last close
    volume: 69        # Sum of volumes
}
```

---

## Warmup

Warmup loads historical data to initialize aggregators correctly.

### Why Warmup?

Without warmup, the first aggregated candle would be incomplete:

```python
# Without warmup - First 5m candle has only 2 candles (incomplete!)
Time 0:00 - Start streaming
Time 0:03 - First 1m candle arrives
Time 0:04 - Second 1m candle arrives
Time 0:05 - Emit 5m candle (only 2 candles! ❌)

# With warmup - First 5m candle has all 5 candles (complete!)
Before streaming - Load last 5 candles
Time 0:00 - Start streaming
Time 0:03 - First 1m candle arrives
Time 0:05 - Emit 5m candle (has 5 complete candles! ✓)
```

### Enable Warmup

```python
runner = sf.BinanceRunner(
    stream_input=stream,
    active_warmup=True  # Enable warmup
)
```

### Warmup Options

| Parameter | Default | Description |
|-----------|---------|-------------|
| `active_warmup` | `False` | Load historical data for context |
| `emit_warmup` | `False` | Also emit historical data |

```python
# Load history but don't emit it
runner = sf.BinanceRunner(
    stream_input=stream,
    active_warmup=True,   # Load history
    emit_warmup=False     # Don't emit it
)

# Load history AND emit it
runner = sf.BinanceRunner(
    stream_input=stream,
    active_warmup=True,   # Load history
    emit_warmup=True      # Emit it too
)
```

**When to use `emit_warmup=True`:**

- Backfilling while streaming
- Initializing a new database
- Want complete historical coverage

**When to use `emit_warmup=False`:**

- Normal operation
- Database already has history
- Only want live data

---

## Supported Timeframes

### Base Timeframes

Stream from any of these:

- `1m`, `3m`, `5m`, `15m`, `30m`
- `1h`, `2h`, `4h`, `6h`, `8h`, `12h`
- `1d`, `3d`
- `1w`, `1M`

### Common Aggregation Patterns

#### Pattern 1: Minute-Based

```python
timeframe="1m",
aggregate_list=["5m", "15m", "30m", "1h"]
```

#### Pattern 2: Hour-Based

```python
timeframe="1h",
aggregate_list=["2h", "4h", "6h", "12h", "1d"]
```

#### Pattern 3: Day-Based

```python
timeframe="1d",
aggregate_list=["3d", "1w", "1M"]
```

#### Pattern 4: All Timeframes

```python
timeframe="1m",
aggregate_list=["5m", "15m", "30m", "1h", "2h", "4h", "6h", "12h", "1d"]
```

---

## Complete Examples

### Example 1: Multi-Timeframe to CSV

Save each timeframe to separate CSV:

```python
import asyncio
import streamforge as sf

async def main():
    stream = sf.DataInput(
        type="kline",
        symbols=["BTCUSDT"],
        timeframe="1m",
        aggregate_list=["5m", "15m", "1h"]
    )
    
    runner = sf.BinanceRunner(
        stream_input=stream,
        active_warmup=True
    )
    
    # Separate CSV for each timeframe
    runner.register_emitter(sf.CSVEmitter(
        source="Binance",
        symbol="BTCUSDT",
        timeframe="1m",
        file_path="btc_1m.csv"
    ))
    
    runner.register_emitter(sf.CSVEmitter(
        source="Binance",
        symbol="BTCUSDT",
        timeframe="5m",
        file_path="btc_5m.csv"
    ))
    
    runner.register_emitter(sf.CSVEmitter(
        source="Binance",
        symbol="BTCUSDT",
        timeframe="15m",
        file_path="btc_15m.csv"
    ))
    
    runner.register_emitter(sf.CSVEmitter(
        source="Binance",
        symbol="BTCUSDT",
        timeframe="1h",
        file_path="btc_1h.csv"
    ))
    
    await runner.run()

asyncio.run(main())
```

Result: 4 CSV files, each with its timeframe!

### Example 2: Multi-Timeframe to PostgreSQL

Save all timeframes to one database table:

```python
import asyncio
import streamforge as sf
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String, Float, BigInteger

Base = declarative_base()

class KlineTable(Base):
    """All timeframes in one table"""
    __tablename__ = 'klines'
    
    source = Column(String, primary_key=True)
    symbol = Column(String, primary_key=True)
    timeframe = Column(String, primary_key=True)  # Differentiates timeframes
    open_ts = Column(BigInteger, primary_key=True)
    
    end_ts = Column(BigInteger)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Float)

async def main():
    stream = sf.DataInput(
        type="kline",
        symbols=["BTCUSDT", "ETHUSDT"],
        timeframe="1m",
        aggregate_list=["5m", "15m", "1h", "4h"]
    )
    
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
        stream_input=stream,
        active_warmup=True
    )
    
    runner.register_emitter(postgres)
    
    
    await runner.run()

asyncio.run(main())
```

Query different timeframes:

```sql
-- 1-minute candles
SELECT * FROM klines WHERE timeframe = '1m';

-- 1-hour candles
SELECT * FROM klines WHERE timeframe = '1h';

-- All timeframes for BTC
SELECT * FROM klines WHERE symbol = 'BTCUSDT' ORDER BY timeframe, open_ts;
```

### Example 3: Trading Strategy

Use multiple timeframes for analysis:

```python
import asyncio
import streamforge as sf

# Track latest prices per timeframe
latest_prices = {
    "1m": None,
    "5m": None,
    "15m": None,
    "1h": None
}

class StrategyEmitter(sf.DataEmitter):
    """Custom emitter for trading logic"""
    
    async def emit(self, data):
        # Update latest price
        latest_prices[data.timeframe] = data.close
        
        # Check if all timeframes are bullish
        if all(latest_prices.values()):
            print(f"\nMulti-Timeframe Analysis:")
            print(f"  1m:  ${latest_prices['1m']:,.2f}")
            print(f"  5m:  ${latest_prices['5m']:,.2f}")
            print(f"  15m: ${latest_prices['15m']:,.2f}")
            print(f"  1h:  ${latest_prices['1h']:,.2f}")
            
            # Check trend
            if (latest_prices["1m"] > latest_prices["5m"] > 
                latest_prices["15m"] > latest_prices["1h"]):
                print("  ⬆️  UPTREND across all timeframes!")

async def main():
    stream = sf.DataInput(
        type="kline",
        symbols=["BTCUSDT"],
        timeframe="1m",
        aggregate_list=["5m", "15m", "1h"]
    )
    
    runner = sf.BinanceRunner(
        stream_input=stream,
        active_warmup=True
    )
    
    runner.register_emitter(StrategyEmitter())
    
    await runner.run()

asyncio.run(main())
```

---

## Performance Considerations

### Memory Usage

Each aggregate timeframe maintains a buffer:

```python
# Moderate memory
aggregate_list=["5m", "15m"]

# Higher memory (more buffers)
aggregate_list=["5m", "15m", "30m", "1h", "2h", "4h", "6h", "12h", "1d"]
```

### Computation

Aggregation is lightweight:

- Simple OHLCV operations
- No heavy computation
- Minimal CPU impact

### Network Load

Aggregation reduces API calls:

```python
# Without aggregation - 4 WebSocket connections
runner_1m = BinanceRunner(timeframe="1m")
runner_5m = BinanceRunner(timeframe="5m")
runner_15m = BinanceRunner(timeframe="15m")
runner_1h = BinanceRunner(timeframe="1h")

# With aggregation - 1 WebSocket connection
runner = BinanceRunner(
    timeframe="1m",
    aggregate_list=["5m", "15m", "1h"]  # ✓ Better!
)
```

---

## Common Patterns

### Pattern 1: Full Spectrum

All major timeframes:

```python
stream = sf.DataInput(
    type="kline",
    symbols=["BTCUSDT"],
    timeframe="1m",
    aggregate_list=["5m", "15m", "30m", "1h", "4h", "1d"]
)
```

### Pattern 2: Trader's Set

Common trading timeframes:

```python
stream = sf.DataInput(
    type="kline",
    symbols=["BTCUSDT"],
    timeframe="1m",
    aggregate_list=["5m", "15m", "1h", "4h"]
)
```

### Pattern 3: Day Trader

Intraday timeframes only:

```python
stream = sf.DataInput(
    type="kline",
    symbols=["BTCUSDT"],
    timeframe="1m",
    aggregate_list=["5m", "15m", "30m", "1h"]
)
```

---

## Troubleshooting

### Aggregation Not Working

**Problem:** No aggregated candles emitted.

**Solution:**

```python
# ✓ Make sure warmup is enabled
runner = sf.BinanceRunner(
    stream_input=stream,
    active_warmup=True  # Required!
)
```

### Incomplete Candles

**Problem:** First aggregated candles seem wrong.

**Solution:** Warmup loads historical data. The first candles after startup are correct.

### Wrong Timestamps

**Problem:** Aggregated timestamps don't align.

**Solution:** StreamForge automatically aligns timestamps to timeframe boundaries. This is expected behavior.

---

## Best Practices

### 1. Always Use Warmup

```python
# ✓ Always enable for aggregation
runner = sf.BinanceRunner(
    stream_input=stream,
    active_warmup=True
)
```

### 2. Choose Appropriate Base Timeframe

```python
# ✓ Good - 1m base for intraday
timeframe="1m", aggregate_list=["5m", "15m", "1h"]

# ✓ Good - 1h base for swing trading
timeframe="1h", aggregate_list=["4h", "1d"]

# ⚠️ Wasteful - 1m base for daily only
timeframe="1m", aggregate_list=["1d"]  # Better to stream "1d" directly
```

### 3. Don't Over-Aggregate

```python
# ⚠️ Too many timeframes
aggregate_list=["3m", "5m", "7m", "10m", "12m", "15m", ...]  # Overkill

# ✓ Reasonable
aggregate_list=["5m", "15m", "1h", "4h"]
```

---

## Next Steps

- [Backfilling →](backfilling.md) - Load historical data
- [Multi-Exchange →](multi-exchange.md) - Merge multiple exchanges
- [Examples →](../examples/advanced-patterns.md) - See aggregation in action

