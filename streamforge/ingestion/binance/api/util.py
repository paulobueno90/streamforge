from aiolimiter import AsyncLimiter
from streamforge.ingestion.binance.util import MARKET_TYPE_STRING_MAP


BINANCE_API_LIMITER = AsyncLimiter(1000, 60)
BINANCE_API_LIMITER_USDM = AsyncLimiter(400,60)
BINANCE_API_LIMITER_COINM = AsyncLimiter(400,60)

API_LIMITER_MAP = {
    "DEFAULT": BINANCE_API_LIMITER,
    "SPOT": BINANCE_API_LIMITER,
    "FUTURES (USD-M)": BINANCE_API_LIMITER_USDM,
    "FUTURES (COIN-M)": BINANCE_API_LIMITER_COINM,
}

API_BASE_URL_MAP = {
    "DEFAULT": "https://api.binance.com/api/v3",
    "SPOT": "https://api.binance.com/api/v3",
    "FUTURES (USD-M)": "https://fapi.binance.com/fapi/v1",
    "FUTURES (COIN-M)": "https://dapi.binance.com/dapi/v1",
}


def get_api_limiter(market_type: str):
    market_type_string = MARKET_TYPE_STRING_MAP.get(market_type.upper(), "DEFAULT")
    return API_LIMITER_MAP.get(market_type_string, BINANCE_API_LIMITER)


def get_api_base_url(market_type: str):
    market_type_string = MARKET_TYPE_STRING_MAP.get(market_type.upper(), "DEFAULT")
    return API_BASE_URL_MAP.get(market_type_string, "https://api.binance.com/api/v3")






