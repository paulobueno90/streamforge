"""
CSV Emitter - Basic Usage
=========================

Save streaming cryptocurrency data to CSV files.

Note: This example is just to show how to use the CSV emitter.
You can use the CSV emitter to save the data to a file.
But in real-world scenarios, you would use a database like PostgreSQL or MongoDB to store the data.
You can check the examples on how to use the PostgreSQL emitter.

Also, CSV is normally best only to backfill data.

Prerequisites:
- streamforge installed
- pandas (included with streamforge)

What it does:
- Streams live data from Binance
- Saves to CSV file
- Automatically appends new data

Run:
    python csv_basic.py
"""

import asyncio
import streamforge as sf


async def basic_csv():
    """
    Basic CSV Export
    """
    runner = sf.BinanceRunner(
        stream_input=sf.DataInput(
            type="kline",
            symbols=["BTCUSDT"],
            timeframe="1m"
        )
    )
    
    # CSV emitter - data will be saved to file
    csv_emitter = sf.CSVEmitter(
        source="Binance",
        symbol="BTCUSDT",
        timeframe="1m",
        file_path="btc_1m.csv"
    )
    
    runner.register_emitter(csv_emitter)
    
    await runner.run()


if __name__ == "__main__":
    asyncio.run(basic_csv())

