from sqlalchemy import Column, Integer, String, Float, TIMESTAMP
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()


class PriceData(Base):
    __tablename__ = "price_data"

    id = Column(Integer, primary_key=True) # Assuming a primary key
    source = Column(String)
    symbol = Column(Integer)
    timestamp = Column(TIMESTAMP)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Float)
    quote_volume = Column(Float)