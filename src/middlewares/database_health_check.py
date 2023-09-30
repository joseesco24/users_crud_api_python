# !/usr/bin/python3
# type: ignore

# ** info: python imports
from asyncio import gather
import logging

# ** info: typing imports
from typing import Callable
from typing import Tuple
from typing import Self

# ** info: starlette imports
from starlette.responses import StreamingResponse
from starlette.responses import ContentStream
from starlette.requests import Request

# ** info: fastapi imports
from fastapi import status

# ** info: artifacts imports
from src.artifacts.pattern.singleton import Singleton
from src.artifacts.env.configs import configs

# ** info: databases connection managers imports
from src.database.cache_database.connection_manager import (
    connection_manager as cache_connection_manager,
)

__all__: list[str] = ["database_health_check"]


class DatabaseHealthCheck(metaclass=Singleton):

    """database health check
    this class provides a databases health check middleware for fastapi based applications
    """

    def __init__(self: Self):
        pass

    async def _get_internal_server_error_stream(self: Self) -> StreamingResponse:
        response_stream: ContentStream = iter(["Internal Server Error"])
        response: StreamingResponse = StreamingResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=response_stream,
        )
        return response

    async def __set_body__(self: Self, request: Request):
        receive_ = await request._receive()

        async def receive():
            return receive_

        request._receive = receive

    async def __call__(
        self: Self,
        request: Request,
        call_next: Callable,
    ) -> StreamingResponse:
        await self.__set_body__(request=request)

        base_url: str = str(request.base_url)
        full_url: str = str(request.url)

        endpoint_url: str = full_url.replace(base_url, "").strip().lower()

        if endpoint_url in configs.app_database_health_check_middleware_exclude:
            logging.info("jumping databases health check middleware validations")
            response: StreamingResponse = await call_next(request)
            return response

        are_databses_healty: bool = True

        cache_connections_health: Tuple[bool, bool] = await gather(
            cache_connection_manager._download_connection._check_connection_health(),
            cache_connection_manager._upload_connection._check_connection_health(),
        )

        is_download_connection_healthy: bool = cache_connections_health[0]
        is_upload_connection_healthy: bool = cache_connections_health[1]

        if is_download_connection_healthy is False:
            logging.warning("cache download connection isn't healthy")
            are_databses_healty = False

        if is_upload_connection_healthy is False:
            logging.warning("cache upload connection isn't healthy")
            are_databses_healty = False

        if are_databses_healty is False:
            return await self._get_internal_server_error_stream()

        logging.info("all databases are healthy")

        response: StreamingResponse = await call_next(request)

        return response


database_health_check: DatabaseHealthCheck = DatabaseHealthCheck()
