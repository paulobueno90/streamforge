"""
Bybit API client for fetching historical kline/candlestick data.
"""

import sys
import asyncio
import aiohttp

from datetime import datetime, timezone
from .error import BybitAPIBanError, BybitAPIError

from streamforge.base.normalize.ohlc.models.timeframes import BaseTimeframe
from streamforge.base.api import BaseCandleAPI
from streamforge.base.config import config
from streamforge.ingestion.bybit.api.util import get_api_limiter, get_api_base_url
from streamforge.ingestion.bybit.util import MARKET_TYPE_STRING_MAP, MARKET_TYPE_PATH_MAP, get_bybit_timeframe


KLINE_ENDPOINT = '/kline'


class BybitAPI(BaseCandleAPI):
    """
    Bybit API client for fetching historical candlestick data.
    
    Supports Spot, Linear (USDT/USDC perpetuals), and Inverse futures markets.
    """
    
    def __init__(self,
                 market_type: str = "DEFAULT",
                 api_call_limit: int = 1000  # Bybit maximum limit per request (range: 1-1000)
                 ):
        api_limiter = get_api_limiter(market_type=market_type)
        base_url = get_api_base_url(market_type=market_type)
        
        self.market_type = market_type
        self.market_type_string = MARKET_TYPE_STRING_MAP.get(market_type.upper(), "SPOT")
        self.category = MARKET_TYPE_PATH_MAP.get(self.market_type_string, "spot")
        
        super().__init__(base_url=base_url, api_limiter=api_limiter, api_call_limit=api_call_limit)

    def _process_warmup_urls(self, symbol: str, timeframe: BaseTimeframe):
        """
        Generate URLs for warmup data fetching.
        
        Bybit API format:
        /v5/market/kline?category={category}&symbol={symbol}&interval={interval}&limit={limit}&start={start}&end={end}
        """
        urls = []
        daily_multiplier = (24 * 60 * 60)
        utc_timestamp_now = int(datetime.now(timezone.utc).timestamp())
        start_timestamp = (utc_timestamp_now // daily_multiplier) * daily_multiplier
        n_datapoints = (utc_timestamp_now - start_timestamp) // timeframe.offset

        # Convert timeframe to Bybit format
        bybit_interval = get_bybit_timeframe(timeframe.string_tf)
        
        # Bybit uses milliseconds for timestamps
        start_ms = start_timestamp * 1000
        end_ms = utc_timestamp_now * 1000

        if n_datapoints <= self.limit:
            url = f"{self.url}{KLINE_ENDPOINT}?category={self.category}&symbol={symbol.upper()}&interval={bybit_interval}&limit={self.limit}&start={start_ms}&end={end_ms}"
            urls.append(url)
        else:
            # Split into two requests if needed
            middle_timestamp = start_timestamp + (1000 * 60)
            middle_ms = middle_timestamp * 1000
            
            first_url = f"{self.url}{KLINE_ENDPOINT}?category={self.category}&symbol={symbol.upper()}&interval={bybit_interval}&limit={self.limit}&start={start_ms}&end={middle_ms}"
            second_url = f"{self.url}{KLINE_ENDPOINT}?category={self.category}&symbol={symbol.upper()}&interval={bybit_interval}&limit={self.limit}&start={(middle_timestamp + 1) * 1000}&end={end_ms}"

            urls.append(first_url)
            urls.append(second_url)

        return urls

    async def _fetch_data_with_limit(self, session, url, params: any = None):
        """
        Fetch data from Bybit API with rate limiting.
        
        Bybit response format:
        {
            "retCode": 0,
            "retMsg": "OK",
            "result": {
                "symbol": "BTCUSDT",
                "category": "spot",
                "list": [
                    [startTime, open, high, low, close, volume, turnover],
                    ...
                ]
            }
        }
        """
        async with self.limiter:
            try:
                async with session.get(url) as response:
                    response.raise_for_status()
                    data = await response.json()
                    
                    # Check Bybit response code
                    if data.get("retCode") != 0:
                        ret_msg = data.get("retMsg", "Unknown error")
                        if "rate limit" in ret_msg.lower() or "too many requests" in ret_msg.lower():
                            config.logger.warning(f"Bybit rate limit exceeded: {ret_msg}. Waiting...")
                            await asyncio.sleep(5)  # Wait 5 seconds for Bybit
                            return await self._fetch_data_with_limit(session, url, params)
                        else:
                            raise BybitAPIError(f"Bybit API error: {ret_msg} (retCode: {data.get('retCode')})")
                    
                    # Return the list of klines from result
                    result = data.get("result", {})
                    klines = result.get("list", [])
                    return klines
                    
            except aiohttp.ClientResponseError as e:
                if e.status == 429:
                    config.logger.warning("Rate limit exceeded. Waiting...")
                    await asyncio.sleep(5)
                    return await self._fetch_data_with_limit(session, url, params)
                elif e.status == 403:
                    config.logger.critical(f"IP has been temporarily banned. Status: {e.status}")
                    raise BybitAPIBanError(f"IP has been temporarily banned. Status: {e.status}")
                else:
                    raise Exception(f"HTTP Error for {url}: {e.status} - {e.message}")

            except aiohttp.ClientConnectionError as e:
                config.logger.error(f"Connection Error for {url}: {e}")
                raise ConnectionError(f"Connection Error for {url}: {e}")
            except Exception as e:
                config.logger.error(f"An unexpected error occurred: {e}")
                raise Exception(f"An unexpected error occurred: {e}")

    async def get_info(self):
        """
        Get exchange information (optional, for future use).
        """
        url = "https://api.bybit.com/v5/market/instruments-info"
        params = {"category": self.category}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    response.raise_for_status()
                    data = await response.json()
                    if data.get("retCode") != 0:
                        raise BybitAPIError(f"Bybit API error: {data.get('retMsg')}")
                    return data
        except Exception as e:
            config.logger.error(f"Critical error: {e}. Shutting down.")
            sys.exit(1)

    def _process_historical_inputs(self, symbol: str, timeframe: BaseTimeframe, from_date: str, to_date: str):
        """
        Process historical data inputs and generate URL parameters for pagination.
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT')
            timeframe: Timeframe for candles (e.g., '1m', '1h')
            from_date: Start date in '%Y-%m-%d' format
            to_date: End date in '%Y-%m-%d' format or 'now'
            
        Returns:
            List of URL strings for fetching historical data
        """
        daily_multiplier = (24 * 60 * 60)
        
        # Parse to_date
        if to_date == "now":
            to_date_ts = int(datetime.now(timezone.utc).timestamp())
        else:
            to_date_ts = int(datetime.strptime(to_date, "%Y-%m-%d").timestamp())
        
        # Parse from_date
        from_date_ts = int(datetime.strptime(from_date, "%Y-%m-%d").timestamp())
        
        # Floor timestamps to start of day
        from_date_ts = (from_date_ts // daily_multiplier) * daily_multiplier
        to_date_ts = (to_date_ts // daily_multiplier) * daily_multiplier
        
        # Convert to milliseconds for Bybit API
        start_timestamp_ms = from_date_ts * 1000
        end_timestamp_ms = to_date_ts * 1000
        
        # Convert timeframe to Bybit format
        bybit_interval = get_bybit_timeframe(timeframe.string_tf)
        
        historical_urls = []
        current_start_ms = start_timestamp_ms
        
        while current_start_ms < end_timestamp_ms:
            # Calculate end for this chunk (limit candles per request)
            # Bybit maximum limit is 1000, so we fetch up to 1000 candles at a time
            chunk_end_ms = min(
                current_start_ms + (self.limit * timeframe.offset * 1000),
                end_timestamp_ms
            )
            
            url = f"{self.url}{KLINE_ENDPOINT}?category={self.category}&symbol={symbol.upper()}&interval={bybit_interval}&limit={self.limit}&start={current_start_ms}&end={chunk_end_ms}"
            historical_urls.append(url)
            
            # Move to next chunk
            current_start_ms = chunk_end_ms + 1
        
        return historical_urls

    async def fetch_historical_candles(self, symbol: str, timeframe: BaseTimeframe, from_date: str, to_date: str):
        """
        Fetch historical candle/kline data for a symbol within a date range.
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT')
            timeframe: Timeframe for candles (e.g., '1m', '1h')
            from_date: Start date in '%Y-%m-%d' format
            to_date: End date in '%Y-%m-%d' format or 'now'
            
        Yields:
            Batches of kline arrays: [[startTime, open, high, low, close, volume, turnover], ...]
        """
        urls = self._process_historical_inputs(symbol=symbol, timeframe=timeframe, from_date=from_date, to_date=to_date)
        
        async with aiohttp.ClientSession() as session:
            for url in urls:
                klines = await self._fetch_data_with_limit(session, url)
                if klines:
                    # Bybit returns data in reverse chronological order (newest first)
                    # Reverse to get chronological order (oldest first)
                    klines.reverse()
                    yield klines

    async def fetch_candles(self, symbol: str, timeframe: BaseTimeframe):
        """
        Fetch historical candle/kline data for a symbol.
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT')
            timeframe: Timeframe for candles (e.g., '1m', '1h')
            
        Returns:
            List of kline arrays: [[startTime, open, high, low, close, volume, turnover], ...]
        """
        try:
            urls = self._process_warmup_urls(symbol=symbol, timeframe=timeframe)
            async with aiohttp.ClientSession() as session:
                tasks = [self._fetch_data_with_limit(session, url) for url in urls]
                responses = await asyncio.gather(*tasks)
                # Flatten the list of lists
                all_klines = []
                for response in responses:
                    if isinstance(response, list):
                        all_klines.extend(response)
                return [all_klines]  # Return as list of lists to match Binance format
        except Exception as e:
            config.logger.error(f"Critical error: {e}. Shutting down.")
            sys.exit(1)


bybit_api = BybitAPI()

