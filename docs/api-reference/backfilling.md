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

---

[Back to API Reference →](index.md)

