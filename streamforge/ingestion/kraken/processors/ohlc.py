from streamforge.base.stream_input import DataInput

from streamforge.base.data_container.ohlc import CandleData
from streamforge.base.data_processor.ohlc import CandleProcessor
from streamforge.base.api import BaseCandleAPI
from streamforge.base.normalize.normalize import Normalizer
from streamforge.base.data_processor.aggregate import BaseAggregateTF, AggregateTF

from streamforge.ingestion.kraken.api.api import kraken_api
from streamforge.ingestion.kraken.normalizers.ohlc import KlineNormalizer


class KrakenCandleData(CandleData):

    def __init__(self,
                 source: str,
                 symbol: str,
                 timeframe: str,
                 max_len: int,
                 normalizer: Normalizer = KlineNormalizer(),
                 exchange_api: BaseCandleAPI = kraken_api,
                 warmup_active: bool = True,
                 emit_active: bool = True
                 ):

        super().__init__("Kraken", symbol, timeframe, max_len, normalizer, exchange_api, warmup_active, emit_active)

    async def _fetch_candle_data(self):
        data = await self._exchange_api.fetch_kline(self._symbol, self._timeframe)

        klines = (self._normalizer.api(data=candle_data, symbol=self._symbol, timeframe=self._timeframe) for candle_data in data)
        return klines


class KrakenCandleProcessor(CandleProcessor):

    def __init__(self,
                 stream_input: DataInput,
                 data_container_class: CandleData = KrakenCandleData,
                 source: str = "Kraken",
                 aggregate_class: BaseAggregateTF = AggregateTF,
                 warmup_active: bool = True,
                 warmup_emit: bool = True,
                 emit_only_closed_candles: bool = True,
                 force_5m_required: bool = True,
                 candle_closed_check: bool = True
                 ):

        super().__init__(stream_input, source, data_container_class, aggregate_class, warmup_active, warmup_emit,
                         emit_only_closed_candles, force_5m_required, candle_closed_check)
