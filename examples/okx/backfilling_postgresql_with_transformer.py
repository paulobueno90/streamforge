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
    timestamp BIGINT NOT NULL,

    -- Floating point data for financial/OHLCV values
    o FLOAT,
    h FLOAT,
    l FLOAT,
    c FLOAT,
    v FLOAT,

    -- Define the composite primary key
    PRIMARY KEY (source, symbol, timeframe, timestamp)
);
"""


from streamforge import OkxBackfilling, PostgresEmitter
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Float, BigInteger
import logging

Base = declarative_base()



class TableExample(Base):
    __tablename__ = 'table_example'
    source = Column(String, primary_key=True)
    symbol = Column(String, primary_key=True)
    timeframe = Column(String, primary_key=True)
    timestamp = Column(BigInteger, primary_key=True)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Float)



def transformer_function(data: dict):
    """
    This is an example of a transformer function, this is specially useful in cases where your column names does not
    match the keys from the Kline normalized object.
    """

    return {
        "source": data["source"],
        "symbol": data["symbol"],
        "timeframe": data["timeframe"],
        "timestamp": data["open_ts"],
        "o": data["open"],
        "h": data["high"],
        "l": data["low"],
        "c": data["close"],
        "v": data["volume"]
    }


db_kline_emitter = PostgresEmitter(
                            host="localhost",
                            dbname="postgres",
                            user="postgres",
                            password="mysecretpassword"
                            ).set_model(TableExample
                            ).set_transformer(transformer_function=transformer_function)



backfiller = OkxBackfilling(symbol="BTC-USDT", timeframe="1m", from_date="2025-10-01")
backfiller.register_emitter(db_kline_emitter)
backfiller.run()