# Examples Gallery

Complete, copy-paste examples for common StreamForge use cases.

---

## Quick Navigation

<div class="grid cards" markdown>

-   :material-rocket-launch: **[Basic Streaming](basic-streaming.md)**
    
    Get started with simple streaming examples

-   :material-database: **[Database/Streaming Output](data_emitters.md)**
    
    Save data to PostgreSQL, Kafka and CSV

-   :material-function: **[Data Transformation](data-transformation.md)**
    
    Transform and enrich your data

-   :material-chart-multiple: **[Advanced Patterns](advanced-patterns.md)**
    
    Aggregation, backfilling, and multi-exchange

</div>

---

## By Use Case

### I want to...

#### ...get started quickly
→ [Basic Streaming →](basic-streaming.md#hello-world)

#### ...save data to CSV
→ [CSV Example →](basic-streaming.md#csv-output)

#### ...save data to PostgreSQL
→ [PostgreSQL Example →](data_emitters.md#basic-postgresql)

#### ...stream to Kafka
→ [Database Output →](data_emitters.md#kafka)

#### ...rename database columns
→ [Data Transformation →](data-transformation.md#rename-fields)

#### ...aggregate 1m to 5m, 15m, 1h
→ [Advanced Patterns →](advanced-patterns.md#multi-timeframe-aggregation)

#### ...load historical data
→ [Advanced Patterns →](advanced-patterns.md#backfilling)

#### ...compare prices across exchanges
→ [Advanced Patterns →](advanced-patterns.md#multi-exchange-merging)

---

## By Complexity

### Beginner ⭐

Start here if you're new to StreamForge:

1. [Hello World](basic-streaming.md#hello-world) - Simplest possible example
2. [CSV Output](basic-streaming.md#csv-output) - Save to file
3. [Multiple Symbols](basic-streaming.md#multiple-symbols) - Track multiple assets

### Intermediate ⭐⭐

Once you understand the basics:

4. [PostgreSQL](data_emitters.md#basic-postgresql) - Database integration
5. [Upsert Patterns](data_emitters.md#upsert-patterns) - Handle duplicates
6. [Transformers](data-transformation.md#basic-transformer) - Modify data
7. [Aggregation](advanced-patterns.md#multi-timeframe-aggregation) - Multiple timeframes

### Advanced ⭐⭐⭐

For complex use cases:

8. [Backfilling](advanced-patterns.md#backfilling) - Historical data
9. [Multi-Exchange](advanced-patterns.md#multi-exchange-merging) - Merge exchanges
10. [Custom Emitters](data-transformation.md#custom-emitter) - Build your own

---

## Source Code

All examples are available in the GitHub repository:

[View on GitHub →](https://github.com/paulobueno90/streamforge/tree/main/examples)

---

## Example Categories

### Basic Streaming

Simple examples to get you started:

- Hello World
- CSV Output  
- Multiple Symbols
- Different Timeframes
- Different Exchanges

[View Examples →](basic-streaming.md)

### Database Output

Save data to databases and streaming platforms:

- PostgreSQL Basic
- PostgreSQL with Upsert
- Kafka Streaming
- Multiple Outputs

[View Examples →](data_emitters.md)

### Data Transformation

Modify and enrich your data:

- Rename Fields
- Add Computed Fields
- Filter Data
- Custom Transformers

[View Examples →](data-transformation.md)

### Advanced Patterns

Complex real-world patterns:

- Multi-Timeframe Aggregation
- Historical Backfilling
- Multi-Exchange Merging
- Arbitrage Detection
- Production Patterns

[View Examples →](advanced-patterns.md)

---

## Running Examples

### Prerequisites

Install StreamForge:

```bash
pip install streamforge
```

For database examples, you'll also need:

```bash
# PostgreSQL
pip install streamforge  # Already includes asyncpg

# For examples with additional dependencies
pip install -r examples/requirements.txt
```

### Running an Example

```bash
# 1. Copy the example code
# 2. Save to a Python file
python my_example.py

# Or download from GitHub
git clone https://github.com/paulobueno90/streamforge.git
cd streamforge/examples
python 01_basic/hello_world.py
```

---

## Example Template

Use this template for your own scripts:

```python
"""
My StreamForge Script
=====================

Description: What this script does

Prerequisites:
- streamforge installed
- (any other requirements)

Run:
    python my_script.py
"""

import asyncio
import streamforge as sf

async def main():
    """Main function"""
    
    # 1. Configure stream
    stream = sf.DataInput(
        type="kline",
        symbols=["BTCUSDT"],
        timeframe="1m"
    )
    
    # 2. Create runner
    runner = sf.BinanceRunner(stream_input=stream)
    
    # 3. Add emitter(s)
    
    
    # 4. Run!
    await runner.run()

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Tips & Tricks

### Start with Logger

Always test with `Logger` first:

```python

```

### Test with Short Periods

Use timeouts for testing:

```python
import asyncio

async def main():
    runner = sf.BinanceRunner(stream_input=stream)
    
    
    # Run for 30 seconds only
    try:
        await asyncio.wait_for(runner.run(), timeout=30)
    except asyncio.TimeoutError:
        print("Test complete!")

asyncio.run(main())
```


## Getting Help

If you need help with examples:

1. Check the [User Guide](../user-guide/emitters.md)
2. Read [Core Concepts](../getting-started/core-concepts.md)
3. See [API Reference](../api-reference/index.md)
4. Ask on [GitHub Discussions](https://github.com/paulobueno90/streamforge/discussions)
5. Report issues on [GitHub Issues](https://github.com/paulobueno90/streamforge/issues)

---

## Next Steps

Ready to dive in?

1. [Basic Streaming →](basic-streaming.md) - Start here
2. [Database Output →](data_emitters.md) - Save your data
3. [Data Transformation →](data-transformation.md) - Customize output
4. [Advanced Patterns →](advanced-patterns.md) - Complex use cases

