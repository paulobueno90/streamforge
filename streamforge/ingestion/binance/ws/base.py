
STREAMS_MAP = {
    "trade": "{}@trade",
    "aggTrade": "{}@aggTrade",
    "kline": "{}@kline_{}",  # 1m, 5m, 1h, 1d, etc.
    "candle": "{}@kline_{}",
    "ohlcv": "{}@kline_{}",
    "miniTicker": "{}@miniTicker",
    "ticker": "{}@ticker",
    "all_tickers": "!ticker@arr",

}
