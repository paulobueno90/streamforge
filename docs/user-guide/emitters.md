# Emitters

Emitters define where your streaming data goes. StreamForge provides several built-in emitters, and you can create custom ones.

---

## Overview

An emitter receives normalized data and outputs it to a destination:

```python
runner = sf.BinanceRunner(stream_input=stream)
runner.register_emitter(emitter)  # Data flows to emitter
await runner.run()
```

You can register **multiple emitters** - data flows to all of them:

```python
runner.register_emitter(logger)
runner.register_emitter(csv_emitter)
runner.register_emitter(postgres_emitter)
# Data goes to all 3!
```

---

## Logger Emitter

Print data to console for debugging and development.

### Basic Usage

```python
import streamforge as sf

logger = sf.Logger(prefix="Binance")
runner.register_emitter(logger)
```

**Output:**
```
[Binance] BTCUSDT 1m | Open: $43,250.00 | High: $43,275.00 | Low: $43,240.00 | Close: $43,260.00
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `prefix` | `str` | `""` | Label for log messages |

### When to Use

✓ **Development** - See data format  
✓ **Debugging** - Verify data flow  
✓ **Monitoring** - Quick health check  

✗ **Production** - Not for long-term storage  
✗ **Analysis** - Can't query console output

### Example

```python
import asyncio
import streamforge as sf

async def main():
    stream = sf.DataInput(
        type="kline",
        symbols=["BTCUSDT", "ETHUSDT"],
        timeframe="1m"
    )
    
    runner = sf.BinanceRunner(stream_input=stream)
    runner.register_emitter(sf.Logger(prefix="💰"))
    
    await runner.run()

asyncio.run(main())
```

---

## CSV Emitter

Save data to CSV files for simple storage and analysis.

### Basic Usage

```python
import streamforge as sf

csv_emitter = sf.CSVEmitter(
    source="Binance",
    symbol="BTCUSDT",
    timeframe="1m",
    file_path="btc_data.csv"
)

runner.register_emitter(csv_emitter)
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `source` | `str` | Yes | Exchange name |
| `symbol` | `str` | Yes | Trading pair |
| `timeframe` | `str` | Yes | Candle interval |
| `file_path` | `str` | Yes | Output file path |
| `transformer_function` | `callable` | No | Data transformer |

### CSV Format

Generated CSV has these columns:

```csv
source,symbol,timeframe,open_ts,end_ts,open,high,low,close,volume
Binance,BTCUSDT,1m,1735689600000,1735689659999,43250.00,43275.00,43240.00,43260.00,12.45
```

### Append Behavior

CSVEmitter **appends** to existing files:

```python
# First run - creates file
csv = sf.CSVEmitter(..., file_path="data.csv")

# Second run - appends to data.csv
csv = sf.CSVEmitter(..., file_path="data.csv")
```

### When to Use

✓ **Backfilling** - Historical data dumps  
✓ **Simple analysis** - Pandas/Excel  
✓ **Portability** - Universal format  
✓ **Quick exports** - Fast and simple  

✗ **Real-time** - File I/O overhead  
✗ **Large datasets** - Databases better  
✗ **Querying** - No indexes

### Complete Example

```python
import asyncio
import streamforge as sf

async def main():
    stream = sf.DataInput(
        type="kline",
        symbols=["BTCUSDT"],
        timeframe="5m"
    )
    
    csv_emitter = sf.CSVEmitter(
        source="Binance",
        symbol="BTCUSDT",
        timeframe="5m",
        file_path="binance_btc_5m.csv"
    )
    
    runner = sf.BinanceRunner(stream_input=stream)
    runner.register_emitter(csv_emitter)
    runner.register_emitter(sf.Logger(prefix="CSV"))  # Also log
    
    await runner.run()

asyncio.run(main())
```

[CSV Example →](../examples/basic-streaming.md#csv-output)

---

## PostgreSQL

### PostgreSQL Emitter

Save data to PostgreSQL database for production use.

### Installation

PostgreSQL support is included:

```bash
pip install streamforge  # Includes asyncpg
```

### Basic Usage

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

# Create emitter
postgres = sf.PostgresEmitter(
    host="localhost",
    dbname="crypto",
    user="postgres",
    password="mysecretpassword"
)

# Set model
postgres.set_model(KlineTable, inplace=True)

runner.register_emitter(postgres)
```

### Connection Methods

=== "Parameters"

    ```python
    postgres = sf.PostgresEmitter(
        host="localhost",
        port=5432,
        dbname="crypto",
        user="postgres",
        password="secret"
    )
    ```

=== "URL"

    ```python
    postgres = sf.PostgresEmitter(
        url="postgresql+asyncpg://user:pass@localhost:5432/crypto"
    )
    ```

### Method Chaining

StreamForge supports fluent method chaining:

```python
emitter = (sf.PostgresEmitter(host="localhost", dbname="crypto")
    .set_model(KlineTable)
    .on_conflict(["source", "symbol", "timeframe", "open_ts"])
    .set_transformer(my_transformer)
)
```

Or step-by-step with `inplace=True`:

```python
emitter = sf.PostgresEmitter(host="localhost", dbname="crypto")
emitter.set_model(KlineTable, inplace=True)
emitter.on_conflict(["source", "symbol", "timeframe", "open_ts"], inplace=True)
```

### Upsert (ON CONFLICT)

Handle duplicate data with upsert:

```python
postgres.on_conflict(
    ["source", "symbol", "timeframe", "open_ts"],  # Primary key columns
    inplace=True
)
```

This enables `ON CONFLICT DO UPDATE`:

```sql
INSERT INTO klines VALUES (...)
ON CONFLICT (source, symbol, timeframe, open_ts)
DO UPDATE SET
    end_ts = EXCLUDED.end_ts,
    open = EXCLUDED.open,
    ...
```

**When to use:**

- Backfilling (may have duplicates)
- Re-running pipelines
- Gap filling

**When not to use:**

- Pure append-only streaming
- No possibility of duplicates

### Custom Conflict Actions

```python
# Update only specific columns
postgres.on_conflict(
    conflict_columns=["source", "symbol", "timeframe", "open_ts"],
    update_columns=["close", "volume"]  # Only update these
)

# Do nothing on conflict
postgres.on_conflict_do_nothing(
    ["source", "symbol", "timeframe", "open_ts"]
)
```

### Database Setup

Create your table:

```sql
CREATE TABLE klines (
    source VARCHAR(255) NOT NULL,
    symbol VARCHAR(255) NOT NULL,
    timeframe VARCHAR(50) NOT NULL,
    open_ts BIGINT NOT NULL,
    end_ts BIGINT,
    open FLOAT,
    high FLOAT,
    low FLOAT,
    close FLOAT,
    volume FLOAT,
    
    PRIMARY KEY (source, symbol, timeframe, open_ts)
);

CREATE INDEX idx_symbol_time ON klines(symbol, open_ts);
```

### Complete Example

```python
import asyncio
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

async def main():
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
    
    # Create stream
    stream = sf.DataInput(
        type="kline",
        symbols=["BTCUSDT", "ETHUSDT"],
        timeframe="1m"
    )
    
    # Run
    runner = sf.BinanceRunner(stream_input=stream)
    runner.register_emitter(postgres)
    runner.register_emitter(sf.Logger(prefix="DB"))
    
    await runner.run()

asyncio.run(main())
```

[PostgreSQL Examples →](../examples/data_emitters.md)

---

## Kafka Emitter

Stream data to Apache Kafka for real-time processing.

### Installation

Kafka support is included:

```bash
pip install streamforge  # Includes aiokafka
```

### Basic Usage

```python
import streamforge as sf

kafka = sf.KafkaEmitter(
    bootstrap_servers="localhost:9092",
    topic="crypto-stream"
)

runner.register_emitter(kafka)
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `bootstrap_servers` | `str` | Required | Kafka broker address |
| `topic` | `str` | Required | Topic name |
| `key` | `str` | `None` | Message key |
| `compression_type` | `str` | `None` | gzip, snappy, lz4, zstd |

### Message Format

Kafka messages are JSON:

```json
{
  "source": "Binance",
  "symbol": "BTCUSDT",
  "timeframe": "1m",
  "open_ts": 1735689600000,
  "end_ts": 1735689659999,
  "open": 43250.00,
  "high": 43275.00,
  "low": 43240.00,
  "close": 43260.00,
  "volume": 12.45
}
```

### With Compression

```python
kafka = sf.KafkaEmitter(
    bootstrap_servers="localhost:9092",
    topic="crypto-stream",
    compression_type="gzip"
)
```

### Complete Example

```python
import asyncio
import streamforge as sf

async def main():
    kafka = sf.KafkaEmitter(
        bootstrap_servers="localhost:9092",
        topic="binance-klines",
        compression_type="gzip"
    )
    
    stream = sf.DataInput(
        type="kline",
        symbols=["BTCUSDT", "ETHUSDT"],
        timeframe="1m"
    )
    
    runner = sf.BinanceRunner(stream_input=stream)
    runner.register_emitter(kafka)
    runner.register_emitter(sf.Logger(prefix="Kafka"))
    
    await runner.run()

asyncio.run(main())
```

### When to Use

✓ **Real-time pipelines** - Stream processing  
✓ **Microservices** - Event streaming  
✓ **Scalability** - Distributed consumption  
✓ **Multiple consumers** - Fan-out pattern  

✗ **Simple use cases** - CSV/DB easier  
✗ **No Kafka** - Requires infrastructure

---

## Emitter Comparison

| Feature | Logger | CSV | PostgreSQL | Kafka |
|---------|--------|-----|------------|-------|
| **Persistence** | ❌ | ✓ File | ✓ Database | ✓ Stream |
| **Queryable** | ❌ | Limited | ✓✓ | ❌ |
| **Real-time** | ✓ | ❌ | ⚠️ | ✓✓ |
| **Scalability** | N/A | ❌ | ✓ | ✓✓ |
| **Debugging** | ✓✓ | ⚠️ | ⚠️ | ❌ |
| **Production** | ❌ | ⚠️ | ✓✓ | ✓✓ |
| **Complexity** | ⭐ | ⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| **Setup** | None | None | Database | Kafka cluster |

**Legend:** ✓✓ Excellent | ✓ Good | ⚠️ Possible | ❌ Not suitable

---

## Multiple Emitters

Send data to multiple destinations simultaneously:

```python
import asyncio
import streamforge as sf

async def main():
    stream = sf.DataInput(
        type="kline",
        symbols=["BTCUSDT"],
        timeframe="1m"
    )
    
    runner = sf.BinanceRunner(stream_input=stream)
    
    # Add multiple emitters
    runner.register_emitter(sf.Logger(prefix="Monitor"))
    runner.register_emitter(sf.CSVEmitter(
        source="Binance",
        symbol="BTCUSDT",
        timeframe="1m",
        file_path="backup.csv"
    ))
    runner.register_emitter(postgres_emitter)
    runner.register_emitter(kafka_emitter)
    
    # Data flows to ALL 4 emitters!
    await runner.run()

asyncio.run(main())
```

### Use Cases

- **Logger + PostgreSQL** - Monitor while saving
- **CSV + PostgreSQL** - Backup + database
- **PostgreSQL + Kafka** - Store + stream
- **All 4** - Complete pipeline

---

## Custom Emitters

Create custom emitters by inheriting from `DataEmitter`:

```python
from streamforge.base.emitters.base import DataEmitter
from streamforge.base.normalize.ohlc.models.candle import Kline

class MyCustomEmitter(DataEmitter):
    """Custom emitter example"""
    
    async def emit(self, data: Kline):
        """Handle each data point"""
        # Your custom logic here
        print(f"Custom: {data.symbol} @ ${data.close}")
    
    async def connect(self):
        """Setup (optional)"""
        print("Connecting to custom destination...")
    
    async def close(self):
        """Cleanup (optional)"""
        print("Closing custom connection...")

# Use it
custom = MyCustomEmitter()
runner.register_emitter(custom)
```

### Advanced Custom Emitter

```python
import aiohttp
from streamforge.base.emitters.base import DataEmitter

class WebhookEmitter(DataEmitter):
    """Send data to webhook"""
    
    def __init__(self, webhook_url: str):
        self.url = webhook_url
        self.session = None
    
    async def connect(self):
        self.session = aiohttp.ClientSession()
    
    async def emit(self, data: Kline):
        payload = {
            "symbol": data.symbol,
            "price": data.close,
            "timestamp": data.open_ts
        }
        await self.session.post(self.url, json=payload)
    
    async def close(self):
        if self.session:
            await self.session.close()

# Use it
webhook = WebhookEmitter("https://api.example.com/webhook")
runner.register_emitter(webhook)
```

---

## Best Practices

### 1. Choose the Right Emitter

- **Development** → Logger
- **Simple storage** → CSV
- **Production** → PostgreSQL
- **Real-time processing** → Kafka

### 2. Use Upsert for Backfilling

```python
# Always use on_conflict when backfilling
postgres.on_conflict(primary_key_columns)
```

### 3. Monitor with Logger

```python
# Add logger alongside other emitters
runner.register_emitter(sf.Logger(prefix="Monitor"))
runner.register_emitter(postgres)
```

### 4. Batch for Performance

```python
# PostgreSQL batches automatically
# Adjust batch size if needed
postgres.batch_size = 100
```

---

## Next Steps

- [Transformers →](transformers.md) - Modify data before emitting
- [Examples →](../examples/data_emitters.md) - See emitters in action
- [API Reference →](../api-reference/emitters.md) - Complete API docs

