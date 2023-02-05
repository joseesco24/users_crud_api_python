# ** info: typing imports
from typing import Callable
from typing import Self

# ** info: loguru imports
from loguru import logger

# ** info: starlette imports
from starlette.responses import StreamingResponse
from starlette.requests import Request

# ** info: artifacts imports
from src.artifacts.uuid.uuid_provider import uuid_provider
from src.artifacts.pattern.singleton import Singleton

# pylint: disable=unused-variable
__all__: list[str] = ["logger_contextualizer"]


class LoggerContextualizer(metaclass=Singleton):

    """logger contextualizer
    this class provides a custom loguru contextualizer middleware for fastapi based applications
    """

    def __init__(self: Self):
        pass

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

        with logger.contextualize(
            requestId=uuid_provider.get_str_uuid(),
            endpointUrl=endpoint_url,
            fullUrl=full_url,
        ):
            response: StreamingResponse = await call_next(request)

        return response


logger_contextualizer: LoggerContextualizer = LoggerContextualizer()
