# Starlette
from starlette.responses import StreamingResponse
from starlette.requests import Request

__all__ = ["logging_middleware"]


class LoggingMiddleware:
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


logging_middleware = LoggingMiddleware()
