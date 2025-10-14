# Runners API

Auto-generated API documentation for StreamForge runners.

---

## BinanceRunner

::: streamforge.ingestion.binance.runner.BinanceRunner
    options:
      show_root_heading: true
      show_source: false
      members:
        - __init__
        - run
        - stream
        - register_emitter
        - set_stream_input

---

## KrakenRunner

::: streamforge.ingestion.kraken.runner.KrakenRunner
    options:
      show_root_heading: true
      show_source: false
      members:
        - __init__
        - run
        - stream
        - register_emitter
        - set_stream_input

---

## OKXRunner

::: streamforge.ingestion.okx.runner.OKXRunner
    options:
      show_root_heading: true
      show_source: false
      members:
        - __init__
        - run
        - stream
        - register_emitter
        - set_stream_input

---

## Common Usage

### Creating a Runner

```python
import streamforge as sf

runner = sf.BinanceRunner(
    stream_input=sf.DataInput(
        type="kline",
        symbols=["BTCUSDT"],
        timeframe="1m"
    ),
    active_warmup=False,
    emit_warmup=False
)
```

### Registering Emitters

```python
runner.register_emitter(sf.Logger())
runner.register_emitter(csv_emitter)
runner.register_emitter(postgres_emitter)
```

### Running

```python
# Continuous streaming
await runner.run()

# Manual iteration
async for data in runner.stream():
    print(data)
```

---

[Back to API Reference →](index.md)

