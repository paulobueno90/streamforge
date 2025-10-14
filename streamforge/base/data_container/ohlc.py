import asyncio
import logging
import bisect
from datetime import datetime, timezone
from abc import ABC, abstractmethod
from streamforge.base.data_container.util import check_offset, get_start_timestamp
from streamforge.base.normalize.ohlc.models.timeframes import TIMEFRAME_CLASS_MAP, BaseTimeframe
from streamforge.base.normalize.ohlc.models.candle import Kline
from streamforge.base.normalize.normalize import Normalizer
from streamforge.base.api import BaseCandleAPI
from streamforge.base.data_container.util import filter_timestamp, timestamp_ms_to_seconds


class CandleData(ABC):

    def __init__(
            self,
            source: str,
            symbol: str,
            timeframe: str,
            max_len: int,
            normalizer: Normalizer,
            exchange_api: BaseCandleAPI,
            warmup_active: bool=True,
            emit_active: bool=True


    ):
        self._source = source
        self._symbol = symbol
        self._timeframe = TIMEFRAME_CLASS_MAP[timeframe]
        self._buffer = list()
        self._max_len = max_len
        self._current_size = 0
        self._is_full = False
        self.offset = self._timeframe.offset
        self._warmup_active = warmup_active
        self._emit_active = emit_active
        self._recent_ohlc = None
        self._normalizer = normalizer
        self._exchange_api = exchange_api


    @abstractmethod
    async def _fetch_candle_data(self):
        pass
        # start_timestamp = get_start_timestamp()
        # data = await self._exchange_api.fetch_candles(self._symbol, self._timeframe)
        #
        # return data
        #
        # # return [self._normalizer.api(
        # #         kline=ohlc_data,
        # #         symbol=self._symbol,
        # #         timeframe=self._timeframe
        # #         ) for ohlc_data in filter_timestamp(ohlc_data_array=data, timestamp=start_timestamp)]

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

    def _insert_data(self, data: Kline):

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

    def _update_recent_ohlc(self, data: Kline):
        self._recent_ohlc = data

    def add_data(self, data: Kline):

        if (data > self._recent_ohlc) or (data == self._recent_ohlc):
            self._update_recent_ohlc(data=data)

        self._insert_data(data=data)

    def _insert_candles(self, candles):
        timestamp_now = int(datetime.now(timezone.utc).timestamp())
        for candle_data in candles:
            if timestamp_now >= candle_data.end_ts:
                self.add_data(data=candle_data)

    async def warmup_generator(self):
        logging.info(f"{self._source:<{10}} | Symbol: {self._symbol} | Timeframe: {self._timeframe.string_tf} | WARM-UP start")

        candles = await self.__fetch_candle_data()

        timestamp_now = get_start_timestamp()

        for candle_data in candles:
            normalized_ts = candle_data.end_ts
            if timestamp_now >= normalized_ts:
                self.add_data(data=candle_data)
                yield candle_data

        logging.info(f"{self._source:<{10}} | Symbol: {self._symbol} | Timeframe: {self._timeframe.string_tf} | WARM-UP OK")

    async def warmup_data(self):
        logging.info(f"{self._source:<{10}} | Symbol: {self._symbol} | Timeframe: {self._timeframe.string_tf} | WARM-UP start")
        candles = await self._fetch_candle_data()
        self._insert_candles(candles=candles)

        logging.info(f"{self._source:<{10}} | Symbol: {self._symbol} | Timeframe: {self._timeframe.string_tf} | WARM-UP OK")
        return None

    def check_data(self):
        if check_offset(self._buffer, offset=self.offset):
            logging.warning(f"{self._source:<{10}} | Data Missing for {self._symbol}-{self._timeframe}")

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
    def counter(self):
        return self._current_size

    @property
    def warmup_active(self):
        return self._warmup_active

    @property
    def recent_ohlc(self):
        return self._recent_ohlc
