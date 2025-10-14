class KrakenAPIBanError(Exception):
    """Custom exception for a Kraken API ban."""
    pass


class KrakenAPIError(Exception):
    """Custom exception for general Kraken API errors."""
    pass