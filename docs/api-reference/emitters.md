# Emitters API

Auto-generated API documentation for StreamForge emitters.

---

## Logger

::: streamforge.base.emitters.logger.logger.Logger
    options:
      show_root_heading: true
      show_source: false

---

## CSVEmitter

::: streamforge.base.emitters.csv.csv.CSVEmitter
    options:
      show_root_heading: true
      show_source: false

---

## PostgresEmitter

::: streamforge.base.emitters.postgresql.db.PostgresEmitter
    options:
      show_root_heading: true
      show_source: false
      members:
        - __init__
        - set_model
        - on_conflict
        - on_conflict_do_nothing
        - set_transformer
        - connect
        - emit
        - close

---

## KafkaEmitter

::: streamforge.base.emitters.kafka.kafka.KafkaEmitter
    options:
      show_root_heading: true
      show_source: false

---

## DataEmitter (Base Class)

::: streamforge.base.emitters.base.DataEmitter
    options:
      show_root_heading: true
      show_source: false

---

## Common Usage

### Logger

```python
logger = sf.Logger(prefix="Binance")
runner.register_emitter(logger)
```

### CSV

```python
csv = sf.CSVEmitter(
    source="Binance",
    symbol="BTCUSDT",
    timeframe="1m",
    file_path="data.csv"
)
runner.register_emitter(csv)
```

### PostgreSQL

```python
postgres = (sf.PostgresEmitter(host="localhost", dbname="crypto")
    .set_model(KlineTable)
    .on_conflict(["source", "symbol", "timeframe", "open_ts"]))
runner.register_emitter(postgres)
```

### Kafka

```python
kafka = sf.KafkaEmitter(
    bootstrap_servers="localhost:9092",
    topic="crypto"
)
runner.register_emitter(kafka)
```

---

[Back to API Reference →](index.md)

