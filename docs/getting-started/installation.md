# Installation

StreamForge can be installed via pip from PyPI. Choose the installation method that fits your needs.

---

## Production Installation

For production use, install from PyPI:

```bash
pip install streamforge
```

This installs StreamForge with all required dependencies for basic functionality.

---

## Development Installation

If you want to contribute or modify StreamForge, install in development mode:

### 1. Clone the Repository

```bash
git clone https://github.com/paulobueno90/streamforge.git
cd streamforge
```

### 2. Install in Editable Mode

```bash
pip install -e .
```

### 3. Install Development Dependencies

```bash
pip install -e ".[dev]"
```

This includes testing tools, linters, and formatters.

---

## Optional Dependencies

StreamForge has optional dependencies for specific features:

### PostgreSQL Support

Already included in the base installation:

```bash
pip install streamforge  # Includes asyncpg and sqlalchemy
```

### Kafka Support

Already included in the base installation:

```bash
pip install streamforge  # Includes aiokafka
```


## System Requirements

### Python Version

StreamForge requires **Python 3.8 or higher**:

```bash
python --version  # Should be 3.8+
```

### Operating Systems

StreamForge is tested and supported on:

- :fontawesome-brands-linux: **Linux** (Ubuntu, Debian, CentOS, etc.)
- :fontawesome-brands-apple: **macOS** (10.14+)
- :fontawesome-brands-windows: **Windows** (10, 11, Server 2016+)

---

## Dependencies

StreamForge installs the following core dependencies:

| Package | Purpose |
|---------|---------|
| `aiohttp` | Async HTTP client |
| `websockets` | WebSocket client |
| `sqlalchemy` | SQL ORM |
| `pandas` | Data manipulation |
| `pydantic` | Data validation |
| `orjson` | Fast JSON parsing |
| `aiokafka` | Kafka client |
| `asyncpg` | PostgreSQL driver |
| `aiolimiter` | Rate limiting |
| `python-dateutil` | Date parsing |
| `numpy` | Numerical operations |
| `requests` | HTTP requests |
| `ciso8601` | Fast datetime parsing |

All dependencies are installed automatically.

---

## Verification

Verify your installation:

```python
import streamforge as sf

print(f"StreamForge version: {sf.__version__}")
print(f"Author: {sf.__author__}")
```

Expected output:

```
StreamForge version: 0.1.0
Author: Paulo Bueno
```

### Test Imports

Verify all major components import correctly:

```python
import streamforge as sf

# Runners
print(sf.BinanceRunner)
print(sf.KrakenRunner)
print(sf.OKXRunner)

# Emitters
print(sf.Logger)
print(sf.PostgresEmitter)
print(sf.KafkaEmitter)

# Configuration
print(sf.DataInput)

# Backfilling
print(sf.BinanceBackfilling)
print(sf.OkxBackfilling)
```

If all imports succeed, your installation is complete!

---


## Next Steps

Now that StreamForge is installed:

1. [Quick Start →](quick-start.md) - Your first stream in 5 minutes
2. [Core Concepts →](core-concepts.md) - Understand the architecture
3. [Examples →](../examples/index.md) - See StreamForge in action

---

## Getting Help

If you encounter installation issues:

- Check [GitHub Issues](https://github.com/paulobueno90/streamforge/issues)
- Create a new issue with your:
  - Python version
  - Operating system
  - Error message
  - Installation command used

