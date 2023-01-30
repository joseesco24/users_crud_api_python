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
    this class provides a custom error handler middleware for fastapi based applications
    """

    def __init__(self):
        pass

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
        with logger.contextualize(requestId=uuid_provider.get_str_uuid()):
            response: StreamingResponse = await call_next(request)

        return response


logger_contextualizer: LoggerContextualizer = LoggerContextualizer()
