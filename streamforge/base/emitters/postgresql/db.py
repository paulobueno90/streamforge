import logging
from typing import Optional, Callable, Dict, Any, Union
from sqlalchemy.sql import text
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.inspection import inspect
from pydantic import BaseModel
from ..base import DataEmitter
from ..util import transform
from streamforge.base.normalize.ohlc.models.candle import Kline

Base = declarative_base()


class PostgresEmitter(DataEmitter):
    EMITTER_TYPE = "database"
    EMITTER = "postgresql"
    DATA_MODEL = None

    def __init__(
            self,
            name: str = EMITTER,
            url: Optional[str] = None,
            host: Optional[str] = None,
            dbname: Optional[str] = None,
            user: Optional[str] = None,
            password: Optional[str] = None,
            port: int = 5432,
            upsert: bool = False,
            index_elements: Optional[list[str]] = None,
            transformer: Callable[[Dict[str, Any]], dict] = None
    ):
        if url:
            self._url = url
        elif host and dbname:
            self._url = f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{dbname}"
        else:
            raise ValueError(
                "Either 'url' or both 'host' and 'dbname' must be provided."
            )

        self.name = name
        self.engine = None
        self.AsyncSessionLocal = None
        self._columns_map = None
        self._dump_include = None
        self._upsert = upsert
        self._index_elements = index_elements

        self._query = None
        self._custom_transformer = transformer

        self._emit_func = self._emit_orm
        logging.info("PostgresWriter initialized.")

    def on_conflict(self, index_elements: list[str], inplace=False):
        self._upsert = True
        self._index_elements = index_elements

        if inplace:
            return None
        else:
            return self

    def register_map(self, columns_map: dict[str, str]):
        # Note: The map keys must match the model's attribute names.
        self._columns_map = columns_map
        self._dump_include = columns_map.values()

    def set_query(self, query: str, inplace=False):

        self._query = query
        self._emit_func = self._emit_sql
        if inplace:
            return None
        else:
            return self

    def set_model(self, model: type[Base], inplace=False):
        self.DATA_MODEL = model
        self._emit_func = self._emit_orm
        if inplace:
            return None
        else:
            return self

    def set_transformer(self, transformer_function: Callable[[Dict[str, Any]], dict], inplace=False):
        self._custom_transformer = transformer_function
        if inplace:
            return None
        else:
            return self

    def _included_columns(self):
        if self._dump_include is not None:
            return self._dump_include
        else:
            return self.DATA_MODEL.__table__.columns.keys()

    def _create_model_object(self, data: Union[BaseModel, Dict]):

        if isinstance(data, dict):
            obj_data = {key: value for key, value in data.items() if key in self._included_columns()}
        else:
            obj_data = data.model_dump(include=self._included_columns())

        if self._custom_transformer is None:
            pass
        else:
            obj_data = self._custom_transformer(obj_data)

        return self.DATA_MODEL(**transform(record=obj_data, map_obj=self._columns_map))

    async def connect(self):
        """Initializes the SQLAlchemy async engine and sessionmaker."""
        try:
            # create_async_engine manages the connection pool.
            self.engine = create_async_engine(self._url)
            # async_sessionmaker is used to create sessions from the pool.
            self.AsyncSessionLocal = async_sessionmaker(
                self.engine, class_=AsyncSession, expire_on_commit=False
            )
            logging.info("Successfully initialized SQLAlchemy async engine.")
        except Exception as e:
            logging.error(f"Error connecting to the database: {e}")
            self.engine = None
            self.AsyncSessionLocal = None

    async def _emit_sql(self, data: BaseModel):

        params = data.model_dump()
        if not self.AsyncSessionLocal:
            logging.error("No database connection available. Cannot emit SQL.")
            return

        try:
            async with self.AsyncSessionLocal() as session:
                try:

                    await session.execute(text(self._query), params)
                    await session.commit()
                    logging.info(f"Emitted Data | Emitter: {self.name} | Mode: Query | {params}.")
                except Exception:
                    await session.rollback()
                    raise
        except Exception as e:
            logging.error(f"Error executing custom SQL query: {e}")

    async def _emit_orm(self, data: BaseModel):
        """Inserts data using a SQLAlchemy ORM model."""
        if not self.AsyncSessionLocal:
            logging.error("No database connection available. Cannot emit data.")
            return

        try:
            data_obj = self._create_model_object(data=data)

            async with self.AsyncSessionLocal() as session:
                try:
                    if self._upsert:
                        # Logic for on_conflict_do_update
                        if not self._index_elements:
                            raise ValueError("index_elements must be provided for upsert.")

                        obj_values = {
                            c.key: getattr(data_obj, c.key)
                            for c in inspect(self.DATA_MODEL).mapper.column_attrs
                        }

                        insert_stmt = insert(self.DATA_MODEL).values(obj_values)

                        key_columns = set(self._index_elements)
                        update_map = {
                            col.key: insert_stmt.excluded[col.key]
                            for col in self.DATA_MODEL.__table__.columns
                            if col.key not in key_columns
                        }

                        on_conflict_stmt = insert_stmt.on_conflict_do_update(
                            index_elements=self._index_elements,
                            set_=update_map
                        )

                        await session.execute(on_conflict_stmt)
                    else:
                        # Original insert logic
                        session.add(data_obj)

                    await session.commit()
                except Exception:
                    await session.rollback()
                    raise
                logging.info(f"Emitted Data | Emitter: {self.name} | Mode: ORM | {data_obj}.")
        except Exception as e:
            logging.info(f"Error inserting data: {e}")

    async def emit_orm_bulk(self, data_list: list[BaseModel]):
        """Insert a list of data objects in bulk using SQLAlchemy ORM."""
        if not self.AsyncSessionLocal:
            logging.error("No database connection available. Cannot emit bulk data.")
            return

        if not data_list:
            logging.warning("Empty list passed to emit_bulk.")
            return

        try:
            # Convert all Pydantic models into ORM objects
            objs = []
            for data in data_list:
                data_obj = self._create_model_object(data=data)
                objs.append(data_obj)

            async with self.AsyncSessionLocal() as session:
                try:
                    if self._upsert:
                        if not self._index_elements:
                            raise ValueError("index_elements must be provided for bulk upsert.")

                        insert_values = [
                            {
                                c.key: getattr(obj, c.key)
                                for c in inspect(self.DATA_MODEL).mapper.column_attrs
                            }
                            for obj in objs
                        ]

                        insert_stmt = insert(self.DATA_MODEL).values(insert_values)

                        key_columns = set(self._index_elements)
                        update_map = {
                            col.key: insert_stmt.excluded[col.key]
                            for col in self.DATA_MODEL.__table__.columns
                            if col.key not in key_columns
                        }

                        on_conflict_stmt = insert_stmt.on_conflict_do_update(
                            index_elements=self._index_elements,
                            set_=update_map
                        )

                        await session.execute(on_conflict_stmt)
                    else:
                        session.add_all(objs)

                    await session.commit()
                    logging.info(f"Bulk emitted {len(objs)} records to {self.name}.")
                except Exception:
                    await session.rollback()
                    raise
        except Exception as e:
            logging.error(f"Error inserting bulk data: {e}")

    async def emit(self, data: BaseModel):
        await self._emit_func(data=data)

    async def close(self):
        """Disposes the engine, closing the connection pool."""
        if self.engine:
            await self.engine.dispose()
            logging.info("SQLAlchemy engine and connection pool closed.")

