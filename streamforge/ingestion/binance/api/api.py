import sys
import asyncio
import aiohttp

from datetime import datetime, timezone
from .error import BinanceAPIBanError


from streamforge.base.normalize.ohlc.models.timeframes import BaseTimeframe
from streamforge.base.api import BaseCandleAPI
from streamforge.base.config import config
from streamforge.ingestion.binance.api.util import get_api_limiter, get_api_base_url


KLINE_BASE_ENDPOINT = '/klines?symbol={}&interval={}&limit={}&startTime={}&endTime={}'





class BinanceAPI(BaseCandleAPI):
    def __init__(self,
                 market_type: str = "DEFAULT",
                 api_call_limit: int = 1000
                 ):

        api_limiter = get_api_limiter(market_type=market_type)
        self.binance_kline_base_endpoint = get_api_base_url(market_type=market_type) + KLINE_BASE_ENDPOINT

        super().__init__(base_url=self.binance_kline_base_endpoint, api_limiter=api_limiter, api_call_limit=api_call_limit)

    def _process_warmup_urls(self, symbol: str, timeframe: BaseTimeframe):
        urls = []
        daily_multiplier = (24 * 60 * 60)
        utc_timestamp_now = int(datetime.now(timezone.utc).timestamp())
        start_timestamp = (utc_timestamp_now // daily_multiplier) * daily_multiplier
        n_datapoints = (utc_timestamp_now - start_timestamp) // timeframe.offset

        if n_datapoints <= self.limit:
            url = self.binance_kline_base_endpoint.format(
                symbol.upper(),
                timeframe.string_tf,
                self.limit,
                start_timestamp * 1000,
                utc_timestamp_now * 1000
            )
            urls.append(url)

        else:
            middle_timestamp = start_timestamp + (1000 * 60)
            first_url = self.binance_kline_base_endpoint.format(
                symbol.upper(),
                timeframe.string_tf,
                self.limit,
                start_timestamp * 1000,
                middle_timestamp * 1000
            )

            second_url = self.binance_kline_base_endpoint.format(
                symbol.upper(),
                timeframe.string_tf,
                self.limit,
                (middle_timestamp + 1) * 1000,
                utc_timestamp_now * 1000
            )

            urls.append(first_url)
            urls.append(second_url)

        return urls

    async def _fetch_data_with_limit(self, session, url):
        async with self.limiter:
            try:
                async with session.get(url) as response:
                    response.raise_for_status()
                    return await response.json()
            except aiohttp.ClientResponseError as e:
                if e.status == 429:
                    config.logger.warning("Rate limit exceeded. Waiting...")
                    await asyncio.sleep(60)
                    return await self._fetch_data_with_limit(session, url)
                elif e.status == 418:
                    config.logger.critical(f"IP has been temporarily banned. Status: {e.status}")
                    raise BinanceAPIBanError(f"IP has been temporarily banned. Status: {e.status}")
                else:
                    raise Exception(f"HTTP Error for {url}: {e.status} - {e.message}")

            except aiohttp.ClientConnectionError as e:
                config.logger.error(f"Connection Error for {url}: {e}")
                raise ConnectionError(f"Connection Error for {url}: {e}")
            except Exception as e:
                config.logger.error(f"An unexpected error occurred: {e}")
                raise Exception(f"An unexpected error occurred: {e}")

    async def get_info(self):
        url = "https://api.binance.com/api/v3/exchangeInfo"
        try:
            async with aiohttp.ClientSession() as session:
                info = await self._fetch_data_with_limit(session, url)
                return info

        except Exception as e:
            config.logger.error(f"Critical error: {e}. Shutting down.")
            sys.exit(1)

    async def fetch_candles(self, symbol: str, timeframe: BaseTimeframe):
        try:
            urls = self._process_warmup_urls(symbol=symbol, timeframe=timeframe)
            async with aiohttp.ClientSession() as session:
                tasks = [self._fetch_data_with_limit(session, url) for url in urls]
                response = await asyncio.gather(*tasks)
                return response
        except Exception as e:
            config.logger.error(f"Critical error: {e}. Shutting down.")
            sys.exit(1)


binance_api = BinanceAPI()
