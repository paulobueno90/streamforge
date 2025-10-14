"""
Data emitter base module.

This module provides abstract base classes for outputting processed data to
various destinations (files, databases, message queues, etc.).
"""

from typing import Optional, Dict, Type, Union, Any
from abc import ABC, abstractmethod
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from pydantic import BaseModel

Base = declarative_base()


class DataEmitter(ABC):
    """
    Abstract base class for data output emitters.
    
    DataEmitter defines the interface for outputting processed market data
    to various destinations. Implementations include CSV files, PostgreSQL
    databases, Kafka streams, and logging outputs.
    
    Attributes:
        EMITTER_TYPE: Category of emitter (e.g., 'database', 'file writer', 'stream')
        EMITTER: Specific emitter name (e.g., 'postgresql', 'csv', 'kafka')
        DATA_MODEL: Optional data model for structured outputs
        
    Examples:
        >>> # Use concrete implementations
        >>> emitter = CSVEmitter(file_path="btc_data.csv")
        >>> await emitter.connect()
        >>> await emitter.emit(kline_data)
        >>> await emitter.close()
    
    Note:
        Subclasses must implement all abstract methods: register_map,
        set_model, emit, connect, and close.
    """

    EMITTER_TYPE = str
    EMITTER = str

    DATA_MODEL = None

    @abstractmethod
    def register_map(self, columns_map: dict[str, str]):
        pass

    @abstractmethod
    def set_model(self, datamodel):
        self.DATA_MODEL = datamodel

    @abstractmethod
    async def emit(self, data):
        pass

    @abstractmethod
    async def connect(self):
        pass

    @abstractmethod
    async def close(self):
        pass


class EmitterHolder:
    """
    Container for managing multiple data emitters.
    
    EmitterHolder allows registering and coordinating multiple output emitters,
    enabling simultaneous output to different destinations (e.g., save to CSV
    while also writing to PostgreSQL and streaming to Kafka).
    
    Attributes:
        EMITTERS_MAP: Dictionary mapping emitter names to emitter instances
        
    Examples:
        >>> holder = EmitterHolder()
        >>> holder.add(CSVEmitter("data.csv"))
        >>> holder.add(PostgresEmitter(connection_string="..."))
        >>> await holder.connect()
        >>> await holder.emit(kline_data)  # Outputs to all emitters
        
    Note:
        The EmitterHolder automatically calls connect() on all emitters
        and manages their lifecycle.
    """

    EMITTERS_MAP = dict()

    def add(self, emitter: DataEmitter, data_model: Optional[Union[BaseModel, Base]] = None, columns_map: dict[str, str] = None):
        """
        Register an emitter for data output.
        
        Args:
            emitter: DataEmitter instance to register
            data_model: Optional data model (SQLAlchemy Base or Pydantic BaseModel)
            columns_map: Optional mapping of field names for custom schemas
        """
        self.EMITTERS_MAP[emitter.EMITTER] = emitter
        if data_model is not None:
            self.EMITTERS_MAP[emitter.EMITTER].set_model(datamodel=data_model)
        if columns_map is not None:
            self.EMITTERS_MAP[emitter.EMITTER].register_map(columns_map)

    async def connect(self):
        """Connect all registered emitters."""
        if self.EMITTERS_MAP:
            for emitter in self.EMITTERS_MAP.values():
                await emitter.connect()

    async def emit(self, data):
        """
        Emit data to all registered emitters.
        
        Args:
            data: Data to emit (typically a Kline or other processed data object)
        """
        if self.EMITTERS_MAP:
            for emitter_name, emitter in self.EMITTERS_MAP.items():
                await emitter.emit(data=data)

    async def emit_bulk(self, data: Any):
        """
        Emit multiple data items in bulk for efficiency.
        
        Args:
            data: List of data items to emit
            
        Note:
            Not all emitters support bulk operations. Falls back to
            individual emits for unsupported emitters.
        """
        for emitter in self.EMITTERS_MAP.values():
            if emitter.EMITTER == "postgresql":
                await emitter.emit_orm_bulk(data_list=data)
            elif emitter.EMITTER == "csv":
                await emitter.emit_bulk(data_list=data)
            else:
                pass

    @property
    def empty(self) -> bool:
        """Check if any emitters are registered."""
        return len(self.EMITTERS_MAP) == 0