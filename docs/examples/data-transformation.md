# Data Transformation

Examples for modifying and enriching streaming data.

---

## Basic Transformer

### Rename Fields

Map StreamForge fields to your database schema:

```python
import asyncio
import streamforge as sf
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String, Float, BigInteger

Base = declarative_base()

class CustomTable(Base):
    __tablename__ = 'custom_klines'
    exchange = Column(String, primary_key=True)
    ticker = Column(String, primary_key=True)
    tf = Column(String, primary_key=True)
    timestamp = Column(BigInteger, primary_key=True)
    o = Column(Float)
    h = Column(Float)
    l = Column(Float)
    c = Column(Float)
    v = Column(Float)

def rename_transformer(data: dict) -> dict:
    """Map to custom schema"""
    return {
        "exchange": data["source"],
        "ticker": data["symbol"],
        "tf": data["timeframe"],
        "timestamp": data["open_ts"],
        "o": data["open"],
        "h": data["high"],
        "l": data["low"],
        "c": data["close"],
        "v": data["volume"]
    }

async def main():
    postgres = (sf.PostgresEmitter(host="localhost", dbname="crypto")
        .set_model(CustomTable)
        .set_transformer(rename_transformer)  # Apply transformer
        .on_conflict(["exchange", "ticker", "tf", "timestamp"]))
    
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

## Add Computed Fields

Calculate technical indicators:

```python
import asyncio
import streamforge as sf

def add_indicators(data: dict) -> dict:
    """Add technical indicators"""
    return {
        **data,
        "price_change": data["close"] - data["open"],
        "price_change_pct": ((data["close"] - data["open"]) / data["open"]) * 100,
        "is_bullish": data["close"] > data["open"],
        "body_size": abs(data["close"] - data["open"]),
        "price_range": data["high"] - data["low"],
    }

async def main():
    csv = sf.CSVEmitter(
        source="Binance",
        symbol="BTCUSDT",
        timeframe="1m",
        file_path="btc_with_indicators.csv",
        transformer_function=add_indicators
    )
    
    runner = sf.BinanceRunner(
        stream_input=sf.DataInput(
            type="kline",
            symbols=["BTCUSDT"],
            timeframe="1m"
        )
    )
    
    runner.register_emitter(csv)
    await runner.run()

asyncio.run(main())
```

---

## Custom Emitter

Build your own custom emitter:

```python
import asyncio
import streamforge as sf
from streamforge.base.emitters.base import DataEmitter
from streamforge.base.normalize.ohlc.models.candle import Kline

class CustomEmitter(DataEmitter):
    """Custom emitter example"""
    
    def __init__(self, threshold: float = 50000):
        self.threshold = threshold
    
    async def emit(self, data: Kline):
        """Handle each data point"""
        if data.close > self.threshold:
            print(f"🚨 ALERT: {data.symbol} above ${self.threshold:,.0f}! Current: ${data.close:,.2f}")
    
    async def connect(self):
        """Setup"""
        print(f"Custom emitter ready. Threshold: ${self.threshold:,.0f}")
    
    async def close(self):
        """Cleanup"""
        print("Custom emitter closed")

async def main():
    custom = CustomEmitter(threshold=43000)
    
    runner = sf.BinanceRunner(
        stream_input=sf.DataInput(
            type="kline",
            symbols=["BTCUSDT"],
            timeframe="1m"
        )
    )
    
    runner.register_emitter(custom)
    runner.register_emitter(sf.Logger(prefix="Monitor"))
    
    await runner.run()

asyncio.run(main())
```

---

[See more examples →](../examples/index.md)

