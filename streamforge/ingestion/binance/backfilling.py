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

from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Float, BigInteger

from streamforge.base.emitters.base import DataEmitter, EmitterHolder
from streamforge.ingestion.binance.normalizers.normalizer import KlineNormalizer
from streamforge.ingestion.binance.api.api import BinanceAPI
from streamforge.base.normalize.ohlc.models.timeframes import TIMEFRAME_CLASS_MAP
from streamforge.base.normalize.ohlc.models.candle import Kline
from streamforge.base.emitters.csv.csv import CSVEmitter




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


class BinanceBackfilling:

    _emitter_holder = EmitterHolder()
    _api = BinanceAPI()
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

        self._url = 'https://data.binance.vision/data'
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
        file_name = f"Binance-{self.symbol.replace('/', '')}-{self.timeframe}-{self.from_date}_{end_date_string}.csv"
        return file_name

    def set_transformer(self, transformer_func : Callable[[Dict[str,Any]], Dict[str, Any]], inplace: bool = False):
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
        logging.info(f"Binance | ADDED | name: '{emitter.EMITTER}' type: '{emitter.EMITTER_TYPE}'")

    def _parse_date(self, date_string: str, format_string: str = "%Y-%m-%d"):
        try:
            return datetime.strptime(date_string, format_string)
        except ValueError:
            raise ValueError(f"date_string: {date_string} expected to be in the format '{format_string}'")

    def _check_data_requirement(self, initial_date, target_date, current_month, from_date, to_date):

        if initial_date > target_date:
            raise ValueError(
                f"from_date variable cannot be greater than to_date. from_date: {from_date} to_date: {to_date}")

        need_daily_data = False
        need_monthly_data = False

        if target_date >= current_month:
            need_daily_data = True

        if initial_date < current_month:
            need_monthly_data = True

        return need_monthly_data, need_daily_data

    def _get_monthly_dates(self, current_date, previous_month):
        monthly_dates = []

        while current_date <= previous_month:
            monthly_dates.append(current_date.strftime("%Y-%m"))
            current_date = current_date + relativedelta(months=1)

        return monthly_dates, current_date

    def _get_daily_dates(self, current_date, previous_day_date, target_date):
        daily_dates = []

        while current_date <= target_date:

            daily_dates.append(current_date.strftime("%Y-%m-%d"))
            current_date = current_date + relativedelta(days=1)

            if current_date > previous_day_date:
                break

        return daily_dates

    def _get_dates(self):

        date_now = datetime.now(timezone.utc).date()
        previous_day_date = datetime.strptime(date_now.strftime("%Y-%m-%d"), "%Y-%m-%d") - relativedelta(days=1)
        current_month = datetime.strptime(date_now.strftime("%Y-%m"), "%Y-%m")
        previous_month = current_month - relativedelta(months=1)

        if self.to_date == "now":
            target_date = datetime.strptime(date_now.strftime("%Y-%m-%d"), "%Y-%m-%d")
        else:
            target_date = self._parse_date(date_string=self.to_date)

        initial_date = self._parse_date(date_string=self.from_date)

        need_monthly_data, need_daily_data = self._check_data_requirement(
            initial_date=initial_date,
            target_date=target_date,
            current_month=current_month,
            from_date=self.from_date,
            to_date=self.to_date)

        
        

        if need_monthly_data:
            current_date = initial_date.replace(day=1)
            monthly_dates, current_date = self._get_monthly_dates(current_date=current_date, previous_month=previous_month)
        else:
            current_date = initial_date
            monthly_dates = []

        if need_daily_data:
            daily_dates = self._get_daily_dates(
                current_date=current_date,
                previous_day_date=previous_day_date,
                target_date=target_date
            )
        else:
            daily_dates = []

        return monthly_dates, daily_dates

    def _create_monthly_urls(self, monthly_dates: List[str]):
        freq = 'monthly'
        file_path_list = []

        for file_date in monthly_dates:
            url = f"{self._url}/{self.symbol_type}/{freq}/{self.data_type}/{self.symbol}" \
                  f"/{self.timeframe}/{self.symbol}-{self.timeframe}-{file_date}.zip"

            file_path_list.append(url)

        return file_path_list

    def _create_daily_urls(self, daily_dates: List[str]):
        freq = 'daily'
        file_path_list = []
        for file_date in daily_dates:
            url = f"{self._url}/{self.symbol_type}/{freq}/{self.data_type}/{self.symbol}" \
                  f"/{self.timeframe}/{self.symbol}-{self.timeframe}-{file_date}.zip"
            file_path_list.append(url)

        return file_path_list

    def _get_urls(self):
        monthly_dates, daily_dates = self._get_dates()

        monthly_urls = self._create_monthly_urls(monthly_dates=monthly_dates)
        daily_urls = self._create_daily_urls(daily_dates=daily_dates)

        return monthly_urls + daily_urls

    def _read_csv_file(self, file_path: str):
        dataframe = pd.read_csv(file_path,
                           names=klines_column_names,
                           dtype=klines_columns_dtypes,
                           engine='pyarrow')

        for _, row in dataframe.iterrows():
            yield row.to_dict()

    def _get_csv_data(self):
        urls_list = self._get_urls()
        for file_path in urls_list:
            logging.info(f"Binance | Start Processing CSV file | name: '{file_path.split('/')[-1]}'")
            for row in self._read_csv_file(file_path=file_path):
                data = row
                data["s"] = self.symbol
                data["i"] = self.timeframe
                kline_data = self._normalizer.csv(data=data)
                yield kline_data

            logging.info(f"Binance | End Processing CSV file | name: '{file_path.split('/')[-1]}'")

    async def stream(self, batch_size: int = 1000):
        buffer = []
        for kline_data in self._get_csv_data():
            row = self.transform(kline_data)
            buffer.append(row)
            if len(buffer) >= batch_size:
                yield buffer
                buffer = []

        if buffer:
            yield buffer

    async def _get_from_api(self):
        tf_class = TIMEFRAME_CLASS_MAP[self.timeframe]
        logging.info(f"Binance | Fetching data from API")
        data_from_api = await self._api.fetch_candles(symbol=self.symbol, timeframe=tf_class)
        klines = [self._normalizer.api(data=item, symbol=self.symbol, timeframe=self.timeframe) for sublist
                  in data_from_api for item in sublist]

        return klines

    async def _run_with_emitter(self):
        await self._emitter_holder.connect()

        urls_list = self._get_urls()
        for file_path in urls_list:
            for kline_data in self._read_csv_file(file_path=file_path):
                await self._emitter_holder.emit(kline_data)

    async def _run_with_emitter_bulk(self, batch_size: int = 1000):
        await self._emitter_holder.connect()

        async for batch in self.stream(batch_size=batch_size):
            await self._emitter_holder.emit_bulk(data=batch)

        today_string = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        if (today_string == self.to_date) or (self.to_date is None) or (self.to_date == "now"):
            klines = await self._get_from_api()
            klines = [self.transform(data.model_dump()) for data in klines]
            await self._emitter_holder.emit_bulk(data=klines)

    def run(self):

        if self._emitter_holder.empty:
            csv_emitter = CSVEmitter(
                source="Binance",
                symbol=self.symbol,
                timeframe=self.timeframe,
                transformer_function=self.transformer
            )
            self.register_emitter(emitter=csv_emitter)

        asyncio.run(self._run_with_emitter_bulk())
