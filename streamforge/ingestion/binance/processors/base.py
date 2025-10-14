from streamforge.ingestion.binance.processors.kline import KlineBinance
from streamforge.base.stream_input import DataInput


class BinanceProcessor:

    _kline = KlineBinance
    _aggtrade = None
    _trade = None
    _bookticker = None
    _depth = None

    def __init__(self,
                 stream_input: DataInput
                 ):
        if stream_input.type in ["kline", "klines"]:
            self.processor = KlineBinance
        elif stream_input.type == "aggtrade":
            raise NotImplementedError(f"Processor for '{stream_input.type}' type  is not implemented.")
        elif stream_input.type == "trade":
            raise NotImplementedError(f"Processor for '{stream_input.type}' type  is not implemented.")
        elif stream_input.type == "bookticker":
            raise NotImplementedError(f"Processor for '{stream_input.type}' type  is not implemented.")
        elif stream_input.type == "depth":
            raise NotImplementedError(f"Processor for '{stream_input.type}' type  is not implemented.")
        else:
            raise ValueError(f"Stream type: '{stream_input.type}' does not exist or not implmented.")






