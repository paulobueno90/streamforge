# Backfilling API

Auto-generated API documentation for StreamForge backfilling.

---

## BinanceBackfilling

::: streamforge.ingestion.binance.backfilling.BinanceBackfilling
    options:
      show_root_heading: true
      show_source: false
      members:
        - __init__
        - run
        - register_emitter
        - set_transformer

---

## OkxBackfilling

::: streamforge.ingestion.okx.backfilling.OkxBackfilling
    options:
      show_root_heading: true
      show_source: false
      members:
        - __init__
        - run
        - register_emitter
        - set_transformer

---

## BybitBackfilling

::: streamforge.ingestion.bybit.backfilling.BybitBackfilling
    options:
      show_root_heading: true
      show_source: false
      members:
        - __init__
        - run
        - register_emitter
        - set_transformer

---

## Common Usage

### Basic Backfill

```python
from streamforge import BinanceBackfilling

backfiller = BinanceBackfilling(
    symbol="BTCUSDT",
    timeframe="1h",
    from_date="2024-01-01",
    to_date="2024-12-31"
)

backfiller.run()  # Sync method
```

### With Emitter

```python
backfiller = BinanceBackfilling(
    symbol="BTCUSDT",
    timeframe="1h",
    from_date="2024-01-01",
    to_date="2024-12-31"
)

backfiller.register_emitter(postgres_emitter)
backfiller.run()
```

### With Transformer

```python
def my_transformer(data: dict) -> dict:
    return {...data, "custom_field": value}

backfiller.set_transformer(my_transformer)
backfiller.run()
```

### Bybit with Market Type

```python
from streamforge import BybitBackfilling

# Spot market (default)
backfiller = BybitBackfilling(
    symbol="BTCUSDT",
    timeframe="1h",
    from_date="2024-01-01",
    to_date="2024-12-31",
    market_type="SPOT"
)

# Linear futures
backfiller = BybitBackfilling(
    symbol="BTCUSDT",
    timeframe="1h",
    from_date="2024-01-01",
    to_date="2024-12-31",
    market_type="LINEAR"
)

# Inverse futures
backfiller = BybitBackfilling(
    symbol="BTCUSD",  # Note: USD for inverse
    timeframe="1h",
    from_date="2024-01-01",
    to_date="2024-12-31",
    market_type="INVERSE"
)

backfiller.run()
```

---

[Back to API Reference →](index.md)

