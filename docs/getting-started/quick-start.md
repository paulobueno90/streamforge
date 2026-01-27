# Quick Start

Get streaming in 5 minutes! This guide walks you through your first StreamForge application.

---

## Prerequisites

Make sure you have StreamForge installed:

```bash
pip install streamforge
```

[Installation Guide →](installation.md)

---

## Your First Stream

Let's create a simple script that streams Bitcoin price data from Binance.

### Step 1: Create a Python File

Create a new file called `my_first_stream.py`:

```python
import asyncio
import streamforge as sf

async def main():
    # Configure what to stream
    stream = sf.DataInput(
        type="kline",           # Candlestick/OHLC data
        symbols=["BTCUSDT"],    # Bitcoin/USDT pair
        timeframe="1m"          # 1-minute candles
    )
    
    # Create Binance runner
    runner = sf.BinanceRunner(stream_input=stream)
    
    # Add logger to see output
    
    
    # Start streaming!
    await runner.run()

if __name__ == "__main__":
    asyncio.run(main())
```

### Step 2: Run It

```bash
python my_first_stream.py
```

### Step 3: See the Magic!

You'll see live Bitcoin data streaming to your console:

```
2025-10-14 16:21:32 - INFO - Aggregation Deactivated
2025-10-14 16:21:33 - INFO - Binance    | Subscribed Successful to params: {'method': 'SUBSCRIBE', 'params': ['btcusdt@kline_1m'], 'id': 999} | Websocket Input: DataInput(type='kline', symbols=['BTCUSDT'], timeframe='1m', aggregate_list=[]).
2025-10-14 16:21:33 - INFO - Binance    | Websocket Connection established successfully!
2025-10-14 16:22:00 - INFO - Binance    | Data Received: source='binance' symbol='BTCUSDT' timeframe='1m' open_ts=1760469660 end_ts=1760469719 open=113329.98 high=113411.45 low=113329.98 close=113383.03 volume=11.95122 quote_volume=1355147.9103971 vwap=None n_trades=5228 is_closed=True
2025-10-14 16:22:00 - INFO - Binance | Received Data | source='binance' symbol='BTCUSDT' timeframe='1m' open_ts=1760469660 end_ts=1760469719 open=113329.98 high=113411.45 low=113329.98 close=113383.03 volume=11.95122 quote_volume=1355147.9103971 vwap=None n_trades=5228 is_closed=True
...
```

Press `Ctrl+C` to stop.

!!! success "Congratulations!"
    You just streamed live cryptocurrency data! 🎉

---

## Understanding the Code

Let's break down what each part does:

### 1. DataInput - Configure What to Stream

```python
stream = sf.DataInput(
    type="kline",           # What type of data
    symbols=["BTCUSDT"],    # Which trading pairs
    timeframe="1m"          # Time interval
)
```

**DataInput** tells StreamForge:

- **type**: What kind of data (`kline`, `trade`, `depth`, etc.)
- **symbols**: Which cryptocurrencies to track
- **timeframe**: For OHLC data, the candle interval

### 2. Runner - Connect to Exchange

```python
runner = sf.BinanceRunner(stream_input=stream)
```

The **Runner** manages the WebSocket connection and data flow from the exchange.

Each exchange has its own runner:

- `BinanceRunner` - For Binance
- `KrakenRunner` - For Kraken
- `OKXRunner` - For OKX

### 3. Emitter - Output the Data

```python

```

**Emitters** determine where data goes:

- `Logger` - Print to console (debugging)
- `CSVEmitter` - Save to CSV file
- `PostgresEmitter` - Save to database
- `KafkaEmitter` - Stream to Kafka

You can register multiple emitters!

### 4. Run - Start Streaming

```python
await runner.run()
```

This starts the WebSocket connection and begins streaming data.

---

## Save to CSV

Let's modify the script to save data to a CSV file:

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

Now data is saved to `btc_data.csv`!

---

## Multiple Symbols

Stream multiple cryptocurrencies at once:

```python
stream = sf.DataInput(
    type="kline",
    symbols=["BTCUSDT", "ETHUSDT", "SOLUSDT"],  # 3 symbols!
    timeframe="1m"
)

runner = sf.BinanceRunner(stream_input=stream)
runner.register_emitter(kafka_emitter)

await runner.run()
```


---

## Multiple Emitters

Send data to multiple destinations:

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
    
    # Register multiple emitters
    
    runner.register_emitter(sf.CSVEmitter(
        source="Binance",
        symbol="BTCUSDT",
        timeframe="1m",
        file_path="btc_data.csv"
    ))
    
    # Data goes to BOTH logger AND CSV!
    await runner.run()

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Different Timeframes

Change the candle interval:

```python
# 5-minute candles
stream = sf.DataInput(type="kline", symbols=["BTCUSDT"], timeframe="5m")

# 1-hour candles
stream = sf.DataInput(type="kline", symbols=["BTCUSDT"], timeframe="1h")

# Daily candles
stream = sf.DataInput(type="kline", symbols=["BTCUSDT"], timeframe="1d")
```

Supported timeframes: `1m`, `5m`, `15m`, `30m`, `1h`, `4h`, `1d`

---

## Different Exchanges

StreamForge supports multiple exchanges with the same API:

=== "Binance"

    ```python
    import streamforge as sf
    
    runner = sf.BinanceRunner(
        stream_input=sf.DataInput(
            type="kline",
            symbols=["BTCUSDT"],  # Binance format
            timeframe="1m"
        )
    )
    ```

=== "OKX"

    ```python
    import streamforge as sf
    
    runner = sf.OKXRunner(
        stream_input=sf.DataInput(
            type="candle",  # OKX calls it "candle"
            symbols=["BTC-USDT"],  # OKX format with dash
            timeframe="1m"
        )
    )
    ```

=== "Kraken"

    ```python
    import streamforge as sf
    
    runner = sf.KrakenRunner(
        stream_input=sf.DataInput(
            type="ohlc",  # Kraken calls it "ohlc"
            symbols=["BTC/USD"],  # Kraken format with slash
            timeframe="1m"
        )
    )
    ```

!!! note "Symbol Formats"
    Each exchange uses different symbol formats:
    
    - **Binance**: `BTCUSDT`
    - **OKX**: `BTC-USDT`
    - **Kraken**: `BTC/USD`
    
    See [Exchange Guides](../exchanges/binance.md) for details.

---

## Common Patterns

### Pattern 1: Debug with Logger

Use `Logger` to see what data looks like:

```python

```

### Pattern 2: Save Everything to CSV

Simple data collection:

```python
csv = sf.CSVEmitter(
    source="Binance",
    symbol="BTCUSDT",
    timeframe="1m",
    file_path="all_data.csv"
)
runner.register_emitter(csv)
```

### Pattern 3: Logger + CSV

Debug while saving:

```python

runner.register_emitter(csv_emitter)
```

---

## Stopping Gracefully

StreamForge runs forever until interrupted. To stop:

1. **Keyboard**: Press `Ctrl+C`
2. **Programmatically**: Use `asyncio` timeout

```python
import asyncio

async def main():
    runner = sf.BinanceRunner(stream_input=stream)
    
    
    # Run for 60 seconds
    try:
        await asyncio.wait_for(runner.run(), timeout=60)
    except asyncio.TimeoutError:
        print("Done!")

asyncio.run(main())
```

---

## Troubleshooting

### Connection Errors

If you can't connect:

- Check your internet connection
- Verify the exchange is not down
- Try a different symbol

### No Data Appearing

If nothing prints:

- Make sure you registered an emitter
- Check the symbol format for your exchange
- Verify the timeframe is valid

### Import Errors

If imports fail:

```bash
pip install --upgrade streamforge
```

---

## What's Next?

Now that you've created your first stream:

<div class="grid cards" markdown>

-   :material-book-open: **[Core Concepts](core-concepts.md)**
    
    Understand how StreamForge works

-   :material-database: **[Emitters Guide](../user-guide/emitters.md)**
    
    Save to databases, Kafka, and more

-   :material-code-braces: **[Examples](../examples/index.md)**
    
    See more complete examples

-   :material-swap-horizontal: **[Exchange Guides](../exchanges/binance.md)**
    
    Learn exchange-specific details

</div>

---

## Complete Example

Here's a complete, production-ready example:

```python
"""
Production-ready StreamForge example
Streams BTC and ETH data to both console and CSV
"""

import asyncio
import streamforge as sf
from datetime import datetime

async def main():
    print(f"Starting StreamForge at {datetime.now()}")
    print("Press Ctrl+C to stop\n")
    
    # Configure stream
    stream = sf.DataInput(
        type="kline",
        symbols=["BTCUSDT", "ETHUSDT"],
        timeframe="1m"
    )
    
    # Create runner
    runner = sf.BinanceRunner(stream_input=stream)
    
    # Add emitters
    
    runner.register_emitter(sf.CSVEmitter(
        source="Binance",
        symbol="BTCUSDT",
        timeframe="1m",
        file_path="binance_data.csv"
    ))
    
    # Start streaming
    try:
        await runner.run()
    except KeyboardInterrupt:
        print("\n\nStopped by user")
    except Exception as e:
        print(f"\n\nError: {e}")

if __name__ == "__main__":
    asyncio.run(main())
```

Save and run:

```bash
python production_stream.py
```

Happy streaming! 🚀

