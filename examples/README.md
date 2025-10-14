# StreamForge Examples

Comprehensive examples demonstrating all features of StreamForge.

## 📁 Directory Structure

```
examples/
├── 01_basic/              # Getting started
├── 02_emitters/           # Output destinations
├── 03_transformers/       # Data transformation
├── 04_aggregation/        # Timeframe aggregation
├── 05_backfilling/        # Historical data loading
├── 06_advanced/           # Advanced patterns
├── 07_production/         # Production deployment
└── requirements.txt       # Python dependencies
```

---

## 🚀 Quick Start

### Installation

```bash
# Install StreamForge
pip install streamforge

# Or install with all dependencies for examples
pip install -r examples/requirements.txt
```

### Your First Example

```bash
cd examples/01_basic
python hello_world.py
```

---

## 📚 Examples by Category

### 01_basic/ - Getting Started

**Start here if you're new to StreamForge!**

| File | Description | Complexity |
|------|-------------|------------|
| `hello_world.py` | Simplest possible example | ⭐ |
| `stream_vs_run.py` | Understanding the two main patterns | ⭐⭐ |
| `logging_debug.py` | Using Logger emitter for debugging | ⭐ |

**Key Concepts:**
- Creating a runner
- Configuring data input
- Using the Logger emitter
- `run()` vs `stream()` methods

---

### 02_emitters/ - Output Destinations

**Learn how to save your data to different outputs.**

| File | Description | Complexity |
|------|-------------|------------|
| `csv_basic.py` | Save to CSV files | ⭐ |
| `postgres_basic.py` | Basic PostgreSQL usage | ⭐⭐ |
| `postgres_method_chaining.py` | Method chaining vs inplace | ⭐⭐ |
| `postgres_upsert_patterns.py` | ON CONFLICT DO UPDATE patterns | ⭐⭐⭐ |
| `postgres_custom_query.py` | Custom SQL queries | ⭐⭐⭐ |
| `kafka_basic.py` | Stream to Apache Kafka | ⭐⭐ |
| `kafka_custom_serializer.py` | Custom serialization | ⭐⭐⭐ |
| `multi_output_pipeline.py` | Multiple outputs simultaneously | ⭐⭐ |

**Key Concepts:**
- CSVEmitter for files
- PostgresEmitter for databases
- KafkaEmitter for real-time streams
- Multiple emitters at once
- Upsert (insert or update)
- Custom SQL queries

**Common Questions:**
- **Q:** When to use `inplace=True`?  
  **A:** Use it for step-by-step configuration or conditional logic. Otherwise, use method chaining.

- **Q:** Should I use upsert?  
  **A:** Yes, if backfilling or might have duplicates. No, if pure append-only streaming.

- **Q:** Can I output to multiple destinations?  
  **A:** Yes! Register multiple emitters and data flows to all of them.

---

### 03_transformers/ - Data Transformation

**Transform data before saving it.**

| File | Description | Complexity |
|------|-------------|------------|
| `basic_transformer.py` | Rename fields, filter, compute | ⭐⭐ |
| `advanced_transformer.py` | Stateful, metadata, indicators | ⭐⭐⭐ |

**Key Concepts:**
- Renaming columns to match your schema
- Filtering unnecessary fields
- Adding computed fields
- Stateful transformations
- Technical indicators

**Common Use Cases:**
- Database columns don't match StreamForge defaults → Use transformer
- Need to calculate additional metrics → Add computed fields
- Want to filter data → Use conditional transformer

---

### 04_aggregation/ - Timeframe Aggregation

**Automatically aggregate to higher timeframes.**

| File | Description | Complexity |
|------|-------------|------------|
| `warmup_configs.py` | Understanding warmup | ⭐⭐ |
| `multi_timeframe.py` | Multiple timeframe aggregation | ⭐⭐ |

**Key Concepts:**
- Warmup: loading historical data
- `active_warmup` vs `emit_warmup`
- Aggregating 1m → 5m, 15m, 1h, 4h, 1d
- All from a single base stream

**Common Questions:**
- **Q:** Do I need warmup?  
  **A:** Yes, if using `aggregate_list`. Otherwise, optional.

- **Q:** What's the difference between `active_warmup` and `emit_warmup`?  
  **A:** `active_warmup` loads history for context. `emit_warmup` saves that history too.

- **Q:** Can I aggregate 1h to 1m?  
  **A:** No, can only aggregate to higher timeframes (1m→5m works, 5m→1m doesn't).

---

### 05_backfilling/ - Historical Data

**Load historical data from exchanges.**

| File | Description | Complexity |
|------|-------------|------------|
| `binance_backfilling.py` | Comprehensive backfilling guide | ⭐⭐ |

**Key Concepts:**
- Loading months of historical data
- Backfilling to CSV or PostgreSQL
- Using transformers during backfill
- Safe re-running with upsert

**Common Use Cases:**
- Initial database population
- Gap filling
- Historical analysis
- Testing with real data

**Tips:**
- Always use upsert when backfilling to PostgreSQL
- Backfill can be run multiple times safely
- Use `to_date="now"` to backfill until present

---

### 06_advanced/ - Advanced Patterns

**Complex use cases and patterns.**

| File | Description | Complexity |
|------|-------------|------------|
| `merge_exchanges.py` | Combine multiple exchange streams | ⭐⭐⭐ |

**Key Concepts:**
- Merging multiple exchanges
- Price comparison
- Arbitrage detection
- Unified multi-exchange database

**Use Cases:**
- Multi-exchange price comparison
- Arbitrage monitoring
- Consolidated market data
- Cross-exchange analysis

---

### 07_production/ - Production Deployment

**Enterprise-grade production setup.**

| Files | Description | Complexity |
|-------|-------------|------------|
| `docker-compose.yml` | Full stack with Docker Compose | ⭐⭐⭐ |
| `production_runner.py` | Production-ready application | ⭐⭐⭐ |
| `Dockerfile` | Container definition | ⭐⭐ |
| `init.sql` | Database initialization | ⭐ |

**Includes:**
- PostgreSQL database
- Apache Kafka
- PgAdmin (database UI)
- Kafka UI (Kafka management)
- Graceful shutdown
- Error handling & retries
- Health checks
- Environment variables
- Logging

**Quick Start:**
```bash
cd examples/07_production
docker-compose up -d
```

**Access:**
- PgAdmin: http://localhost:5050
- Kafka UI: http://localhost:8080

---

## 🎯 Decision Guide

### "I want to..."

#### ...get started quickly
→ `01_basic/hello_world.py`

#### ...save data to CSV
→ `02_emitters/csv_basic.py`

#### ...save data to PostgreSQL
→ `02_emitters/postgres_basic.py`

#### ...stream data to Kafka
→ `02_emitters/kafka_basic.py`

#### ...understand upsert (ON CONFLICT)
→ `02_emitters/postgres_upsert_patterns.py`

#### ...rename database columns
→ `03_transformers/basic_transformer.py`

#### ...aggregate 1m to 5m, 15m, 1h
→ `04_aggregation/multi_timeframe.py`

#### ...load historical data
→ `05_backfilling/binance_backfilling.py`

#### ...compare prices across exchanges
→ `06_advanced/merge_exchanges.py`

#### ...deploy to production
→ `07_production/`

#### ...save to multiple outputs at once
→ `02_emitters/multi_output_pipeline.py`

#### ...debug my pipeline
→ `01_basic/logging_debug.py`

---

## 🔧 Common Patterns

### Pattern 1: Simple CSV Streaming
```python
import streamforge as sf

runner = sf.BinanceRunner(
    stream_input=sf.DataInput(
        type="kline",
        symbols=["BTCUSDT"],
        timeframe="1m"
    )
)

emitter = sf.CSVEmitter(
    source="Binance",
    symbol="BTCUSDT",
    timeframe="1m",
    file_path="btc.csv"
)

runner.register_emitter(emitter)
await runner.run()
```

### Pattern 2: PostgreSQL with Upsert
```python
from sqlalchemy import Column, String, Float, BigInteger
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class KlineTable(Base):
    __tablename__ = 'klines'
    source = Column(String, primary_key=True)
    symbol = Column(String, primary_key=True)
    timeframe = Column(String, primary_key=True)
    open_ts = Column(BigInteger, primary_key=True)
    # ... other columns

emitter = (sf.PostgresEmitter(
        host="localhost",
        dbname="crypto",
        user="postgres",
        password="pwd"
    )
    .set_model(KlineTable)
    .on_conflict(["source", "symbol", "timeframe", "open_ts"])
)

runner.register_emitter(emitter)
await runner.run()
```

### Pattern 3: Multi-Timeframe Aggregation
```python
runner = sf.BinanceRunner(
    stream_input=sf.DataInput(
        type="kline",
        symbols=["BTCUSDT"],
        timeframe="1m",
        aggregate_list=["5m", "15m", "1h"]  # Auto-aggregate!
    ),
    active_warmup=True  # Required for aggregation
)

await runner.run()
```

### Pattern 4: Multiple Outputs
```python
# Register multiple emitters - data goes to all!
runner.register_emitter(csv_emitter)
runner.register_emitter(postgres_emitter)
runner.register_emitter(kafka_emitter)
runner.register_emitter(logger)

await runner.run()  # Data flows to all 4 outputs
```

---

## 📖 Emitter Comparison

| Feature | CSV | PostgreSQL | Kafka | Logger |
|---------|-----|------------|-------|--------|
| Persistence | File | Database | Stream | Console |
| Query | ❌ | ✅ | ❌ | ❌ |
| Real-time | ❌ | ⚠️ | ✅ | ✅ |
| Debugging | ⚠️ | ⚠️ | ❌ | ✅ |
| Production | ⚠️ | ✅ | ✅ | ❌ |
| Complexity | ⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐ |

**Legend:**
- ✅ Excellent
- ⚠️ Possible but not ideal
- ❌ Not suitable

---

## 🐛 Troubleshooting

### Problem: PostgreSQL connection error

**Solution:**
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Or
sudo systemctl status postgresql
```

### Problem: Kafka connection error

**Solution:**
```bash
# Check Kafka is running
docker-compose ps kafka

# Check Kafka topics
docker-compose exec kafka kafka-topics.sh --list --bootstrap-server localhost:9092
```

### Problem: Aggregation not working

**Solution:**
- Make sure `active_warmup=True`
- Check that base timeframe is smaller than aggregated timeframes
- Verify aggregate_list is specified

### Problem: Duplicate data in database

**Solution:**
- Use `.on_conflict()` for upsert behavior
- This is especially important for backfilling

### Problem: Column name mismatch

**Solution:**
- Use a transformer to rename fields
- See `03_transformers/basic_transformer.py`

---

## 📊 Performance Tips

1. **Batch Operations**: Use `emit_orm_bulk()` for better performance when backfilling
2. **Indexes**: Create database indexes on frequently queried columns
3. **Connection Pooling**: SQLAlchemy handles this automatically
4. **Kafka Batching**: Kafka producer batches messages automatically
5. **Warmup**: Warmup data is loaded in bulk for efficiency

---

## 🎓 Learning Path

### Beginner (Day 1)
1. `01_basic/hello_world.py`
2. `01_basic/stream_vs_run.py`
3. `02_emitters/csv_basic.py`

### Intermediate (Week 1)
4. `02_emitters/postgres_basic.py`
5. `02_emitters/postgres_upsert_patterns.py`
6. `03_transformers/basic_transformer.py`
7. `04_aggregation/multi_timeframe.py`

### Advanced (Week 2)
8. `02_emitters/multi_output_pipeline.py`
9. `05_backfilling/binance_backfilling.py`
10. `06_advanced/merge_exchanges.py`

### Production (Week 3)
11. `07_production/` - Full stack deployment

---

## 🤝 Support

- **Documentation**: See main README.md
- **Issues**: GitHub Issues
- **Questions**: GitHub Discussions

---

## 📄 License

MIT License - See LICENSE file for details

---

**Happy Streaming! 🚀**

