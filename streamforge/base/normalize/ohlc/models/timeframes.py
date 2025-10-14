from dataclasses import dataclass


class BaseTimeframe:
    string_tf: str
    tf: str
    offset: int

    def __eq__(self, other):
        return self.offset == other.offset

    def __gt__(self, other):
        return self.offset > other.offset

    def __lt__(self, other):
        return self.offset < other.offset

    def __mod__(self, other):
        return self.offset % other.offset


@dataclass
class TIMEFRAME_1M(BaseTimeframe):
    string_tf: str = "1m"
    tf: str = "1"
    offset: int = 60


@dataclass
class TIMEFRAME_5M(BaseTimeframe):
    string_tf: str = "5m"
    tf: str = "5"
    offset: int = 60 * 5


@dataclass
class TIMEFRAME_15M(BaseTimeframe):
    string_tf: str = "15m"
    tf: str = "15"
    offset: int = 60 * 15


@dataclass
class TIMEFRAME_30M(BaseTimeframe):
    string_tf: str = "30m"
    tf: str = "30"
    offset: int = 60 * 30


@dataclass
class TIMEFRAME_1H(BaseTimeframe):
    string_tf: str = "1h"
    tf: str = "60"
    offset: int = 60 * 60


@dataclass
class TIMEFRAME_4H(BaseTimeframe):
    string_tf: str = "4h"
    tf: str = "240"
    offset: int = 60 * 240


@dataclass
class TIMEFRAME_1D(BaseTimeframe):
    string_tf: str = "1d"
    tf: str = "1440"
    offset: int = 60 * 1440


TIMEFRAME_CLASS_MAP = {
    "1m": TIMEFRAME_1M(),
    "5m": TIMEFRAME_5M(),
    "15m": TIMEFRAME_15M(),
    "30m": TIMEFRAME_30M(),
    "1h": TIMEFRAME_1H(),
    "4h": TIMEFRAME_4H(),
    "1d": TIMEFRAME_1D()
}

TIMEFRAME_BUFFER_SIZE_MAP = {
    "1m": int(1440 / 1),
    "5m": int(1440 / 5),
    "15m": int(1440 / 15),
    "30m": int(1440 / 30),
    "1h": int(1440 / 60),
    "4h": int(1440 / 240),
    "1d": int(1440 / 1440)
}

TIMEFRAME_INTERVAL_MAP = {
    1: '1m',
    5: '5m',
    10: '10m',
    15: '15m',
    30: '30m',
    60: '1h',
    240: '4h',
    1440: '1d'
}