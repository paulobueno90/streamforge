# Basic Streaming

Simple examples to get you started with StreamForge.

---

## Hello World

The simplest possible example - stream Bitcoin data and print to console:

```python
import asyncio
import streamforge as sf

async def main():
    # Configure what to stream
    stream = sf.DataInput(
        type="kline",
        symbols=["BTCUSDT"],
        timeframe="1m"
    )
    
    # Create runner
    runner = sf.BinanceRunner(stream_input=stream)
    
    # Add logger
    
    
    # Start streaming!
    await runner.run()

if __name__ == "__main__":
    asyncio.run(main())
```

**Output:**
```
2025-10-14 16:21:32 - INFO - Aggregation Deactivated
2025-10-14 16:21:33 - INFO - Binance    | Subscribed Successful to params: {'method': 'SUBSCRIBE', 'params': ['btcusdt@kline_1m'], 'id': 999} | Websocket Input: DataInput(type='kline', symbols=['BTCUSDT'], timeframe='1m', aggregate_list=[]).
2025-10-14 16:21:33 - INFO - Binance    | Websocket Connection established successfully!
2025-10-14 16:22:00 - INFO - Binance    | Data Received: source='binance' symbol='BTCUSDT' timeframe='1m' open_ts=1760469660 end_ts=1760469719 open=113329.98 high=113411.45 low=113329.98 close=113383.03 volume=11.95122 quote_volume=1355147.9103971 vwap=None n_trades=5228 is_closed=True
2025-10-14 16:22:00 - INFO - Logger-Binance | Received Data | source='binance' symbol='BTCUSDT' timeframe='1m' open_ts=1760469660 end_ts=1760469719 open=113329.98 high=113411.45 low=113329.98 close=113383.03 volume=11.95122 quote_volume=1355147.9103971 vwap=None n_trades=5228 is_closed=True
```

---

## CSV Output

Save streaming data to CSV file:

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
    
    # Add CSV emitter
    csv_emitter = sf.CSVEmitter(
        source="Binance",
        symbol="BTCUSDT",
        timeframe="1m",
        file_path="btc_data.csv"
    )
    
    runner.register_emitter(csv_emitter)
    
    
    await runner.run()

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Multiple Symbols

Stream multiple cryptocurrencies at once:

```python
import asyncio
import streamforge as sf

async def main():
    stream = sf.DataInput(
        type="kline",
        symbols=["BTCUSDT", "ETHUSDT", "SOLUSDT"],  # 3 symbols!
        timeframe="1m"
    )
    
    runner = sf.BinanceRunner(stream_input=stream)
    
    
    await runner.run()

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Different Timeframes

Change the candle interval:

```python
import asyncio
import streamforge as sf

async def timeframe_example(timeframe: str):
    """Stream with custom timeframe"""
    stream = sf.DataInput(
        type="kline",
        symbols=["BTCUSDT"],
        timeframe=timeframe
    )
    
    runner = sf.BinanceRunner(stream_input=stream)
    
    
    await runner.run()

if __name__ == "__main__":
    # Try different timeframes:
    # asyncio.run(timeframe_example("1m"))   # 1-minute
    # asyncio.run(timeframe_example("5m"))   # 5-minute
    # asyncio.run(timeframe_example("1h"))   # 1-hour
    asyncio.run(timeframe_example("1d"))   # Daily
```

---

## Different Exchanges

StreamForge works with multiple exchanges:

=== "Binance"
    ```python
    import asyncio
    import streamforge as sf
    
    async def main():
        runner = sf.BinanceRunner(
            stream_input=sf.DataInput(
                type="kline",
                symbols=["BTCUSDT"],  # Binance format
                timeframe="1m"
            )
        )
        
        await runner.run()
    
    asyncio.run(main())
    ```

=== "OKX"
    ```python
    import asyncio
    import streamforge as sf
    
    async def main():
        runner = sf.OKXRunner(
            stream_input=sf.DataInput(
                type="candle",          # OKX uses "candle"
                symbols=["BTC-USDT"],   # OKX format with dash
                timeframe="1m"
            )
        )
        
        await runner.run()
    
    asyncio.run(main())
    ```

=== "Kraken"
    ```python
    import asyncio
    import streamforge as sf
    
    async def main():
        runner = sf.KrakenRunner(
            stream_input=sf.DataInput(
                type="ohlc",            # Kraken uses "ohlc"
                symbols=["BTC/USD"],    # Kraken format with slash
                timeframe="1m"
            )
        )
        
        await runner.run()
    
    asyncio.run(main())
    ```

---

## Multiple Outputs

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
    
    # Add multiple emitters - data goes to ALL
    
    runner.register_emitter(sf.CSVEmitter(
        source="Binance",
        symbol="BTCUSDT",
        timeframe="1m",
        file_path="backup.csv"
    ))
    
    # Data flows to BOTH logger AND CSV!
    await runner.run()

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Timed Run

Run for a specific duration:

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
    
    
    # Run for 60 seconds
    try:
        await asyncio.wait_for(runner.run(), timeout=60)
    except asyncio.TimeoutError:
        print("\nDone!")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Next Steps

- [Database Output →](data_emitters.md) - Save to PostgreSQL and Kafka
- [Data Transformation →](data-transformation.md) - Modify your data
- [Advanced Patterns →](advanced-patterns.md) - Complex use cases

