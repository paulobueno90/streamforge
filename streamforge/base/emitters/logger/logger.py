import asyncio
import logging
from ..base import DataEmitter


class Logger(DataEmitter):

    EMITTER_TYPE = "logging"
    EMITTER = "logger"

    DATA_MODEL = None

    def __init__(self, prefix=""):
        self.prefix = prefix

    def register_map(self, columns_map: dict[str, str]):
        pass

    def set_model(self, datamodel):
        pass

    async def emit(self, data):
        logging.info(f"{self.prefix} | Received Data | {data}")

    async def connect(self):
        pass

    async def close(self):
        pass

