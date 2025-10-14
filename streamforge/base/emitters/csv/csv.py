import logging
import pandas as pd
from pathlib import Path
from typing import Optional, Callable, Dict, Any, Union, List

from ..base import DataEmitter
from ..util import transform


class CSVEmitter(DataEmitter):

    EMITTER_TYPE = "file writer"
    EMITTER = "csv"
    DATA_MODEL = None

    def __init__(
            self,
            source: str,
            symbol: str,
            timeframe: str,
            name: str = EMITTER,
            file_path: Optional[str] = None,
            transformer_function: Callable[[Dict[str, Any]], dict] = None
    ):
        self.source = source
        self.symbol = symbol
        self.timeframe = timeframe
        self.name = name
        self._custom_transformer = transformer_function
        self.file_path = file_path
        logging.info("CSVWriter initialized.")

    def set_transformer(self, transformer_function: Callable[[Dict[str,Any]], dict], inplace=False):
        self._custom_transformer = transformer_function
        if inplace:
            return None
        else:
            return self

    def set_file_path(self, file_path: str, inplace=True):
        self.file_path = file_path
        if inplace:
            return None
        else:
            return self

    def transform(self, data: dict):
        if self._custom_transformer is None:
            return data
        else:
            return self._custom_transformer(data)

    async def _emit_single(self, data: Dict[str,Any]):
        """Inserts data using a SQLAlchemy ORM model."""

        try:
            batch = [self.transform(data=data)]
            df = pd.DataFrame(batch)
            if Path(self.file_path).exists():
                df.to_csv(self.file_path, mode="a", header=not Path(self.file_path).exists(), index=False)
            else:
                df.to_csv(self.file_path, index=False)

            logging.info(f"Emitted Data | Emitter: {self.name} | {batch[0]}.")
        except Exception as e:
            logging.info(f"Error inserting data: {e}")

    async def emit_bulk(self, data_list: list[Dict[str, Any]]):

        if not data_list:
            logging.warning("Empty list passed to emit_bulk.")
            return

        try:
            batch = (self.transform(data=data) for data in data_list)
            df = pd.DataFrame(batch)

            df.to_csv(self.file_path, mode="a", header=not Path(self.file_path).exists(), index=False)
            logging.info(f"Inserted {len(df)} rows | File: {self.file_path} | First Row: {df.iloc[0].to_dict()}")
        except Exception as e:
            logging.error(f"Error inserting bulk data: {e}")

    async def emit(self, data: Union[Dict[str, Any], List[Dict[str, Any]]]):
        if isinstance(data, list):
            await self._emit_bulk(data=data)
        else:
            await self._emit_single(data=data)

    def register_map(self, columns_map: dict[str, str]):
        pass

    def set_model(self, datamodel):
        pass

    async def connect(self):
        pass

    async def close(self):
        pass