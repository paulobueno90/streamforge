# Database & Streaming Output

Examples for saving streaming data to databases and other persistent storage.

---

## Basic PostgreSQL

Save streaming data to PostgreSQL database:

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
    postgres = sf.PostgresEmitter(
        host="localhost",
        dbname="crypto",
        user="postgres",
        password="mysecretpassword"
    )
    postgres.set_model(KlineTable, inplace=True)
    
    runner = sf.BinanceRunner(
        stream_input=sf.DataInput(
            type="kline",
            symbols=["BTCUSDT"],
            timeframe="1m"
        )
    )
    
    runner.register_emitter(postgres)
    
    
    await runner.run()

asyncio.run(main())
```

---

## Upsert Patterns

Handle duplicate data with ON CONFLICT:

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
    # Method chaining style
    postgres = (sf.PostgresEmitter(
            host="localhost",
            dbname="crypto",
            user="postgres",
            password="secret"
        )
        .set_model(KlineTable)
        .on_conflict(["source", "symbol", "timeframe", "open_ts"])  # Upsert!
    )
    
    runner = sf.BinanceRunner(
        stream_input=sf.DataInput(
            type="kline",
            symbols=["BTCUSDT"],
            timeframe="1m"
        )
    )
    
    runner.register_emitter(postgres)
    await runner.run()

asyncio.run(main())
```

---

## Kafka

### Kafka Streaming

Stream to Apache Kafka:

```python
import asyncio
import streamforge as sf

async def main():
    kafka = sf.KafkaEmitter(
        bootstrap_servers="localhost:9092",
        topic="crypto-stream",
        compression_type="gzip"
    )
    
    runner = sf.BinanceRunner(
        stream_input=sf.DataInput(
            type="kline",
            symbols=["BTCUSDT", "ETHUSDT"],
            timeframe="1m"
        )
    )
    
    runner.register_emitter(kafka)
    
    
    await runner.run()

asyncio.run(main())
```

---

## Multiple Outputs

Save to PostgreSQL, CSV, and Kafka simultaneously:

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
    # PostgreSQL
    postgres = (sf.PostgresEmitter(host="localhost", dbname="crypto")
        .set_model(KlineTable)
        .on_conflict(["source", "symbol", "timeframe", "open_ts"]))
    
    # CSV
    csv = sf.CSVEmitter(
        source="Binance",
        symbol="BTCUSDT",
        timeframe="1m",
        file_path="backup.csv"
    )
    
    # Kafka
    kafka = sf.KafkaEmitter(
        bootstrap_servers="localhost:9092",
        topic="crypto"
    )
    
    # Stream
    runner = sf.BinanceRunner(
        stream_input=sf.DataInput(
            type="kline",
            symbols=["BTCUSDT"],
            timeframe="1m"
        )
    )
    
    # Register all 3 emitters - data flows to ALL!
    runner.register_emitter(postgres)
    runner.register_emitter(csv)
    runner.register_emitter(kafka)
    
    
    await runner.run()

asyncio.run(main())
```

---

[See more examples →](../examples/index.md)
