import streamforge as sf


def transformer_function_example(data: dict):

    return {
        "source": data["source"],
        "timeframe": data["timeframe"],
        "open_ts": data["open_ts"],
        "end_ts": data["end_ts"],
        "open": data["open"],
        "high": data["high"],
        "low": data["low"],
        "close": data["close"],
        "volume": data["volume"]
    }

# if you don't use any transformer it will send the default data that comes from normalizer to the file
backfiller = sf.BybitBackfilling(symbol="BTCUSDT", timeframe="1m", from_date="2024-01-01", market_type="SPOT")
backfiller.set_transformer(transformer_function_example)
backfiller.run()

