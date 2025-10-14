from typing import List, Dict, Any

from streamforge.base.data_container.ohlc import CandleData, get_start_timestamp,filter_timestamp
from streamforge.base.data_processor.ohlc import CandleProcessor
from streamforge.base.normalize.normalize import Normalizer
from streamforge.base.api import BaseCandleAPI
from streamforge.base.stream_input import DataInput
from streamforge.base.normalize.ohlc.models.timeframes import BaseTimeframe
from streamforge.base.data_processor.aggregate import BaseAggregateTF, AggregateTF

from streamforge.ingestion.okx.normalizers.ohlc import KlineNormalizer
from streamforge.ingestion.okx.api.ohlc import OkxCandleApi


def iterate_okx_api_data(data: List[Dict[str, List[Any]]], start_timestamp: int):
    for api_response in data:
        for candle_data in filter_timestamp(api_response["data"], timestamp=start_timestamp, handle_timestamp=True):
            yield candle_data


class OkxCandleData(CandleData):

    def __init__(self, source: str, symbol: str, timeframe: str, max_len: int, normalizer: Normalizer = KlineNormalizer(),
                 exchange_api: BaseCandleAPI = OkxCandleApi(), warmup_active: bool = True, emit_active: bool = True):

        super().__init__("OKX", symbol, timeframe, max_len, normalizer, exchange_api, warmup_active, emit_active)

    async def _fetch_candle_data(self):

        start_timestamp = get_start_timestamp()
        data = await self._exchange_api.fetch_candles(self._symbol, self._timeframe)

        return [self._normalizer.api(
                data=ohlc_data,
                symbol=self._symbol,
                timeframe=self._timeframe
                ) for ohlc_data in iterate_okx_api_data(data=data, start_timestamp=start_timestamp)]


class OkxCandleProcessor(CandleProcessor):

    def __init__(self, stream_input: DataInput, data_container_class: CandleData = OkxCandleData, source: str = "okx",
                 aggregate_class: BaseAggregateTF = AggregateTF, warmup_active: bool = True, warmup_emit: bool = True,
                 emit_only_closed_candles: bool = True, force_5m_required: bool = False,
                 candle_closed_check: bool = False):

        super().__init__(stream_input, source, data_container_class, aggregate_class, warmup_active, warmup_emit,
                         emit_only_closed_candles, force_5m_required, candle_closed_check)




