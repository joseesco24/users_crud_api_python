# !/usr/bin/python3
# type: ignore

# ** info: python imports
from datetime import timedelta
import logging
import pickle
import gc

# ** info: typing imports
from typing import Optional
from typing import Union
from typing import Self
from typing import Any

# ** info: fastapi imports
from fastapi import HTTPException
from fastapi import status

# **info: asyncio redis imports
from redis.asyncio import Redis as AsyncRedis

# **info: redis exceptions imports
from redis.exceptions import ConnectionError as AsyncConnectionError

# ** info: artifacts imports
from src.artifacts.datetime.datetime_provider import datetime_provider
from src.artifacts.uuid.uuid_provider import uuid_provider
from src.artifacts.pattern.singleton import Singleton
from src.artifacts.env.configs import configs

__all__: list[str] = ["connection_manager"]


class AsyncDownloadConnection(AsyncRedis):
    def __init__(self: Self, password: str, host: str, port: int, database: str, logs: bool):
        self._connection_creation: str = datetime_provider.get_utc_iso_string()
        self._connection_id: str = uuid_provider.get_str_uuid()
        self._logs: bool = logs

        super().__init__(host=host, port=port, db=database, password=password)

        self._post_init()

    def _post_init(self: Self) -> None:
        if self._logs:
            logging.info(f"cache download connection started with id: {self._connection_id}")

    async def close(self: Self, close_connection_pool: Optional[bool] = None) -> None:
        logging.info(f"closing cache download connection with id: {self._connection_id}")
        await super().close(close_connection_pool=close_connection_pool)


class AsyncUploadConnection(AsyncRedis):
    def __init__(self: Self, password: str, host: str, port: int, database: str, logs: bool):
        self._connection_creation: str = datetime_provider.get_utc_iso_string()
        self._connection_id: str = uuid_provider.get_str_uuid()
        self._logs: bool = logs

        super().__init__(host=host, port=port, db=database, password=password)

        self._post_init()

    def _post_init(self: Self) -> None:
        if self._logs:
            logging.info(f"cache upload connection started with id: {self._connection_id}")

    async def close(self: Self, close_connection_pool: Optional[bool] = None) -> None:
        logging.info(f"closing cache upload connection with id: {self._connection_id}")
        await super().close(close_connection_pool=close_connection_pool)


class DownloadConnection(metaclass=Singleton):
    def __init__(self: Self, password: str, host: str, port: int, database: str, logs: bool):
        self._database: str = database
        self._password: str = password
        self._logs: bool = logs
        self._host: str = host
        self._port: int = port

        self._connection: Union[AsyncUploadConnection, None] = None

    def _start_connection(self: Self) -> None:
        if self._connection is None:
            self._connection = AsyncUploadConnection(
                password=self._password,
                database=self._database,
                logs=self._logs,
                host=self._host,
                port=self._port,
            )

    async def _close_connection(self: Self) -> None:
        if self._connection is not None:
            await self._connection.close()
            del self._connection
            gc.collect()
            self._connection = None

    async def _reset_connection(self: Self) -> None:
        await self._close_connection()
        self._start_connection()

    async def _check_connection_health(self: Self) -> bool:
        self._start_connection()
        try:
            await self._connection.ping()
            if self._logs:
                logging.debug(f"cache download connection {self._connection._connection_id} is healthy")
                logging.debug(
                    f"using cache download connection {self._connection._connection_id} since {self._connection._connection_creation}"  # noqa: E501
                )
            return True
        except AsyncConnectionError:
            if self._logs:
                logging.exception(f"cache download connection {self._connection._connection_id} isn't healthy")
                logging.warning("creating a new cache download connection")
            await self._reset_connection()
            return False

    async def _get(self: Self, key: str) -> Union[None, Any]:
        self._start_connection()
        if await self._check_connection_health() is False:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return await self._connection.get(name=key)


class UploadConnection(metaclass=Singleton):
    def __init__(self: Self, password: str, host: str, port: int, database: str, logs: bool):
        self._database: str = database
        self._password: str = password
        self._logs: bool = logs
        self._host: str = host
        self._port: int = port

        self._connection: Union[AsyncUploadConnection, None] = None

    def _start_connection(self: Self) -> None:
        if self._connection is None:
            self._connection = AsyncUploadConnection(
                password=self._password,
                database=self._database,
                logs=self._logs,
                host=self._host,
                port=self._port,
            )

    async def _close_connection(self: Self) -> None:
        if self._connection is not None:
            await self._connection.close()
            del self._connection
            gc.collect()
            self._connection = None

    async def _reset_connection(self: Self) -> None:
        await self._close_connection()
        self._start_connection()

    async def _check_connection_health(self: Self) -> bool:
        self._start_connection()
        try:
            await self._connection.ping()
            if self._logs:
                logging.debug(f"cache upload connection {self._connection._connection_id} is healthy")
                logging.debug(
                    f"using cache upload connection {self._connection._connection_id} since {self._connection._connection_creation}"  # noqa: E501
                )
            return True
        except AsyncConnectionError:
            if self._logs:
                logging.exception(f"cache upload connection {self._connection._connection_id} isn't healthy")
                logging.warning("creating a new cache upload connection")
            await self._reset_connection()
            return False

    async def _expire(self: Self, key: str, time: int) -> None:
        self._start_connection()
        if await self._check_connection_health() is False:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        await self._connection.expire(name=key, time=timedelta(seconds=time))

    async def _set_with_ttl(self: Self, key: str, value: Any, time: int) -> None:
        self._start_connection()
        if await self._check_connection_health() is False:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        await self._connection.set(name=key, value=value)
        await self._expire(key=key, time=time)


class ConnectionManager(metaclass=Singleton):
    def __init__(self: Self, password: str, host: str, port: int, database: str, logs: bool):
        self._download_connection: DownloadConnection = DownloadConnection(password=password, host=host, port=port, database=database, logs=logs)
        self._upload_connection: UploadConnection = UploadConnection(password=password, host=host, port=port, database=database, logs=logs)

    async def get(self: Self, key: str) -> Union[None, Any]:
        cache_response: Union[bytes, Any] = await self._download_connection._get(key=key)
        if cache_response is not None:
            return pickle.loads(cache_response)
        return None

    async def set_with_ttl(self, key: str, value: Any, time: int = configs.cache_database_default_ttl) -> None:
        await self._upload_connection._set_with_ttl(key=key, value=pickle.dumps(value), time=time)


connection_manager: ConnectionManager = ConnectionManager(
    password=configs.cache_database_password,
    database=configs.cache_database_name,
    host=configs.cache_database_host,
    port=configs.cache_database_port,
    logs=configs.cache_database_logs,
)
