#!/usr/bin/env python3

# ** info: python imports
import logging

# ** info: starlette imports
from starlette.responses import StreamingResponse
from starlette.responses import ContentStream
from starlette.requests import Request

# ** info: fastapi imports
from fastapi import status

# ** info: common artifacts imports
from src.common_artifacts.singleton import Singleton

__all__ = ["error_handler"]


class ErrorHandler(metaclass=Singleton):
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

        try:

            response: StreamingResponse = await call_next(request)

        except Exception as exception:

            logging.exception(
                f"a not handled error has occurred on the api server: {exception.args[0]}"
            )

            response_stream: ContentStream = iter(["Internal Server Error"])

            response: StreamingResponse = StreamingResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=response_stream,
            )

        return response


error_handler: ErrorHandler = ErrorHandler()
