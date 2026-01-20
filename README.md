# StreamForge

[![PyPI version](https://badge.fury.io/py/streamforge.svg)](https://badge.fury.io/py/streamforge)
[![Python Support](https://img.shields.io/pypi/pyversions/streamforge.svg)](https://pypi.org/project/streamforge/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Real-time cryptocurrency and financial data ingestion made simple.**

StreamForge is a unified, async-first framework for ingesting real-time market data from cryptocurrency exchanges. Built with Python's asyncio, it offers high-performance data streaming, normalization, and multiple output formats.

---

## Features

- **Real-time WebSocket Streaming** - Live market data from multiple exchanges
- **Multi-Exchange Support** - Binance, Kraken, OKX with unified API
- **Multiple Output Formats** - CSV, PostgreSQL, Kafka, or custom emitters
- **Timeframe Aggregation** - Automatic aggregation to higher timeframes
- **Historical Backfilling** - Load months of historical data effortlessly
- **Data Transformation** - Built-in transformers for custom data processing
- **Stream Merging** - Combine multiple exchanges into unified streams
- **Type-Safe** - Full type hints and Pydantic validation

---

## Installation

```bash
pip install streamforge
```

**Requirements:** Python 3.8+

---

## Quick Start

Stream Bitcoin price data in 3 lines:

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
    
    # Create runner and add logger
    runner = sf.BinanceRunner(stream_input=stream)
    runner.register_emitter(sf.Logger(prefix="Binance"))
    
    # Start streaming!
    await runner.run()

asyncio.run(main())
```

**Output:**
```
[Binance] BTCUSDT 1m | Open: 43,250.00 | High: 43,275.00 | Low: 43,240.00 | Close: 43,260.00
```

[📖 Read the full documentation →](https://paulobueno90.github.io/streamforge/)

---

## Supported Exchanges

| Exchange | Symbol Format | Type Name | Backfilling |
|----------|---------------|-----------|-------------|
| **Binance** | `BTCUSDT` | `kline` | ✓ |
| **Kraken** | `BTC/USD` | `ohlc` | Limited |
| **OKX** | `BTC-USDT` | `candle` | ✓ |

---

## Usage Examples

### Save to CSV

```python
import asyncio
import streamforge as sf

async def main():
    runner = sf.BinanceRunner(
        stream_input=sf.DataInput(
            type="kline",
            symbols=["BTCUSDT"],
            timeframe="1m"
        )
    )
    
    csv_emitter = sf.CSVEmitter(
        source="Binance",
        symbol="BTCUSDT",
        timeframe="1m",
        file_path="btc_data.csv"
    )
    
    runner.register_emitter(csv_emitter)
    await runner.run()

asyncio.run(main())
```

### Save to PostgreSQL

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
    postgres = (sf.PostgresEmitter(
            host="localhost",
            dbname="crypto",
            user="postgres",
            password="password"
        )
        .set_model(KlineTable)
        .on_conflict(["source", "symbol", "timeframe", "open_ts"])
    )
    
    runner = sf.BinanceRunner(
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

### Multi-Timeframe Aggregation

Stream 1-minute data and automatically create 5m, 15m, and 1h candles:

```python
import asyncio
import streamforge as sf

async def main():
    runner = sf.BinanceRunner(
        stream_input=sf.DataInput(
            type="kline",
            symbols=["BTCUSDT"],
            timeframe="1m",
            aggregate_list=["5m", "15m", "1h"]  # Auto-aggregate!
        ),
        active_warmup=True  # Required for aggregation
    )
    
    runner.register_emitter(sf.Logger(prefix="Multi-TF"))
    await runner.run()

asyncio.run(main())
```

### Historical Backfilling

Load historical data:

```python
import streamforge as sf

backfiller = sf.BinanceBackfilling(
    symbol="BTCUSDT",
    timeframe="1h",
    from_date="2024-01-01",
    to_date="2024-12-31"
)

backfiller.register_emitter(postgres_emitter)
backfiller.run()  # Downloads and saves year of data
```

### Multi-Exchange Streaming

Merge data from multiple exchanges:

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
    
    async for data in merge_streams(binance, okx):
        print(f"{data.source} | {data.symbol} | ${data.close:,.2f}")

asyncio.run(main())
```

---

## Documentation

**Full documentation:** https://paulobueno90.github.io/streamforge/

- [Installation Guide](https://paulobueno90.github.io/streamforge/getting-started/installation/)
- [Quick Start Tutorial](https://paulobueno90.github.io/streamforge/getting-started/quick-start/)
- [User Guide](https://paulobueno90.github.io/streamforge/user-guide/emitters/)
- [Examples Gallery](https://paulobueno90.github.io/streamforge/examples/)
- [API Reference](https://paulobueno90.github.io/streamforge/api-reference/)
- [Exchange Guides](https://paulobueno90.github.io/streamforge/exchanges/binance/)

---

## Key Concepts

### Runners

Connect to exchanges and manage data flow:

```python
runner = sf.BinanceRunner(stream_input=stream)  # Binance
runner = sf.KrakenRunner(stream_input=stream)   # Kraken  
runner = sf.OKXRunner(stream_input=stream)      # OKX
```

### Emitters

Define where data goes:

```python
sf.Logger()              # Print to console
sf.CSVEmitter()          # Save to CSV
sf.PostgresEmitter()     # Save to PostgreSQL
sf.KafkaEmitter()        # Stream to Kafka
```

### DataInput

Configure what to stream:

```python
stream = sf.DataInput(
    type="kline",                           # Data type
    symbols=["BTCUSDT", "ETHUSDT"],        # Trading pairs
    timeframe="1m",                         # Candle interval
    aggregate_list=["5m", "15m", "1h"]     # Optional aggregation
)
```

---

## Development

### Install from Source

```bash
git clone https://github.com/paulobueno90/streamforge.git
cd streamforge
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest
```

### Code Formatting

```bash
black streamforge/
isort streamforge/
flake8 streamforge/
```

---

## Requirements

Core dependencies (installed automatically):

- `aiohttp` - Async HTTP client
- `websockets` - WebSocket client
- `sqlalchemy` - SQL ORM
- `pandas` - Data manipulation
- `pydantic` - Data validation
- `aiokafka` - Kafka client
- `asyncpg` - PostgreSQL driver
- `aiolimiter` - Rate limiting

---

## Examples

### Stream Multiple Symbols

```python
import asyncio
import streamforge as sf

async def main():
    runner = sf.BinanceRunner(
        stream_input=sf.DataInput(
            type="kline",
            symbols=["BTCUSDT", "ETHUSDT", "SOLUSDT"],
            timeframe="1m"
        )
    )
    
    runner.register_emitter(sf.Logger(prefix="Crypto"))
    await runner.run()

asyncio.run(main())
```

### Multiple Output Destinations

```python
import asyncio
import streamforge as sf

async def main():
    runner = sf.BinanceRunner(
        stream_input=sf.DataInput(
            type="kline",
            symbols=["BTCUSDT"],
            timeframe="1m"
        )
    )
    
    # Register multiple emitters - data goes to ALL
    runner.register_emitter(sf.Logger(prefix="Monitor"))
    runner.register_emitter(csv_emitter)
    runner.register_emitter(postgres_emitter)
    runner.register_emitter(kafka_emitter)
    
    await runner.run()

asyncio.run(main())
```

[See more examples →](https://paulobueno90.github.io/streamforge/examples/)

---

## Architecture

```
Exchange WebSocket → Runner → Normalizer → Processor → Aggregator → Transformer → Emitter(s)
```

1. **Runner** - Manages WebSocket connections
2. **Normalizer** - Standardizes data across exchanges
3. **Processor** - Buffers and processes data
4. **Aggregator** - Creates higher timeframe candles (optional)
5. **Transformer** - Applies custom transformations (optional)
6. **Emitter** - Outputs to your destination(s)

[Learn more about architecture →](https://paulobueno90.github.io/streamforge/getting-started/core-concepts/)

---

## Use Cases

- **Trading Bots** - Real-time market data for algorithmic trading
- **Data Analysis** - Collect data for backtesting and research
- **Price Monitoring** - Track cryptocurrency prices across exchanges
- **Arbitrage Detection** - Find price differences between exchanges
- **Market Research** - Analyze market trends and patterns
- **Portfolio Tracking** - Monitor your cryptocurrency holdings

---

## Contributing

Contributions are welcome! Please see our [Contributing Guide](https://paulobueno90.github.io/streamforge/contributing/).

### Development Setup

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/streamforge.git`
3. Install dev dependencies: `pip install -e ".[dev]"`
4. Create a branch: `git checkout -b feature/my-feature`
5. Make changes and add tests
6. Run tests: `pytest`
7. Submit a pull request

---

## Links

- **Documentation:** https://paulobueno90.github.io/streamforge/
- **PyPI:** https://pypi.org/project/streamforge/
- **GitHub:** https://github.com/paulobueno90/streamforge
- **Issues:** https://github.com/paulobueno90/streamforge/issues
- **Changelog:** [CHANGELOG.md](CHANGELOG.md)

---

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

## Author

**Paulo Bueno**  
Email: paulohmbueno@gmail.com  
GitHub: [@paulobueno90](https://github.com/paulobueno90)

---

## Acknowledgments

Built with:
- [aiohttp](https://github.com/aio-libs/aiohttp) - Async HTTP
- [websockets](https://github.com/python-websockets/websockets) - WebSocket support
- [Pydantic](https://github.com/pydantic/pydantic) - Data validation
- [SQLAlchemy](https://github.com/sqlalchemy/sqlalchemy) - Database ORM
- [Pandas](https://github.com/pandas-dev/pandas) - Data manipulation

---

**Happy Streaming!** 🚀
