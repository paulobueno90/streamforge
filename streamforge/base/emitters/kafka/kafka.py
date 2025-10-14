import orjson
import logging
from typing import Optional, Dict, Type
from ..base import DataEmitter
from aiokafka import AIOKafkaProducer
from pydantic import BaseModel

from ..util import transform


class KafkaEmitter(DataEmitter):
    EMITTER_TYPE = "stream"
    EMITTER = "kafka"

    def __init__(
        self,

        topic: str,
        bootstrap_servers: str = "localhost:9092",
        key_serializer: Optional[callable] = None,
        value_serializer: Optional[callable] = None,
        name: str = EMITTER,
    ):
        self.topic = topic
        self.bootstrap_servers = bootstrap_servers
        self.key_serializer = key_serializer
        self.value_serializer = value_serializer or (lambda v: orjson.dumps(v))
        self.producer: Optional[AIOKafkaProducer] = None
        self._columns_map: Optional[Dict[str, str]] = None
        self._dump_include: Optional[set[str]] = None
        self.DATA_MODEL: Optional[Type[BaseModel]] = None

        self.name = name

        logging.info("KafkaEmitter initialized.")

    def set_model(self, model: Type[BaseModel]):
        """Set the canonical Pydantic model for this emitter."""
        self.DATA_MODEL = model

    def register_map(self, columns_map: Dict[str, str]):
        """Optional field mapping for output."""
        self._columns_map = columns_map
        self._dump_include = set(columns_map.keys())

    async def connect(self):
        """Initialize the Kafka producer."""
        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            key_serializer=self.key_serializer,
            value_serializer=self.value_serializer,
        )
        await self.producer.start()
        logging.info("Kafka producer started successfully.")

    async def emit(self, data: BaseModel, key: Optional[str] = None):
        """Send a single message to Kafka."""
        if not self.producer:
            raise RuntimeError("Kafka producer not connected. Call `connect()` first.")

        # Filter / map fields
        obj_data = data.model_dump(include=self._dump_include)
        if self._columns_map:
            obj_data = transform(obj_data, self._columns_map)

        try:
            await self.producer.send_and_wait(self.topic, value=obj_data, key=key.encode() if key else None)
            logging.info(f"Emitted Data | Emitter: {self.name} | topic:'{self.topic}' | data: {obj_data}")
        except Exception as e:
            logging.error(f"Error sending message to Kafka: {e}")

    async def close(self):
        """Close the Kafka producer."""
        if self.producer:
            await self.producer.stop()
            logging.info("Kafka producer stopped.")