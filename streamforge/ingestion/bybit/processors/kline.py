"""
Bybit kline/candle data processor for handling real-time and historical data.
"""

import asyncio
from datetime import datetime
from streamforge.base.config import config

from .aggregate import AggregateTF
from .util import check_offset, config_aggregation
from streamforge.base.stream_input import DataInput
from streamforge.base.models import BaseKlineBuffer
from streamforge.base.normalize.ohlc.models.timeframes import TIMEFRAME_CLASS_MAP, TIMEFRAME_BUFFER_SIZE_MAP
from streamforge.base.normalize.ohlc.models.candle import Kline
from streamforge.base.normalize.ohlc.processor import OHLCDatNormalizer
from ..api.api import BybitAPI
from streamforge.ingestion.bybit.api.api import bybit_api

from streamforge.base.data_container.ohlc import CandleData, get_start_timestamp, filter_timestamp
from streamforge.base.data_processor.ohlc import CandleProcessor
from streamforge.base.api import BaseCandleAPI

from streamforge.ingestion.bybit.normalizers.normalizer import BybitNormalizers
from streamforge.ingestion.bybit.normalizers.ohlc import KlineNormalizer
from streamforge.base.normalize.normalize import Normalizer
from streamforge.base.data_processor.aggregate import BaseAggregateTF, AggregateTF


class BybitCandleData(CandleData):
    """
    Bybit-specific candle data container.
    """

    def __init__(self,
                 source: str,
                 symbol: str,
                 timeframe: str,
                 max_len: int,
                 normalizer: Normalizer = KlineNormalizer(),
                 exchange_api: BaseCandleAPI = None,
                 warmup_active: bool = True,
                 emit_active: bool = True,
                 market_type: str = "SPOT"
                 ):
        # Create market-specific API instance if not provided
        if exchange_api is None:
            from streamforge.ingestion.bybit.api.api import BybitAPI
            exchange_api = BybitAPI(market_type=market_type)

        super().__init__("Bybit", symbol, timeframe, max_len, normalizer, exchange_api, warmup_active, emit_active)

    async def _fetch_candle_data(self):
        """
        Fetch historical candle data from Bybit API.
        
        Returns:
            Generator of normalized Kline objects
        """
        data = await self._exchange_api.fetch_kline(self._symbol, self._timeframe)
        klines = (self._normalizer.api(data=item, symbol=self._symbol, timeframe=self._timeframe.string_tf) for sublist in
                  data for item in sublist)
        return klines


class BybitCandleProcessor(CandleProcessor):
    """
    Bybit candle processor for handling kline data processing and aggregation.
    """

    def __init__(self,
                 stream_input: DataInput,
                 data_container_class: CandleData = BybitCandleData,
                 source: str = "Bybit",
                 aggregate_class: BaseAggregateTF = AggregateTF,
                 warmup_active: bool = True,
                 warmup_emit: bool = True,
                 emit_only_closed_candles: bool = True,
                 force_5m_required: bool = False,
                 candle_closed_check: bool = False,
                 market_type: str = "SPOT"
                 ):
        self._market_type = market_type
        super().__init__(stream_input, source, data_container_class, aggregate_class, warmup_active, warmup_emit,
                         emit_only_closed_candles, force_5m_required, candle_closed_check)

    def _process_input(self, stream_input: DataInput):
        """
        Override to pass market_type to CandleData instances.
        """
        for symbol in stream_input.symbols:
            buffer_input = dict(
                source=self.source,
                symbol=symbol,
                timeframe=stream_input.timeframe,
                max_len=TIMEFRAME_BUFFER_SIZE_MAP[stream_input.timeframe],
                emit_active=True,
                market_type=self._market_type  # Pass market_type
            )
            self._data_map[f"{symbol.upper()}-{stream_input.timeframe}"] = self._container_class(**buffer_input)

            if self._agg is not None:
                for timeframe in self._agg.target_timeframes:
                    buffer_input = dict(
                        source=self.source,
                        symbol=symbol,
                        timeframe=timeframe.string_tf,
                        max_len=TIMEFRAME_BUFFER_SIZE_MAP[timeframe.string_tf],
                        emit_active=True,
                        market_type=self._market_type  # Pass market_type
                    )
                    if self._agg.tf_5m_force_included and (timeframe.string_tf == "5m"):
                        buffer_input.update(emit_active=False)

                    self._data_map[f"{symbol.upper()}-{timeframe.string_tf}"] = self._container_class(**buffer_input)


# Keep aggregate.py separate - it can reuse the Binance aggregate logic
# Just import it here for reference
from .aggregate import AggregateTF

