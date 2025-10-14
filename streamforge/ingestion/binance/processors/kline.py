import asyncio
import logging
import bisect
from datetime import datetime

from .aggregate import AggregateTF
from .util import check_offset, config_aggregation
from streamforge.base.stream_input import DataInput
from streamforge.base.models import BaseKlineBuffer
from streamforge.base.normalize.ohlc.models.timeframes import TIMEFRAME_CLASS_MAP, TIMEFRAME_BUFFER_SIZE_MAP
from streamforge.base.normalize.ohlc.models.candle import Kline
from streamforge.base.normalize.ohlc.processor import OHLCDatNormalizer
from ..api.api import BinanceAPI
from streamforge.ingestion.binance.api.api import binance_api


from streamforge.base.data_container.ohlc import CandleData, get_start_timestamp,filter_timestamp
from streamforge.base.data_processor.ohlc import CandleProcessor
from streamforge.base.api import BaseCandleAPI

from streamforge.ingestion.binance.normalizers.normalizer import BinanceNormalizers
from streamforge.ingestion.binance.normalizers.ohlc import KlineNormalizer
from streamforge.base.normalize.normalize import Normalizer
from streamforge.base.data_processor.aggregate import BaseAggregateTF, AggregateTF


class KlineData(BaseKlineBuffer):

    source = "binance"
    _kline_normalizer = KlineNormalizer()

    def __init__(self, symbol, timeframe, max_len, warmup_active=True):
        self._symbol = symbol
        self._timeframe = TIMEFRAME_CLASS_MAP[timeframe]
        self._buffer = list()
        self._max_len = max_len
        self._current_size = 0
        self._is_full = False
        self.offset = self._timeframe.offset
        self._warmup_active = warmup_active

    def _is_duplicate(self, data):
        insert_index_left = bisect.bisect_left(self._buffer, data)
        insert_index_right = bisect.bisect_right(self._buffer, data)

        if self._current_size == 0:
            return False
        elif (insert_index_right > (self._current_size - 1)) and (self._buffer[self._current_size - 1] != data):
            return False
        elif (insert_index_left == 0) and (self._current_size > 1) and (self._buffer[insert_index_left + 1] == data):
            return True
        elif (self._buffer[insert_index_left] == data) or (self._buffer[insert_index_right] == data):
            return True
        else:
            return False

    def _handle_size(self):
        if self._is_full:
            if self._current_size > self._max_len:
                for _ in range(self._current_size - self._max_len):
                    self._buffer.pop(0)
                    self._current_size -= 1

    def add_data(self, data):
        index = bisect.bisect_left(self._buffer, data)
        if index < len(self._buffer) and self._buffer[index] == data:
            self._buffer[index] = data
        else:
            bisect.insort_left(self._buffer, data)
            self._current_size += 1

        if not self._is_full:
            self._is_full = True if self._current_size >= self._max_len else False
        else:
            self._handle_size()

    def _insert_klines(self, klines):
        timestamp_now = int(datetime.utcnow().timestamp())

        for kline_data in klines:
            if timestamp_now >= kline_data.end_ts:
                self.add_data(data=kline_data)

    async def __fetch_klines_data(self):
        data = await binance_api.fetch_kline(self._symbol, self._timeframe)
        klines = (self._kline_normalizer.api(item, self._symbol, self._timeframe.string_tf) for sublist in data for item in sublist)
        return klines

    async def warmup_generator(self):
        logging.info(f"Symbol: {self._symbol} | Timeframe: {self._timeframe.string_tf} | WARM-UP start")

        klines = await self.__fetch_klines_data()
        timestamp_now = int(datetime.now().timestamp())

        for kline_data in klines:
            normalized_ts = (kline_data.end_ts // 1000)
            if timestamp_now >= normalized_ts:
                self.add_data(data=kline_data)
                yield kline_data

        logging.info(f"Symbol: {self._symbol} | Timeframe: {self._timeframe.string_tf} | WARM-UP OK")

    async def warmup_data(self):

        logging.info(f"Symbol: {self._symbol} | Timeframe: {self._timeframe.string_tf} | WARM-UP start")

        klines = await self.__fetch_klines_data()
        self._insert_klines(klines=klines)

        logging.info(f"Symbol: {self._symbol} | Timeframe: {self._timeframe.string_tf} | WARM-UP OK")
        return None

    def check_data(self):
        if check_offset(self._buffer, offset=self.offset):
            logging.warning(f"Data Missing for {self._symbol}-{self._timeframe}")

    @property
    def data(self):
        return self._buffer

    @property
    def symbol(self):
        return self._symbol

    @property
    def timeframe(self):
        return self._timeframe

    @property
    def size(self):
        return len(self._buffer)

    @property
    def warmup_active(self):
        return self._warmup_active


class KlineBinance:
    source = "binance"

    def __init__(
            self,
            stream_input,
            aggregate_class=AggregateTF,
            warmup_active: bool = True,
            warmup_emit: bool = True,
    ):
        self._stream_input = stream_input
        self._data_map = dict()
        self._warmup_active = warmup_active
        self._warmup_emit = warmup_emit

        self._agg = config_aggregation(streams_input=stream_input,
                                       aggregate_cls=aggregate_class,
                                       warmup_active=self._warmup_active)

        self._process_streams_input(streams_input=stream_input)

    def _process_single_input(self, stream_input):
        for symbol in stream_input.symbols:
            tf = stream_input.timeframe
            max_len = TIMEFRAME_BUFFER_SIZE_MAP[tf]
            self._data_map[f"{symbol.upper()}-{tf}"] = KlineData(symbol=symbol, timeframe=tf, max_len=max_len)

            if self._agg is not None:
                for timeframe in self._agg.target_timeframes:
                    self._data_map[f"{symbol.upper()}-{timeframe.string_tf}"] = KlineData(
                        symbol=symbol,
                        timeframe=timeframe.string_tf,
                        max_len=TIMEFRAME_BUFFER_SIZE_MAP[timeframe.string_tf],
                    )

    def _process_streams_input(self, streams_input):
        if isinstance(streams_input, DataInput):
            self._process_single_input(stream_input=streams_input)
        elif isinstance(streams_input, list):
            for s_input in streams_input:
                self._process_single_input(stream_input=s_input)
        else:
            raise TypeError(f"'streams_input' expects List[DataInput] or DataInput, {type(streams_input)} provided.")

    def _insert_data(self, kline_data: Kline):
        self._data_map[kline_data.map_key()].add_data(data=kline_data)

    def _process_aggregation(self, timestamp, base_data):

        for tf in self._agg.timeframes_to_aggregate(timestamp=timestamp):

            new_kline_data = self._agg.aggregate(base_data=base_data, timeframe=tf, ref_timestamp=timestamp)

            self._insert_data(kline_data=new_kline_data)

            logging.info(f"Data Aggregated: {new_kline_data}")

            yield new_kline_data

    async def emit_warmup(self):
        for data_container in self._data_map.values():
            async for data in data_container.warmup_generator():
                yield data

    async def warmup(self):

        tasks = [data_container.warmup_data() for data_container in self._data_map.values() if data_container.warmup_active]
        await asyncio.gather(*tasks)

    async def process_data(self, data: Kline):

        self._insert_data(kline_data=data)
        yield data

        if self._agg is not None:
            base_data = self._data_map[data.map_key()]
            for agg_kline_data in self._process_aggregation(
                    timestamp=data.end_ts,
                    base_data=base_data
            ):
                yield agg_kline_data


class BinanceCandleData(CandleData):

    def __init__(self,
                 source: str,
                 symbol: str,
                 timeframe: str,
                 max_len: int,
                 normalizer: Normalizer = KlineNormalizer(),
                 exchange_api: BaseCandleAPI = binance_api,
                 warmup_active: bool = True,
                 emit_active: bool = True
                 ):

        super().__init__("Binance", symbol, timeframe, max_len, normalizer, exchange_api, warmup_active, emit_active)

    async def _fetch_candle_data(self):
        data = await self._exchange_api.fetch_kline(self._symbol, self._timeframe)
        klines = (self._normalizer.api(data=item, symbol=self._symbol, timeframe=self._timeframe.string_tf) for sublist in
                  data for item in sublist)
        return klines


class BinanceCandleProcessor(CandleProcessor):

    def __init__(self,
                 stream_input: DataInput,
                 data_container_class: CandleData = BinanceCandleData,
                 source: str = "Binance",
                 aggregate_class: BaseAggregateTF = AggregateTF,
                 warmup_active: bool = True,
                 warmup_emit: bool = True,
                 emit_only_closed_candles: bool = True,
                 force_5m_required: bool = False,
                 candle_closed_check: bool = False
                 ):

        super().__init__(stream_input, source, data_container_class, aggregate_class, warmup_active, warmup_emit,
                         emit_only_closed_candles, force_5m_required, candle_closed_check)


