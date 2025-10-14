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


import streamforge as sf
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Float, BigInteger
import logging

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


# Example with chain settings
# db_kline_emitter = sf.PostgresEmitter(
#                             host="localhost",
#                             dbname="postgres",
#                             user="postgres",
#                             password="mysecretpassword",
#                             upsert=True # Upsert is when "on conflict update" will be handled
#                             ).set_model(TableExample).on_conflict(["source","symbol","timeframe", "open_ts"])


db_kline_emitter = sf.PostgresEmitter(host="localhost",
                                      dbname="postgres",
                                      user="postgres",
                                      password="mysecretpassword",
                                      )

db_kline_emitter.set_model(model=TableExample, inplace=True)

# Pass Indexes and all columns that are not the indexes in conflict will be updated
db_kline_emitter.on_conflict(index_elements=["source","symbol","timeframe", "open_ts"], inplace=True)


backfiller = sf.BinanceBackfilling(symbol="BTCUSDT", timeframe="1m", from_date="2025-10-01")
backfiller.register_emitter(db_kline_emitter)
backfiller.run()


backfiller = sf.OkxBackfilling(symbol="BTC-USDT", timeframe="1m", from_date="2025-10-01")
backfiller.register_emitter(db_kline_emitter)
backfiller.run()