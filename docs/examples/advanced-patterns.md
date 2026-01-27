# Advanced Patterns

Complex real-world patterns including aggregation, backfilling, and multi-exchange streaming.

---

## Multi-Timeframe Aggregation

Stream 1-minute data and automatically create 5m, 15m, and 1h candles:

```python
import asyncio
import streamforge as sf

async def main():
    runner = sf.BinanceRunner(
        stream_input=sf.DataInput(
            type="kline",
            symbols=["BTCUSDT"],
            timeframe="1m",                      # Base timeframe
            aggregate_list=["5m", "15m", "1h"]  # Auto-aggregate!
        ),
        active_warmup=True  # Required for aggregation
    )
    
    
    await runner.run()

asyncio.run(main())
```

---

## Backfilling

Load historical data into database:

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

def main():
    postgres = (sf.PostgresEmitter(host="localhost", dbname="crypto")
        .set_model(KlineTable)
        .on_conflict(["source", "symbol", "timeframe", "open_ts"]))  # Important!
    
    backfiller = sf.BinanceBackfilling(
        symbol="BTCUSDT",
        timeframe="1h",
        from_date="2024-01-01",
        to_date="2024-12-31"
    )
    
    backfiller.register_emitter(postgres)
    backfiller.run()  # Sync, not async!

if __name__ == "__main__":
    main()
```

---

## Multi-Exchange Merging

Combine streams from multiple exchanges:

```python
import asyncio
import streamforge as sf
from streamforge.merge_stream import merge_streams

async def main():
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
    
    # Merge and process
    async for data in merge_streams(binance, okx):
        print(f"{data.source:8} | {data.symbol:10} | ${data.close:,.2f}")

asyncio.run(main())
```

---

## Arbitrage Detection

Detect price differences across exchanges:

```python
import asyncio
import streamforge as sf
from streamforge.merge_stream import merge_streams

async def main():
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
        latest_prices[data.source] = data.close
        
        if len(latest_prices) >= 2:
            binance_price = latest_prices.get("Binance", 0)
            okx_price = latest_prices.get("OKX", 0)
            
            if binance_price and okx_price:
                diff = binance_price - okx_price
                diff_pct = (diff / binance_price) * 100
                
                print(f"\n💰 Binance: ${binance_price:,.2f} | OKX: ${okx_price:,.2f} | Diff: {diff_pct:+.4f}%")
                
                if abs(diff_pct) > 0.1:
                    print("   🚨 ARBITRAGE OPPORTUNITY!")

asyncio.run(main())
```

---

[See more examples →](../examples/index.md)

