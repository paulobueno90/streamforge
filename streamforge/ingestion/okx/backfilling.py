import logging
import asyncio
import datetime as dt
from datetime import datetime, timezone
from pydantic import BaseModel
from typing import List, Dict, Optional, Any, Union, Callable
from pathlib import Path

import numpy as np
import pandas as pd

from dateutil.relativedelta import relativedelta
from streamforge.base.emitters import PostgresEmitter
from streamforge.base.data_container.ohlc import CandleData, get_start_timestamp,filter_timestamp

from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Float, BigInteger

from streamforge.base.emitters.base import DataEmitter, EmitterHolder
from streamforge.ingestion.okx.normalizers.normalizer import KlineNormalizer
from streamforge.ingestion.okx.api.ohlc import OkxCandleApi
from streamforge.base.normalize.ohlc.models.timeframes import TIMEFRAME_CLASS_MAP
from streamforge.base.normalize.ohlc.models.candle import Kline
from streamforge.base.emitters.csv.csv import CSVEmitter
from streamforge.ingestion.okx.processors.candle import iterate_okx_api_data


Base = declarative_base()


klines_column_names = [
    'datetime',
    'open',
    'high',
    'low',
    'close',
    'volume',
    'close time',
    'Quote asset volume',
    'Number of trades',
    'Taker buy base asset volume',
    'Taker buy quote asset volume',
    'Ignore'
]

klines_columns_dtypes = {
    'datetime': 'Int64',
    'open': 'float64',
    'high': 'float64',
    'low': 'float64',
    'close': 'float64',
    'volume': 'float64',
    'close time': 'Int64',
    'Quote asset volume': 'float64',
    'Number of trades': 'Int64',
    'Taker buy base asset volume': 'float64',
    'Taker buy quote asset volume': 'float64',
    'Ignore': bool,
    }


class OkxBackfilling:

    _emitter_holder = EmitterHolder()
    _api = OkxCandleApi()
    _normalizer = KlineNormalizer()

    def __init__(self,
                 symbol: str,
                 timeframe: str,
                 from_date: str,
                 to_date: str = "now",
                 file_path: Optional[str] = None,
                 data_type: str = 'klines',
                 transformer: Optional[Callable[[Dict[str,Any]], Dict[str, Any]]] = None
                 ):

        self.symbol = symbol
        self.timeframe = timeframe
        self.from_date = from_date
        self.to_date = to_date
        self.symbol_type = "spot"
        self.data_type = data_type

        self.file_path = self._file_name() if file_path is None else file_path

        self.transformer = transformer

    def _file_name(self):
        today_string = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        end_date_string = today_string if ((self.to_date == "now") or (self.to_date is None)) else self.to_date
        file_name = f"Okx-{self.symbol.replace('/', '')}-{self.timeframe}-{self.from_date}_{end_date_string}.csv"
        return file_name

    def set_transformer(self, transformer_func: Callable[[Dict[str, Any]], Dict[str, Any]], inplace: bool = False):
        self.transformer = transformer_func
        if inplace:
            return None
        else:
            return self

    def transform(self, data: Union[Dict[str, Any], Kline]):

        if not isinstance(data, dict):
            data = data.model_dump()

        if self.transformer is not None:
            return self.transformer(data)
        else:
            return data

    def register_emitter(
            self,
            emitter: DataEmitter,
            model: Optional[Union[Base, BaseModel]] = None,
            map_object: Optional[Dict] = None
    ):
        if emitter.EMITTER == "csv":
            emitter.set_file_path(file_path=self.file_path, inplace=True)
        self._emitter_holder.add(emitter=emitter, data_model=model, columns_map=map_object)
        logging.info(f"Okx | ADDED | name: '{emitter.EMITTER}' type: '{emitter.EMITTER_TYPE}'")

    def _parse_date(self, date_string: str, format_string: str = "%Y-%m-%d"):
        try:
            return datetime.strptime(date_string, format_string)
        except ValueError:
            raise ValueError(f"date_string: {date_string} expected to be in the format '{format_string}'")

    async def fetch_historical_data(self):
        tf_class = TIMEFRAME_CLASS_MAP[self.timeframe]
        start_timestamp = int(datetime.strptime(self.from_date, "%Y-%m-%d").timestamp())
        async for data in self._api.fetch_historical_candles(
                                            symbol=self.symbol,
                                            timeframe=tf_class,
                                            from_date=self.from_date,
                                            to_date=self.to_date
                                        ):

            for ohlc_data in iterate_okx_api_data(data=data, start_timestamp=start_timestamp):
                yield self._normalizer.api(
                    data=ohlc_data,
                    symbol=self.symbol,
                    timeframe=tf_class)

    async def stream(self, batch_size: int = 1000):
        buffer = []
        async for kline_data in self.fetch_historical_data():
            row = self.transform(kline_data)
            buffer.append(row)
            if len(buffer) >= batch_size:
                yield buffer
                buffer = []

        if buffer:
            yield buffer

    async def _run_with_emitter_bulk(self, batch_size: int = 1000):
        await self._emitter_holder.connect()

        async for batch in self.stream(batch_size=batch_size):
            await self._emitter_holder.emit_bulk(data=batch)

    def run(self):

        if self._emitter_holder.empty:
            csv_emitter = CSVEmitter(
                source="Okx",
                symbol=self.symbol,
                timeframe=self.timeframe,
                transformer_function=self.transformer
            )

            self.register_emitter(emitter=csv_emitter)

        asyncio.run(self._run_with_emitter_bulk())









