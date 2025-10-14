from sqlalchemy import Column, Integer, String, Float, BigInteger



import asyncio
from streamforge.ingestion import binance
from streamforge.base.emitters import KafkaEmitter, PostgresEmitter
from streamforge.base.model.sql import Base

from sqlalchemy.ext.declarative import declared_attr, as_declarative

if __name__ == "__main__":

    symbols = [
            "btcusdt",
            "ethusdt",
            # "solusdt",
            # "xrpusdt",
            # "adausdt",
            # "dogeusdt",
            # "dotusdt",
            # "trxusdt",
            # "maticusdt",
            # "linkusdt",
            # "ltcusdt",
            # "avaxusdt",
            # "shibusdt",
        ]


    class PriceData2(Base):
        __tablename__ = 'price_data'
        id = Column(Integer, primary_key=True)
        source = Column(String)
        timeframe = Column(String)
        open_ts = Column(BigInteger)
        end_ts = Column(BigInteger)
        close = Column(Float)

    db_kline_emitter = PostgresEmitter(
        host="localhost",
        dbname="postgres",
        user="postgres",
        password="mysecretpassword"
    ).set_model(PriceData2)

    #db_kline_emitter.set_model(PriceData2, inplace=True)

    streaming_kafka = KafkaEmitter(topic="test")
    logger = binance.Logger()

    input_kline_example = binance.DataInput(
        type="klines",
        symbols=symbols,
        timeframe="1m",
        aggregate_list=["5m", "15m"]
    )

    runner = binance.BinanceRunner()
    runner.set_websocket_input(input_kline_example)
    runner.register_emitter(emitter=logger)
    #runner.register_emitter(emitter=streaming_kafka)
    #runner.register_emitter(emitter=db_kline_emitter)
    asyncio.run(runner.run())