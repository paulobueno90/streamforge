"""
StreamForge Base Module.

This module contains the core framework components for data ingestion:
- Runner: Orchestrates the ingestion pipeline
- WebsocketHandler: Manages WebSocket connections
- DataInput: Stream configuration
- DataEmitter: Output interface
- Processors: Data processing logic
- Normalizers: Data standardization
"""

from .stream_input import DataInput
from .runner import Runner
from .ws import WebsocketHandler, SubscribeError
from .emitters.base import DataEmitter, EmitterHolder
from .models import BaseKlineBuffer, BaseAggregateTF, WarmupConfigurationError

__all__ = [
    # Configuration
    "DataInput",
    
    # Core classes
    "Runner",
    "WebsocketHandler",
    "SubscribeError",
    
    # Emitters
    "DataEmitter",
    "EmitterHolder",
    
    # Models
    "BaseKlineBuffer",
    "BaseAggregateTF",
    "WarmupConfigurationError",
]
