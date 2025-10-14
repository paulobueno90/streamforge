import sys
import asyncio
import aiohttp
import logging
from urllib.parse import urlencode
from aiolimiter import AsyncLimiter
from typing import Any

from streamforge.base.api import BaseCandleAPI
from streamforge.base.normalize.ohlc.models.timeframes import BaseTimeframe

from streamforge.ingestion.kraken.api.error import KrakenAPIBanError, KrakenAPIError
from streamforge.ingestion.kraken.api.warnings import timeframe_warning


KRAKEN_API_LIMITER = AsyncLimiter(1, 1)  # 1 request per second for public endpoints
KRAKEN_API_BASE_URL = 'https://api.kraken.com/0/public/OHLC'
KRAKEN_API_INFO_URL = 'https://api.kraken.com/0/public/AssetPairs'


class KrakenAPI(BaseCandleAPI):

    def __init__(self,
                 base_url: str = KRAKEN_API_BASE_URL,
                 api_limiter: AsyncLimiter = KRAKEN_API_LIMITER,
                 api_call_limit: int = 1000
                 ):

        super().__init__(base_url=base_url, api_limiter=api_limiter, api_call_limit=api_call_limit)

    def _process_warmup_urls(self, symbol: str, timeframe: BaseTimeframe):
        """Process URLs for Kraken OHLC data fetching"""
        urls = []
        kraken_symbol = symbol

        params = {
            'pair': kraken_symbol,
            'interval': timeframe.tf,
            'since': ''  # Empty since gets the most recent data
        }

        url = f"{KRAKEN_API_BASE_URL}?{urlencode(params)}"
        urls.append(url)

        return urls

    async def get_info(self):
        """Get asset pairs information from Kraken"""
        url = KRAKEN_API_INFO_URL
        try:
            async with aiohttp.ClientSession() as session:
                info = await self._fetch_data_with_limit(session, url)
                return info

        except Exception as e:
            logging.error(f"Critical error: {e}. Shutting down.")
            sys.exit(1)

    async def fetch_candles(self, symbol: str, timeframe: BaseTimeframe):
        """Fetch OHLC data from Kraken"""
        timeframe_warning(tf_offset=timeframe.offset)

        try:
            urls = self._process_warmup_urls(symbol=symbol, timeframe=timeframe)

            async with aiohttp.ClientSession() as session:
                tasks = [self._fetch_data_with_limit(session, url) for url in urls]
                response = await asyncio.gather(*tasks)
                return response[0]["result"][symbol]
        except Exception as e:
            logging.error(f"Critical error: {e}. Shutting down.")
            sys.exit(1)

    async def _fetch_data_with_limit(self, session, url, params: Any = None):
        """Fetch data with rate limiting and error handling"""
        async with self.limiter:
            try:
                async with session.get(url) as response:
                    response.raise_for_status()
                    data = await response.json()

                    # Check for Kraken API errors
                    if data.get('error') and len(data['error']) > 0:
                        error_msg = data['error'][0]
                        if 'Rate limit' in error_msg:
                            logging.warning("Rate limit exceeded. Waiting...")
                            await asyncio.sleep(60)
                            return await self._fetch_data_with_limit(session, url)
                        elif 'IP banned' in error_msg or 'temporarily banned' in error_msg:
                            logging.critical(f"IP has been temporarily banned. Error: {error_msg}")
                            raise KrakenAPIBanError(f"IP has been temporarily banned. Error: {error_msg}")
                        else:
                            raise KrakenAPIError(f"Kraken API Error: {error_msg}")

                    return data

            except aiohttp.ClientResponseError as e:
                if e.status == 429:
                    logging.warning("Rate limit exceeded. Waiting...")
                    await asyncio.sleep(60)
                    return await self._fetch_data_with_limit(session, url)
                elif e.status == 418:
                    logging.critical(f"IP has been temporarily banned. Status: {e.status}")
                    raise KrakenAPIBanError(f"IP has been temporarily banned. Status: {e.status}")
                else:
                    raise Exception(f"HTTP Error for {url}: {e.status} - {e.message}")

            except aiohttp.ClientConnectionError as e:
                logging.error(f"Connection Error for {url}: {e}")
                raise ConnectionError(f"Connection Error for {url}: {e}")
            except Exception as e:
                logging.error(f"An unexpected error occurred: {e}")
                raise Exception(f"An unexpected error occurred: {e}")


kraken_api = KrakenAPI()




