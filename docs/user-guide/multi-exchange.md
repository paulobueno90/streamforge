# Multi-Exchange

Stream and merge data from multiple cryptocurrency exchanges simultaneously. Perfect for price comparison, arbitrage monitoring, and unified data collection.

---

## What is Multi-Exchange?

Multi-exchange streaming allows you to:

1. **Stream from multiple exchanges** at once
2. **Merge streams** into a unified pipeline
3. **Compare prices** across exchanges
4. **Detect arbitrage** opportunities
5. **Store in unified database** with exchange labels

---

## Merge Streams

### Basic Merging

```python
import asyncio
import streamforge as sf
from streamforge.merge_stream import merge_streams

async def main():
    # Create runners for different exchanges
    binance_runner = sf.BinanceRunner(
        stream_input=sf.DataInput(
            type="kline",
            symbols=["BTCUSDT"],
            timeframe="1m"
        )
    )
    
    okx_runner = sf.OKXRunner(
        stream_input=sf.DataInput(
            type="candle",
            symbols=["BTC-USDT"],  # OKX format
            timeframe="1m"
        )
    )
    
    # Merge and process
    async for data in merge_streams(binance_runner, okx_runner):
        print(f"{data.source:8} | {data.symbol:10} | ${data.close:,.2f}")

asyncio.run(main())
```

**Output:**
```
Binance  | BTCUSDT    | $43,260.00
OKX      | BTC-USDT   | $43,255.00
Binance  | BTCUSDT    | $43,265.00
OKX      | BTC-USDT   | $43,258.00
```

### Three Exchanges

```python
async def three_exchanges():
    binance = sf.BinanceRunner(
        stream_input=sf.DataInput(
            type="kline",
            symbols=["BTCUSDT", "ETHUSDT"],
            timeframe="1m"
        )
    )
    
    okx = sf.OKXRunner(
        stream_input=sf.DataInput(
            type="candle",
            symbols=["BTC-USDT", "ETH-USDT"],
            timeframe="1m"
        )
    )
    
    kraken = sf.KrakenRunner(
        stream_input=sf.DataInput(
            type="ohlc",
            symbols=["BTC/USD", "ETH/USD"],
            timeframe="1m"
        )
    )
    
    # Merge all 3
    async for data in merge_streams(binance, okx, kraken):
        print(f"📡 {data.source:8} | {data.symbol:12} | ${data.close:,.2f}")

asyncio.run(three_exchanges())
```

---

## Symbol Format Mapping

Each exchange uses different symbol formats:

| Exchange | BTC/USD Format | ETH/USD Format |
|----------|----------------|----------------|
| Binance | `BTCUSDT` | `ETHUSDT` |
| OKX | `BTC-USDT` | `ETH-USDT` |
| Kraken | `BTC/USD` | `ETH/USD` |

When merging, StreamForge preserves the original symbol format. For comparison, normalize symbols in your code:

```python
def normalize_symbol(symbol: str, source: str) -> str:
    """Normalize symbol to common format"""
    if source == "Binance":
        return symbol  # Already normalized
    elif source == "OKX":
        return symbol.replace("-", "")  # BTC-USDT → BTCUSDT
    elif source == "Kraken":
        return symbol.replace("/", "")  # BTC/USD → BTCUSD
    return symbol

async for data in merge_streams(binance, okx, kraken):
    normalized = normalize_symbol(data.symbol, data.source)
    print(f"{data.source} {normalized}: ${data.close:,.2f}")
```

---

## Unified Database

Store data from all exchanges in one table:

```python
import asyncio
import streamforge as sf
from streamforge.merge_stream import merge_streams
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String, Float, BigInteger

Base = declarative_base()

class UnifiedKlineTable(Base):
    """One table for all exchanges"""
    __tablename__ = 'unified_klines'
    
    source = Column(String, primary_key=True)      # Exchange name
    symbol = Column(String, primary_key=True)
    timeframe = Column(String, primary_key=True)
    open_ts = Column(BigInteger, primary_key=True)
    
    end_ts = Column(BigInteger)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Float)

async def unified_database():
    # Create shared emitter
    postgres = (sf.PostgresEmitter(
            host="localhost",
            dbname="crypto",
            user="postgres",
            password="secret"
        )
        .set_model(UnifiedKlineTable)
        .on_conflict(["source", "symbol", "timeframe", "open_ts"])
    )
    
    await postgres.connect()
    
    # Create runners
    binance = sf.BinanceRunner(
        stream_input=sf.DataInput(
            type="kline",
            symbols=["BTCUSDT", "ETHUSDT"],
            timeframe="1m"
        )
    )
    
    okx = sf.OKXRunner(
        stream_input=sf.DataInput(
            type="candle",
            symbols=["BTC-USDT", "ETH-USDT"],
            timeframe="1m"
        )
    )
    
    # Merge and emit to shared database
    async for data in merge_streams(binance, okx):
        await postgres.emit(data)
        print(f"💾 Saved {data.source} {data.symbol}")

asyncio.run(unified_database())
```

**Query the unified table:**

```sql
-- All BTC data across exchanges
SELECT source, symbol, close, volume
FROM unified_klines
WHERE symbol LIKE '%BTC%'
ORDER BY open_ts DESC
LIMIT 10;

-- Compare prices by exchange
SELECT 
    source,
    AVG(close) as avg_price,
    MAX(close) as max_price,
    MIN(close) as min_price
FROM unified_klines
WHERE symbol LIKE '%BTC%'
  AND timeframe = '1m'
  AND open_ts > EXTRACT(EPOCH FROM NOW() - INTERVAL '1 hour') * 1000
GROUP BY source;
```

---

## Price Comparison

Track price differences in real-time:

```python
import asyncio
import streamforge as sf
from streamforge.merge_stream import merge_streams

async def price_comparison():
    # Store latest prices
    latest_prices = {}
    
    binance = sf.BinanceRunner(
        stream_input=sf.DataInput(
            type="kline",
            symbols=["BTCUSDT"],
            timeframe="1m"
        )
    )
    
    okx = sf.OKXRunner(
        stream_input=sf.DataInput(
            type="candle",
            symbols=["BTC-USDT"],
            timeframe="1m"
        )
    )
    
    async for data in merge_streams(binance, okx):
        # Update latest price
        latest_prices[data.source] = data.close
        
        # Compare when we have both
        if len(latest_prices) >= 2:
            binance_price = latest_prices.get("Binance", 0)
            okx_price = latest_prices.get("OKX", 0)
            
            if binance_price and okx_price:
                diff = binance_price - okx_price
                diff_pct = (diff / binance_price) * 100
                
                print(f"\n💰 Price Comparison:")
                print(f"   Binance: ${binance_price:,.2f}")
                print(f"   OKX:     ${okx_price:,.2f}")
                print(f"   Diff:    ${diff:+.2f} ({diff_pct:+.4f}%)")
                
                # Alert on large difference
                if abs(diff_pct) > 0.1:
                    print(f"   🚨 ARBITRAGE OPPORTUNITY!")

asyncio.run(price_comparison())
```

---

## Arbitrage Detection

Detect and alert on arbitrage opportunities:

```python
import asyncio
import streamforge as sf
from streamforge.merge_stream import merge_streams
from collections import defaultdict

class ArbitrageDetector:
    """Detect arbitrage opportunities"""
    
    def __init__(self, threshold_pct=0.1):
        self.threshold = threshold_pct
        self.prices = defaultdict(dict)  # {symbol: {exchange: price}}
    
    def update(self, data):
        """Update price and check for arbitrage"""
        # Normalize symbol for comparison
        symbol = self.normalize_symbol(data.symbol)
        
        # Update price
        self.prices[symbol][data.source] = data.close
        
        # Check arbitrage
        self.check_arbitrage(symbol)
    
    def normalize_symbol(self, symbol: str) -> str:
        """Normalize to BTC/USD format"""
        return symbol.replace("-", "/").replace("USDT", "/USDT")
    
    def check_arbitrage(self, symbol: str):
        """Check for arbitrage opportunities"""
        prices = self.prices[symbol]
        
        if len(prices) < 2:
            return
        
        # Find highest and lowest
        exchanges = list(prices.keys())
        highest_exchange = max(exchanges, key=lambda e: prices[e])
        lowest_exchange = min(exchanges, key=lambda e: prices[e])
        
        highest_price = prices[highest_exchange]
        lowest_price = prices[lowest_exchange]
        
        # Calculate difference
        diff = highest_price - lowest_price
        diff_pct = (diff / lowest_price) * 100
        
        # Alert if above threshold
        if diff_pct > self.threshold:
            print(f"\n🚨 ARBITRAGE ALERT: {symbol}")
            print(f"   Buy  @ {lowest_exchange:8}: ${lowest_price:,.2f}")
            print(f"   Sell @ {highest_exchange:8}: ${highest_price:,.2f}")
            print(f"   Profit: ${diff:,.2f} ({diff_pct:.2f}%)")

async def arbitrage_monitor():
    """Monitor for arbitrage opportunities"""
    
    detector = ArbitrageDetector(threshold_pct=0.1)
    
    binance = sf.BinanceRunner(
        stream_input=sf.DataInput(
            type="kline",
            symbols=["BTCUSDT", "ETHUSDT"],
            timeframe="1m"
        )
    )
    
    okx = sf.OKXRunner(
        stream_input=sf.DataInput(
            type="candle",
            symbols=["BTC-USDT", "ETH-USDT"],
            timeframe="1m"
        )
    )
    
    kraken = sf.KrakenRunner(
        stream_input=sf.DataInput(
            type="ohlc",
            symbols=["BTC/USD", "ETH/USD"],
            timeframe="1m"
        )
    )
    
    async for data in merge_streams(binance, okx, kraken):
        detector.update(data)

asyncio.run(arbitrage_monitor())
```

---

## Complete Examples

### Example 1: Multi-Symbol Multi-Exchange

```python
import asyncio
import streamforge as sf
from streamforge.merge_stream import merge_streams

async def multi_everything():
    """Multiple symbols from multiple exchanges"""
    
    binance = sf.BinanceRunner(
        stream_input=sf.DataInput(
            type="kline",
            symbols=["BTCUSDT", "ETHUSDT", "SOLUSDT"],
            timeframe="1m"
        )
    )
    
    okx = sf.OKXRunner(
        stream_input=sf.DataInput(
            type="candle",
            symbols=["BTC-USDT", "ETH-USDT", "SOL-USDT"],
            timeframe="1m"
        )
    )
    
    print("✓ Streaming:")
    print("  - 3 symbols (BTC, ETH, SOL)")
    print("  - 2 exchanges (Binance, OKX)")
    print("  = 6 data streams merged!\n")
    
    async for data in merge_streams(binance, okx):
        print(f"📈 {data.source:8} | {data.symbol:10} | ${data.close:>10,.2f} | Vol: {data.volume:>10,.2f}")

asyncio.run(multi_everything())
```

### Example 2: CSV Per Exchange

Separate CSV files per exchange:

```python
import asyncio
import streamforge as sf
from streamforge.merge_stream import merge_streams

async def csv_per_exchange():
    """Save each exchange to separate CSV"""
    
    binance = sf.BinanceRunner(
        stream_input=sf.DataInput(
            type="kline",
            symbols=["BTCUSDT"],
            timeframe="1m"
        )
    )
    binance.register_emitter(sf.CSVEmitter(
        source="Binance",
        symbol="BTCUSDT",
        timeframe="1m",
        file_path="binance_btc.csv"
    ))
    
    okx = sf.OKXRunner(
        stream_input=sf.DataInput(
            type="candle",
            symbols=["BTC-USDT"],
            timeframe="1m"
        )
    )
    okx.register_emitter(sf.CSVEmitter(
        source="OKX",
        symbol="BTC-USDT",
        timeframe="1m",
        file_path="okx_btc.csv"
    ))
    
    async for data in merge_streams(binance, okx):
        pass  # Data automatically saved by emitters

asyncio.run(csv_per_exchange())
```

---

## Use Cases

### 1. Price Comparison

Monitor price differences for trading decisions:

```python
async for data in merge_streams(binance, okx, kraken):
    print(f"{data.source}: ${data.close:,.2f}")
```

### 2. Arbitrage Trading

Detect profitable price differences:

```python
if binance_price > okx_price + fees:
    print("Buy OKX, Sell Binance!")
```

### 3. Data Redundancy

Multiple sources for reliability:

```python
# If one exchange goes down, others continue
async for data in merge_streams(binance, okx, kraken):
    save_to_database(data)
```

### 4. Volume Analysis

Compare trading volumes across exchanges:

```python
volumes = {}
async for data in merge_streams(binance, okx):
    volumes[data.source] = volumes.get(data.source, 0) + data.volume
```

### 5. Exchange Health Monitoring

Track exchange uptime and data quality:

```python
async for data in merge_streams(*runners):
    log_exchange_activity(data.source, data.symbol)
```

---

## Performance Considerations

### Memory Usage

Each runner maintains its own connection and buffers:

```python
# 3 runners = 3 WebSocket connections
binance = sf.BinanceRunner(...)
okx = sf.OKXRunner(...)
kraken = sf.KrakenRunner(...)
```

### Network Load

Each exchange has its own WebSocket:

```python
# Each runner connects independently
# Total connections = number of runners
async for data in merge_streams(r1, r2, r3):  # 3 connections
    pass
```

### Data Rate

Merged stream combines data rates:

```python
# Binance: ~60 updates/min for 1m candles
# OKX: ~60 updates/min for 1m candles
# Merged: ~120 updates/min total
```

---

## Best Practices

### 1. Use Consistent Timeframes

```python
# ✓ Good - same timeframe
binance = sf.BinanceRunner(DataInput(timeframe="1m", ...))
okx = sf.OKXRunner(DataInput(timeframe="1m", ...))

# ⚠️ Mixed - harder to compare
binance = sf.BinanceRunner(DataInput(timeframe="1m", ...))
okx = sf.OKXRunner(DataInput(timeframe="5m", ...))
```

### 2. Normalize Symbols

```python
def normalize_symbol(symbol: str) -> str:
    """Convert all to common format"""
    return symbol.replace("-", "").replace("/", "")
```

### 3. Handle Exchange-Specific Features

```python
# Some exchanges may have features others don't
if data.source == "Binance":
    # Binance-specific logic
    pass
elif data.source == "OKX":
    # OKX-specific logic
    pass
```

### 4. Monitor Connection Health

```python
from collections import defaultdict
from datetime import datetime, timedelta

last_update = defaultdict(lambda: datetime.now())

async for data in merge_streams(binance, okx, kraken):
    last_update[data.source] = datetime.now()
    
    # Check for stale connections
    for exchange, last_time in last_update.items():
        if datetime.now() - last_time > timedelta(minutes=5):
            print(f"⚠️  {exchange} hasn't sent data in 5 minutes!")
```

---

## Troubleshooting

### Different Update Rates

**Problem:** Exchanges update at different rates.

**Solution:** This is normal. Exchanges have different internal mechanisms.

### Symbol Format Confusion

**Problem:** Same asset has different symbols.

**Solution:** Normalize symbols for comparison:

```python
def normalize_symbol(symbol: str) -> str:
    return symbol.replace("-", "").replace("/", "").upper()
```

### Missing Data from One Exchange

**Problem:** One exchange stops sending data.

**Solution:** Add timeout detection:

```python
from datetime import datetime, timedelta

last_seen = {}

async for data in merge_streams(binance, okx):
    last_seen[data.source] = datetime.now()
    
    # Alert if an exchange goes silent
    for exchange in ["Binance", "OKX"]:
        if exchange not in last_seen:
            continue
        if datetime.now() - last_seen[exchange] > timedelta(minutes=2):
            print(f"⚠️  {exchange} connection may be down!")
```

---

## Next Steps

- [Examples →](../examples/advanced-patterns.md) - See multi-exchange examples
- [API Reference →](../api-reference/runners.md) - Complete runner documentation
- [Exchange Guides →](../exchanges/binance.md) - Exchange-specific details

