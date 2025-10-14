"""
Kafka Emitter - Basic Usage
===========================

Stream cryptocurrency data to Apache Kafka topics.

Prerequisites:
- Kafka server running (localhost:9092)
- streamforge installed with: pip install streamforge[kafka]
- aiokafka package installed

Setup Kafka (using Docker):
```bash
docker run -d --name kafka -p 9092:9092 \
  -e KAFKA_ENABLE_KRAFT=yes \
  -e KAFKA_CFG_PROCESS_ROLES=broker,controller \
  -e KAFKA_CFG_CONTROLLER_LISTENER_NAMES=CONTROLLER \
  -e KAFKA_CFG_LISTENERS=PLAINTEXT://:9092,CONTROLLER://:9093 \
  -e KAFKA_CFG_LISTENER_SECURITY_PROTOCOL_MAP=CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT \
  -e KAFKA_CFG_ADVERTISED_LISTENERS=PLAINTEXT://localhost:9092 \
  bitnami/kafka:latest
```

Run:
    python kafka_basic.py
"""

import asyncio
import streamforge as sf


async def basic_kafka():
    """
    Pattern 1: Basic Kafka Streaming
    
    Stream data to a Kafka topic
    """
    print("\n" + "="*60)
    print("PATTERN 1: Basic Kafka Streaming")
    print("="*60)
    
    # Create Kafka emitter
    kafka_emitter = sf.KafkaEmitter(
        topic="crypto-klines",              # Kafka topic name
        bootstrap_servers="localhost:9092"   # Kafka broker address
    )
    
    # Create runner
    runner = sf.BinanceRunner(
        stream_input=sf.DataInput(
            type="kline",
            symbols=["BTCUSDT","ETHUSDT","SOLUSDT"],
            timeframe="1m"
        )
    )
    
    # Register emitter
    runner.register_emitter(kafka_emitter)
    
    print("✓ Streaming BTC data to Kafka topic 'crypto-klines'")
    
    await runner.run()


async def kafka_multiple_symbols():
    """
    Pattern 2: Multiple Symbols to One Topic
    
    Stream multiple cryptocurrencies to the same topic
    """
    print("\n" + "="*60)
    print("PATTERN 2: Multiple Symbols to One Topic")
    print("="*60)
    
    kafka_emitter = sf.KafkaEmitter(
        topic="crypto-all",
        bootstrap_servers="localhost:9092"
    )
    
    runner = sf.BinanceRunner(
        stream_input=sf.DataInput(
            type="kline",
            symbols=["BTCUSDT", "ETHUSDT", "SOLUSDT"],
            timeframe="1m"
        )
    )
    
    runner.register_emitter(kafka_emitter)
    
    print("✓ Streaming BTC, ETH, and SOL to Kafka topic 'crypto-all'")
    
    await runner.run()


async def kafka_with_aggregation():
    """
    Pattern 3: Stream Aggregated Timeframes
    
    Stream base timeframe + aggregated timeframes
    """
    print("\n" + "="*60)
    print("PATTERN 3: Stream with Aggregation")
    print("="*60)
    
    kafka_emitter = sf.KafkaEmitter(
        topic="crypto-multi-tf",
        bootstrap_servers="localhost:9092"
    )
    
    runner = sf.BinanceRunner(
        stream_input=sf.DataInput(
            type="kline",
            symbols=["BTCUSDT","ETHUSDT","SOLUSDT"],
            timeframe="1m",
            aggregate_list=["5m", "15m", "1h"]  # Also send aggregated data
        )
    )
    
    runner.register_emitter(kafka_emitter)
    
    print("✓ Streaming 1m, 5m, 15m, and 1h candles to Kafka")
    
    await runner.run()



async def kafka_multiple_exchanges():
    """
    Pattern 5: Multiple Exchanges to Different Topics
    
    Stream data from different exchanges to separate Kafka topics
    """
    print("\n" + "="*60)
    print("PATTERN 5: Multiple Exchanges to Different Topics")
    print("="*60)
    
    # Kafka emitters for different exchanges
    binance_kafka = sf.KafkaEmitter(
        topic="binance-klines",
        bootstrap_servers="localhost:9092"
    )
    
    okx_kafka = sf.KafkaEmitter(
        topic="okx-candles",
        bootstrap_servers="localhost:9092"
    )
    
    kraken_kafka = sf.KafkaEmitter(
        topic="kraken-ohlc",
        bootstrap_servers="localhost:9092"
    )
    
    # Create runners
    binance_runner = sf.BinanceRunner(
        stream_input=sf.DataInput(type="kline", symbols=["BTCUSDT","ETHUSDT","SOLUSDT"], timeframe="1m")
    )
    binance_runner.register_emitter(binance_kafka)
    
    okx_runner = sf.OKXRunner(
        stream_input=sf.DataInput(type="candle", symbols=["BTC-USDT","ETH-USDT","SOL-USDT"], timeframe="1m")
    )
    okx_runner.register_emitter(okx_kafka)
    
    kraken_runner = sf.KrakenRunner(
        stream_input=sf.DataInput(type="ohlc", symbols=["BTC/USD","ETH/USD","SOL/USD"], timeframe="1m")
    )
    kraken_runner.register_emitter(kraken_kafka)
    
    print("✓ Streaming from 3 exchanges to separate Kafka topics:")
    print("  - binance-klines")
    print("  - okx-candles")
    print("  - kraken-ohlc")
    
    # Run all in parallel
    await asyncio.gather(
        binance_runner.run(),
        okx_runner.run(),
        kraken_runner.run()
    )


async def main():
    """
    Kafka Use Cases:
    
    ✓ Real-time data pipelines
    ✓ Microservices communication
    ✓ Event streaming
    ✓ Decoupling producers from consumers
    ✓ Scalable data distribution
    """
    print("""
╔══════════════════════════════════════════════════════════════╗
║              Kafka Emitter: Basic Usage                     ║
╚══════════════════════════════════════════════════════════════╝

Available patterns:
1. basic_kafka() - Simple streaming to Kafka
2. kafka_multiple_symbols() - Multiple symbols, one topic
3. kafka_with_aggregation() - Stream aggregated timeframes
4. kafka_multiple_exchanges() - Different exchanges, different topics

Make sure Kafka is running on localhost:9092!

Choose one pattern below:
""")
    
    # Uncomment ONE pattern to run:
    await basic_kafka()
    # await kafka_multiple_symbols()
    # await kafka_with_aggregation()
    # await kafka_multiple_exchanges()


if __name__ == "__main__":
    asyncio.run(main())

