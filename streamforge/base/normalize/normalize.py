"""
Data normalization base classes.

This module provides abstract base classes for normalizing exchange-specific
data formats into standardized models (like Kline).
"""

from abc import ABC, abstractmethod
from typing import Union, Dict, Any, List, overload
from streamforge.base.normalize.ohlc.models.candle import Kline


class Normalizer(ABC):
    """
    Abstract base class for data normalizers.
    
    Normalizers convert exchange-specific data formats into standardized
    StreamForge models, handling field mapping, data type conversion, and
    validation.
    
    Note:
        Each exchange has its own normalizer implementation that handles
        the specific quirks of that exchange's data format.
    """

    @abstractmethod
    def ws(self, data: Dict[str, Any]) -> Union[Kline]:  # Might add other formats
        pass

    @abstractmethod
    def api(self, data: Union[Dict[str, Any], List], **kwargs):
        pass


class GeneralNormalizers(ABC):

    def __init__(self, normalizers_map: Dict[str, Normalizer]):
        self._normalizers_map = normalizers_map

    @abstractmethod
    def ws(self, data: Dict[str, Any]) -> Union[Kline]: # Might add other formats
        pass

    @abstractmethod
    def api(self, data: Union[Dict[str, Any], List]):
        pass

