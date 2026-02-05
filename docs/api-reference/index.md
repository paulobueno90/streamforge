# API Reference

Complete API documentation for StreamForge, auto-generated from source code.

---

## Overview

StreamForge's API is organized into several key modules:

<div class="grid cards" markdown>

-   :material-play: **[Runners](runners.md)**
    
    Main entry points for streaming data

-   :material-database-export: **[Emitters](emitters.md)**
    
    Output destinations for data

-   :material-file-document: **[Data Models](data-models.md)**
    
    Data structures and schemas

-   :material-history: **[Backfilling](backfilling.md)**
    
    Historical data loading

</div>

---

## Quick Reference

### Import Statement

```python
import streamforge as sf
```

### Main Classes

| Class | Module | Purpose |
|-------|--------|---------|
| `BinanceRunner` | `streamforge` | Binance streaming |
| `KrakenRunner` | `streamforge` | Kraken streaming |
| `OKXRunner` | `streamforge` | OKX streaming |
| `DataInput` | `streamforge` | Stream configuration |
| `CSVEmitter` | `streamforge.base.emitters.csv` | CSV file output |
| `PostgresEmitter` | `streamforge` | PostgreSQL output |
| `KafkaEmitter` | `streamforge` | Kafka streaming |
| `Kline` | `streamforge` | OHLC data model |
| `BinanceBackfilling` | `streamforge` | Binance backfilling |
| `OkxBackfilling` | `streamforge` | OKX backfilling |

---

## Type Hints

StreamForge is fully type-hinted for better IDE support:

```python
from streamforge import DataInput, BinanceRunner
from streamforge.base.normalize.ohlc.models.candle import Kline

def process_kline(kline: Kline) -> None:
    price: float = kline.close
    symbol: str = kline.symbol
```

---

## Explore the API

- [Runners →](runners.md) - Exchange-specific runners
- [Emitters →](emitters.md) - Output destinations
- [Data Models →](data-models.md) - Data structures
- [Backfilling →](backfilling.md) - Historical data

---

## Source Code

Browse the source code on GitHub:

[View Source →](https://github.com/paulobueno90/streamforge)

