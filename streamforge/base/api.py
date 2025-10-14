from abc import ABC, abstractmethod
from typing import Union, Dict, Any, List, AnyStr
from streamforge.base.normalize.ohlc.models.timeframes import BaseTimeframe
from aiolimiter import AsyncLimiter


class BaseCandleAPI(ABC):

    def __init__(
            self,
            base_url: str,
            api_limiter: AsyncLimiter,
            api_call_limit: int
    ):

        self.limiter = api_limiter
        self.limit = api_call_limit
        self.url = base_url

    @abstractmethod
    async def _fetch_data_with_limit(self, session, url, params: Any = None):
        """Fetch data from API with rate limiting."""
        pass

    @abstractmethod
    async def get_info(self):
        """Get exchange information and metadata."""
        pass

    @abstractmethod
    async def fetch_candles(self, symbol: str, timeframe: BaseTimeframe):
        """
        Fetch historical candle/kline data for a symbol.
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT')
            timeframe: Timeframe for candles (e.g., '1m', '1h')
            
        Returns:
            List of historical candle data
        """
        pass

    async def fetch_kline(self, symbol: str, timeframe: BaseTimeframe):
        response = await self.fetch_candles(symbol=symbol, timeframe=timeframe)
        return response

    async def fetch_ohlc(self, symbol: str, timeframe: BaseTimeframe):
        response = await self.fetch_candles(symbol=symbol, timeframe=timeframe)
        return response
