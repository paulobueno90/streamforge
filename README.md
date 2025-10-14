# StreamForge

[![PyPI version](https://badge.fury.io/py/streamforge.svg)](https://badge.fury.io/py/streamforge)
[![Python Support](https://img.shields.io/pypi/pyversions/streamforge.svg)](https://pypi.org/project/streamforge/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A real-time cryptocurrency and financial data ingestion system supporting multiple exchanges.

StreamForge provides a unified, async-first framework for ingesting real-time market data from various cryptocurrency exchanges and financial data providers. Built with Python's asyncio, it offers high-performance data streaming, normalization, and multiple output formats.

## Features

- Real-time WebSocket data ingestion from multiple exchanges:
  - Binance
  - Kraken
  - OKX
  - Polygon (planned)
- OHLC/Kline data processing and aggregation
- Multiple output formats (CSV, PostgreSQL, Kafka)
- Configurable data normalization
- Async/await architecture for high performance

## Installation

### Local Development Installation

```bash
# Clone the repository
git clone <repository-url>
cd ws-binance

# Install in development mode
pip install -e .

# Or install with development dependencies
pip install -e ".[dev]"
```

### Production Installation

```bash
pip install streamforge
```

## Quick Start

```python
from streamforge.ingestion.binance.runner import BinanceRunner
from streamforge.base.stream_input import DataInput

# Create a data input configuration
stream_input = DataInput(
    symbol="BTCUSDT",
    type="kline",
    interval="1m"
)

# Initialize and run the Binance runner
runner = BinanceRunner()
runner.set_stream_input(stream_input)

# Run the ingestion
await runner.run()
```

## Configuration

The system supports various configuration options for:
- Exchange-specific settings
- Data processing parameters
- Output destinations
- Normalization rules

## Supported Exchanges

### Binance
- Kline/OHLC data
- Real-time WebSocket streams
- Historical data backfilling

### Kraken
- OHLC data
- WebSocket integration
- API-based data retrieval

### OKX
- Candlestick data
- Real-time streaming
- Historical data support

## Development

### Requirements

- Python 3.8+
- aiohttp
- websockets
- pandas
- sqlalchemy
- pydantic

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black streamforge/
flake8 streamforge/
```

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
