# ** info: python imports
import logging

# ** info: starlette imports
from starlette.responses import StreamingResponse
from starlette.responses import ContentStream
from starlette.requests import Request

# ** info: fastapi imports
from fastapi import status

# ** info: artifacts imports
from src.artifacts.pattern.singleton import Singleton

# ** info: databases connection managers imports
from src.database.cache_database.connection_manager import (
    connection_manager as cache_connection_manager,
)
from src.database.users_database.connection_manager import (
    connection_manager as users_connection_manager,
)

# pylint: disable=unused-variable
__all__: list[str] = ["database_health_check"]


class DatabaseHealthCheck(metaclass=Singleton):

    """database health check
    this class provides a databases health check middleware for fastapi based applications
    """

    def __init__(self):
        pass

    async def _get_internal_server_error_stream(self) -> ContentStream:
        response_stream: ContentStream = iter(["Internal Server Error"])
        response: StreamingResponse = StreamingResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=response_stream,
        )
        return response

    async def __set_body__(self, request: Request):
        receive_ = await request._receive()

        async def receive():
            return receive_

        request._receive = receive

    async def __call__(
        self,
        request: Request,
        call_next: callable,
    ) -> StreamingResponse:
        are_databses_healty: bool = True

        if (
            await cache_connection_manager._download_connection._check_connection_health()
            is False
        ):
            logging.warning("cache download connection isn't healthy")
            are_databses_healty = False

        if (
            await cache_connection_manager._upload_connection._check_connection_health()
            is False
        ):
            logging.warning("cache upload connection isn't healthy")
            are_databses_healty = False

        if users_connection_manager._check_query_session_health() is False:
            logging.warning("users query session isn't healthy")
            are_databses_healty = False

        if are_databses_healty is False:
            return self._get_internal_server_error_stream()

        logging.info("all databases are healthy")

        response: StreamingResponse = await call_next(request)

        return response


database_health_check: DatabaseHealthCheck = DatabaseHealthCheck()
