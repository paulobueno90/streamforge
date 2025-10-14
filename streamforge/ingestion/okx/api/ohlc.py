import sys
import asyncio
import aiohttp
import logging
from typing import List, Tuple, AnyStr, Dict, Any
from aiolimiter import AsyncLimiter
from datetime import datetime, timezone

from streamforge.base.api import BaseCandleAPI
from streamforge.base.normalize.ohlc.models.timeframes import BaseTimeframe


OKX_API_LIMITER = AsyncLimiter(8, 1)

OKX_BASE_CANDLE_URL = "https://www.okx.com/api/v5/market/candles"
OKX_HISTORICAL_CANDLE_URL = "https://www.okx.com/api/v5/market/history-candles"

daily_multiplier = (24 * 60 * 60)


def floor_date_timestamp(timestamp: int):
    return (timestamp // daily_multiplier) * daily_multiplier


class OkxCandleApi(BaseCandleAPI):

    def __init__(self,
                 base_url: str = OKX_BASE_CANDLE_URL,
                 api_limiter: AsyncLimiter = OKX_API_LIMITER,
                 api_call_limit: int = 100
                 ):

        super().__init__(base_url=base_url, api_limiter=api_limiter, api_call_limit=api_call_limit)

        self._historical_data_limit = 250

    def _process_warmup_inputs(self, symbol: AnyStr, timeframe: BaseTimeframe):
        warmup_inputs = []
        daily_multiplier = (24 * 60 * 60)
        utc_timestamp_now = int(datetime.now(timezone.utc).timestamp())
        start_timestamp = (utc_timestamp_now // daily_multiplier) * daily_multiplier

        while True:
            n_datapoints = (utc_timestamp_now - start_timestamp) // timeframe.offset
            if n_datapoints > 0:
                params = {
                    'instId': symbol,
                    'bar': timeframe.string_tf,
                    'limit': self.limit,
                    'after': ((100 * timeframe.offset) + start_timestamp) * 1000,
                }

                warmup_inputs.append(params)
                start_timestamp += (100 * timeframe.offset)

            else:
                break

        return warmup_inputs

    async def _fetch_data_with_limit(self, session, url, params: Any = None):

        async with self.limiter:
            try:
                async with session.get(url, params=params) as response:
                    response.raise_for_status()
                    return await response.json()
            except aiohttp.ClientResponseError as e:
                if e.status == 50011:
                    logging.warning("Rate limit exceeded. Waiting...")
                    await asyncio.sleep(60)
                    return await self._fetch_data_with_limit(session, url, params=params)
                else:
                    raise Exception(f"HTTP Error for {url}: {e.status} - {e.message}")

            except aiohttp.ClientConnectionError as e:
                logging.error(f"Connection Error for {url}: {e}")
                raise ConnectionError(f"Connection Error for {url}: {e}")
            except Exception as e:
                logging.error(f"An unexpected error occurred: {e}")
                raise Exception(f"An unexpected error occurred: {e}")

    async def get_info(self):
        pass

    async def fetch_candles(self, symbol: str, timeframe: BaseTimeframe):

        try:
            params_list = self._process_warmup_inputs(symbol=symbol, timeframe=timeframe)
            async with aiohttp.ClientSession() as session:
                tasks = [self._fetch_data_with_limit(session=session, url=self.url, params=params)
                         for params in params_list]
                response = await asyncio.gather(*tasks)
                return response
        except Exception as e:
            logging.error(f"Critical error: {e}. Shutting down.")
            sys.exit(1)

    def _process_historical_inputs(self, symbol: AnyStr, timeframe: BaseTimeframe,from_date: str, to_date: str):

        if to_date == "now":
            to_date_ts = floor_date_timestamp(timestamp=int(datetime.now(timezone.utc).timestamp()))
        else:
            to_date_ts = floor_date_timestamp(timestamp=int(datetime.strptime(to_date,"%Y-%m-%d").timestamp()))

        from_date_ts = datetime.strptime(from_date, "%Y-%m-%d").timestamp()
        start_timestamp = floor_date_timestamp(timestamp=int(from_date_ts))

        historical_inputs = []

        while True:
            n_datapoints = (to_date_ts - start_timestamp) // timeframe.offset
            if n_datapoints > 0:
                params = {
                    'instId': symbol,
                    'bar': timeframe.string_tf,
                    'limit': self._historical_data_limit,
                    'after': ((self._historical_data_limit * timeframe.offset) + start_timestamp) * 1000,
                }

                historical_inputs.append(params)
                start_timestamp += (self._historical_data_limit * timeframe.offset)

            else:
                break

        return historical_inputs

    async def fetch_historical_candles(self, symbol: str, timeframe: BaseTimeframe, from_date: str, to_date: str):
        #try:
        params_list = self._process_historical_inputs(
                                                    symbol=symbol,
                                                    timeframe=timeframe,
                                                    from_date=from_date,
                                                    to_date=to_date
                                                    )
        async with aiohttp.ClientSession() as session:
            for params in params_list:
                response = await self._fetch_data_with_limit(
                                                session=session,
                                                url=OKX_HISTORICAL_CANDLE_URL,
                                                params=params)
                yield [response]

        # except Exception as e:
        #     logging.error(f"Critical error: {e}. Shutting down.")
        #     sys.exit(1)

