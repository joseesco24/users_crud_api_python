# ** info: starlette imports
from starlette.responses import StreamingResponse
from starlette.requests import Request


# ** info: artifacts imports
from src.artifacts.pattern.singleton import Singleton

# pylint: disable=unused-variable
__all__: list[str] = ["logger_setup"]


class LoggerSetup(metaclass=Singleton):

    """error handler
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
        response: StreamingResponse = await call_next(request)

        return response


logger_setup: LoggerSetup = LoggerSetup()
