import asyncio
from abc import ABC, abstractmethod
from typing import Type, Optional, Dict, Union, List, ClassVar, AnyStr, Any
from streamforge.base.normalize.ohlc.models.candle import Kline
from streamforge.base.data_container.ohlc import CandleData
from streamforge.base.ws import DataInput
from streamforge.base.data_processor.aggregate import BaseAggregateTF, AggregateTF
from streamforge.base.normalize.ohlc.models.timeframes import TIMEFRAME_BUFFER_SIZE_MAP, BaseTimeframe
from streamforge.base.api import BaseCandleAPI
import logging


class CandleProcessor2(ABC):

    @abstractmethod
    async def process_data(self, data: Kline):
        pass


class WarmupConfigurationError(Exception):
    """Exception raised when warmup configuration is invalid for aggregation"""
    pass


TIMEFRAMES_5M_REQUIRED_AGG = {"15m", "30m", "1h", "4h", "1d"}


class CandleProcessor(ABC):

    def __init__(
            self,
            stream_input: DataInput,
            source: str,
            data_container_class: CandleData,
            aggregate_class: BaseAggregateTF = AggregateTF,
            warmup_active: bool = True,
            warmup_emit: bool = True,
            emit_only_closed_candles: bool = True,
            force_5m_required: bool = False,
            candle_closed_check: bool = False,

    ):
        self.source = source.lower()
        self._stream_input = stream_input
        self._container_class = data_container_class
        self._data_map: dict[str, CandleData] = dict()

        # Boolean Variables
        self._warmup_active = warmup_active
        self._warmup_emit = warmup_emit
        self._emit_only_closed_candles = emit_only_closed_candles
        self._force_5m_required = force_5m_required
        self._requires_candle_closed_check = candle_closed_check

        self._agg = self.__config_aggregation(streams_input=stream_input,
                                              aggregate_cls=aggregate_class,
                                              warmup_active=self._warmup_active)

        self._process_streams_input(streams_input=stream_input)

    def set_warmup_active(self, value: bool):
        self._warmup_active = value

    def set_warmup_emit(self, value: bool):
        self._warmup_emit = value

    @staticmethod
    def __check_aggregation_setup(warmup_active, streams_input):
        """Check if aggregation setup is valid"""
        if streams_input.aggregate_list:
            if not warmup_active:
                raise WarmupConfigurationError()
            else:
                return True
        else:
            return False

    @staticmethod
    def __get_map_key(base_tf: str, timeframe: BaseTimeframe, datapoint: Kline):

        map_key = datapoint.map_key()
        if (base_tf == "1m") and (timeframe.string_tf in TIMEFRAMES_5M_REQUIRED_AGG):
            return map_key.replace("1m", "5m")
        else:
            return map_key

    def __config_aggregation(self, streams_input, aggregate_cls, warmup_active):
        """Configure aggregation based on stream input"""
        if self.__check_aggregation_setup(warmup_active=warmup_active, streams_input=streams_input):

            aggregate_list, force_5m = self.__handle_aggregate_list(
                base_tf=streams_input.timeframe,
                aggregate_list=streams_input.aggregate_list
            )

            agg_obj = aggregate_cls(
                source=self.source,
                timeframe=streams_input.timeframe,
                target_timeframes=aggregate_list,
                tf_5m_force_included=force_5m
            )

            if agg_obj.is_empty:
                logging.info(f"{self.source.title():<{10}} | Aggregation "
                             f"Could not be initiated for timeframes: {streams_input.aggregate_list}")
                logging.info(f"{self.source.title():<{10}} | Aggregation Deactivated")
                return None
            else:
                logging.info(f"{self.source.title():<{10}} | Aggregation Activated for: "
                             f"{[tf.string_tf for tf in agg_obj.target_timeframes]}")
                return agg_obj
        else:
            logging.info("Aggregation Deactivated")
            return None

    def __handle_aggregate_list(self, base_tf: str, aggregate_list: List[str]):

        force_5m = False

        agg_set = set(aggregate_list)
        if base_tf == "1m":
            if (agg_set & TIMEFRAMES_5M_REQUIRED_AGG) and ("5m" not in agg_set):
                aggregate_list.insert(0, "5m")
                force_5m = True
                logging.warning(f"{self.source.title():<{10}} | Timeframe '5 minutes' included in warmup and processing "
                                "because '1 minute' warmup might have missing data due to API limitations.")

        return aggregate_list, force_5m

    def _process_input(self, stream_input: DataInput):
        for symbol in stream_input.symbols:
            tf = stream_input.timeframe
            max_len = TIMEFRAME_BUFFER_SIZE_MAP[tf]
            self._data_map[f"{symbol.upper()}-{tf}"] = self._container_class(source= self.source,
                                                                     symbol=symbol,
                                                                     timeframe=tf,
                                                                     max_len=max_len)

            if self._agg is not None:
                for timeframe in self._agg.target_timeframes:
                    buffer_input = dict(
                        source=self.source,
                        symbol=symbol,
                        timeframe=timeframe.string_tf,
                        max_len=TIMEFRAME_BUFFER_SIZE_MAP[timeframe.string_tf],
                        emit_active=True
                    )
                    if self._agg.tf_5m_force_included and (timeframe.string_tf == "5m"):
                        buffer_input.update(emit_active=False)

                    self._data_map[f"{symbol.upper()}-{timeframe.string_tf}"] = self._container_class(**buffer_input)

    def _process_streams_input(self, streams_input: Union[DataInput, List[DataInput]]):
        if isinstance(streams_input, DataInput):
            self._process_input(stream_input=streams_input)
        elif isinstance(streams_input, list):
            for s_input in streams_input:
                self._process_input(stream_input=s_input)
        else:
            raise TypeError(f"'streams_input' expects List[DataInput] or DataInput, {type(streams_input)} provided.")

    def add_data(self, ohlc_data: Kline):
        self._data_map[ohlc_data.map_key()].add_data(data=ohlc_data)

    def _get_data_container(self, ohlc_data: Kline):
        return self._data_map[ohlc_data.map_key()]

    def _candle_check_handling(self, data: Kline):

        last_closed_candle = None

        if self._requires_candle_closed_check:
            data_container = self._get_data_container(ohlc_data=data)
            is_new_candle = data > data_container.recent_ohlc

            last_closed_candle = None
            if is_new_candle:
                last_closed_candle = data_container.recent_ohlc
                last_closed_candle.is_closed = True

        else:
            if data.is_closed:
                is_new_candle = True
                last_closed_candle = data
            else:
                is_new_candle = False

        last_not_null = last_closed_candle is not None

        self.add_data(ohlc_data=data)

        return is_new_candle, last_closed_candle, last_not_null

    async def emit_warmup(self):
        for data_container in self._data_map.values():
            async for data in data_container.warmup_generator():
                yield data

    async def warmup(self):
        tasks = [data_container.warmup_data() for data_container in self._data_map.values() if
                 data_container.warmup_active]
        await asyncio.gather(*tasks)

    def _process_aggregation(self, last_datapoint: Kline):
        timestamp = last_datapoint.end_ts
        base_tf = last_datapoint.timeframe

        for tf in self._agg.timeframes_to_aggregate(timestamp=timestamp):

            map_key = self.__get_map_key(base_tf=base_tf, timeframe=tf, datapoint=last_datapoint)
            base_data = self._data_map[map_key]
            if not (base_data.counter >= (tf.offset // base_data.timeframe.offset)):
                continue

            new_ohlc_data = self._agg.aggregate(base_data=base_data, timeframe=tf, ref_timestamp=timestamp)

            if new_ohlc_data is None:
                continue

            self.add_data(ohlc_data=new_ohlc_data)
            logging.info(f"{self.source.title():<{10}} | Data Aggregated: {new_ohlc_data}")

            if (tf.string_tf == "5m") and self._agg.tf_5m_force_included:
                continue
            else:
                yield new_ohlc_data

    async def process_data(self, data: Union[Kline, List[Kline]]):

        is_new_candle, last_closed_candle, last_not_null = self._candle_check_handling(data=data)

        if not self._emit_only_closed_candles:
            yield data

        if is_new_candle:
            if self._emit_only_closed_candles and last_not_null:
                yield last_closed_candle

            if self._agg is not None:
                if last_not_null:
                    for agg_ohlc_data in self._process_aggregation(last_datapoint=last_closed_candle):
                        yield agg_ohlc_data
