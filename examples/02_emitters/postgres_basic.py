"""
PostgreSQL Emitter - Basic Usage
================================

Save streaming data to PostgreSQL database using SQLAlchemy ORM.

Prerequisites:
- PostgreSQL server running
- Database created
- streamforge installed with: pip install streamforge[postgresql]

Setup Database:
```sql
CREATE TABLE klines (
    source VARCHAR(255) NOT NULL,
    symbol VARCHAR(255) NOT NULL,
    timeframe VARCHAR(50) NOT NULL,
    open_ts BIGINT NOT NULL,
    end_ts BIGINT,
    open FLOAT,
    high FLOAT,
    low FLOAT,
    close FLOAT,
    volume FLOAT,
    
    PRIMARY KEY (source, symbol, timeframe, open_ts)
);
```

Run:
    python postgres_basic.py
"""

import asyncio
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String, Float, BigInteger
import streamforge as sf


Base = declarative_base()


class KlineTable(Base):
    """
    SQLAlchemy ORM Model for Kline/Candlestick Data
    
    Must match your database table structure
    """
    __tablename__ = 'klines'
    
    # Primary key components
    source = Column(String, primary_key=True)
    symbol = Column(String, primary_key=True)
    timeframe = Column(String, primary_key=True)
    open_ts = Column(BigInteger, primary_key=True)
    
    # Data fields
    end_ts = Column(BigInteger)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Float)


async def basic_postgres():
    """
    Basic PostgreSQL streaming
    """
    # Create PostgreSQL emitter
    postgres_emitter = sf.PostgresEmitter(
        host="localhost",
        dbname="crypto",
        user="postgres",
        password="mysecretpassword",
        port=5432
    )
    
    # Set the ORM model
    postgres_emitter.set_model(KlineTable, inplace=True)
    
    # Create runner
    runner = sf.BinanceRunner(
        stream_input=sf.DataInput(
            type="kline",
            symbols=["BTCUSDT"],
            timeframe="1m"
        )
    )
    
    # Register emitter
    runner.register_emitter(postgres_emitter)
    
    # Start streaming
    await runner.run()


async def postgres_with_url():
    """
    Alternative: Use connection URL instead of individual parameters
    """
    postgres_emitter = sf.PostgresEmitter(
        url="postgresql+asyncpg://postgres:mysecretpassword@localhost:5432/crypto"
    )
    
    postgres_emitter.set_model(KlineTable, inplace=True)
    
    runner = sf.BinanceRunner(
        stream_input=sf.DataInput(
            type="kline",
            symbols=["BTCUSDT"],
            timeframe="1m"
        )
    )
    
    runner.register_emitter(postgres_emitter)
    
    await runner.run()


if __name__ == "__main__":
    # Choose one:
    asyncio.run(basic_postgres())
    # asyncio.run(postgres_with_url())

