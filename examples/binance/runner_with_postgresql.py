"""
Example with a table in postgresql created like with this:

CREATE TABLE table_example (
    -- String columns (VARCHAR is a standard choice).
    -- These are part of the composite primary key and must be NOT NULL.
    source VARCHAR(255) NOT NULL,
    symbol VARCHAR(255) NOT NULL,
    timeframe VARCHAR(50) NOT NULL,

    -- Integer timestamps (BIGINT for millisecond precision)
    -- This is the final component of the composite primary key.
    open_ts BIGINT NOT NULL,
    end_ts BIGINT,

    -- Floating point data for financial/OHLCV values
    "open" FLOAT,
    high FLOAT,
    low FLOAT,
    "close" FLOAT,
    volume FLOAT,

    -- Define the composite primary key
    PRIMARY KEY (source, symbol, timeframe, open_ts)
);
"""


import asyncio
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Float, BigInteger
import streamforge as sf


Base = declarative_base()


class TableExample(Base):
    __tablename__ = 'table_example'
    source = Column(String, primary_key=True)
    symbol = Column(String, primary_key=True)
    timeframe = Column(String, primary_key=True)
    open_ts = Column(BigInteger, primary_key=True)
    end_ts = Column(BigInteger)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Float)


db_kline_emitter = sf.PostgresEmitter(
                    host="localhost",
                    dbname="postgres",
                    user="postgres",
                    password="mysecretpassword"
                    ).set_model(TableExample)


binance_input = sf.DataInput(
        type="kline",
        symbols=["BTCUSDT", "ETHUSDT", "SOLUSDT"],
        timeframe="1m",
        aggregate_list=["5m", "15m"]
    )


binance_runner = sf.BinanceRunner(stream_input=binance_input)
binance_runner.register_emitter(emitter=db_kline_emitter)

asyncio.run(binance_runner.run())
