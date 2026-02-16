"""
Bybit API utilities for rate limiting and base URL mapping.

Note: Bybit uses the same API endpoint (/v5/market/kline) for all market types
(spot, linear, inverse) with only the 'category' parameter differing. Therefore,
all market types share the same rate limit pool and must use a single shared limiter.
"""

from aiolimiter import AsyncLimiter
from streamforge.ingestion.bybit.util import MARKET_TYPE_STRING_MAP


BYBIT_API_LIMITER = AsyncLimiter(20, 1)

API_LIMITER_MAP = {
    "DEFAULT": BYBIT_API_LIMITER,
    "SPOT": BYBIT_API_LIMITER,
    "LINEAR": BYBIT_API_LIMITER,  # Shared limiter - same endpoint
    "INVERSE": BYBIT_API_LIMITER,  # Shared limiter - same endpoint
}

# Bybit uses the same base URL for all market types, but different category parameter
API_BASE_URL = "https://api.bybit.com/v5/market"

API_BASE_URL_MAP = {
    "DEFAULT": API_BASE_URL,
    "SPOT": API_BASE_URL,
    "LINEAR": API_BASE_URL,
    "INVERSE": API_BASE_URL,
}


def get_api_limiter(market_type: str):
    """
    Get rate limiter for the specified market type.
    
    Args:
        market_type: Market type string (SPOT, LINEAR, INVERSE, etc.)
        
    Returns:
        AsyncLimiter instance for the market type
    """
    market_type_string = MARKET_TYPE_STRING_MAP.get(market_type.upper(), "DEFAULT")
    return API_LIMITER_MAP.get(market_type_string, BYBIT_API_LIMITER)


def get_api_base_url(market_type: str):
    """
    Get base URL for the specified market type.
    
    Args:
        market_type: Market type string (SPOT, LINEAR, INVERSE, etc.)
        
    Returns:
        Base URL string for Bybit API
    """
    market_type_string = MARKET_TYPE_STRING_MAP.get(market_type.upper(), "DEFAULT")
    return API_BASE_URL_MAP.get(market_type_string, API_BASE_URL)

