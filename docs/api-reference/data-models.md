# Data Models API

Auto-generated API documentation for StreamForge data models.

---

## Kline

::: streamforge.base.normalize.ohlc.models.candle.Kline
    options:
      show_root_heading: true
      show_source: false

---

## DataInput

::: streamforge.base.stream_input.DataInput
    options:
      show_root_heading: true
      show_source: false

---

## Common Usage

### Kline Model

The `Kline` dataclass represents OHLC/candlestick data:

```python
from streamforge.base.normalize.ohlc.models.candle import Kline

kline = Kline(
    source="Binance",
    symbol="BTCUSDT",
    timeframe="1m",
    open_ts=1735689600000,
    end_ts=1735689659999,
    open=43250.00,
    high=43275.00,
    low=43240.00,
    close=43260.00,
    volume=12.45
)

# Access fields
print(kline.close)   # 43260.00
print(kline.symbol)  # BTCUSDT
```

### DataInput Configuration

```python
from streamforge import DataInput

# Basic
stream = DataInput(
    type="kline",
    symbols=["BTCUSDT"],
    timeframe="1m"
)

# With aggregation
stream = DataInput(
    type="kline",
    symbols=["BTCUSDT"],
    timeframe="1m",
    aggregate_list=["5m", "15m", "1h"]
)
```

---

[Back to API Reference →](index.md)

