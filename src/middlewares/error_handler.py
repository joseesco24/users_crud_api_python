# !/usr/bin/python3
# type: ignore

# ** info: python imports
from contextvars import Context
from typing import Callable
import contextvars
import logging

# ** info: typing imports
from typing import Self
from typing import Dict

# ** info: starlette imports
from starlette.responses import StreamingResponse
from starlette.responses import ContentStream
from starlette.requests import Request

# ** info: fastapi imports
from fastapi import status

# ** info: artifacts imports
from src.artifacts.pattern.singleton import Singleton

__all__: list[str] = ["error_handler"]


class ErrorHandler(metaclass=Singleton):

    """error handler
    this class provides a custom error handler middleware for fastapi based applications
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
        request_context: Context = contextvars.copy_context()
        logger_kwargs: Dict = dict()

        for item in request_context.items():
            if item[0].name == "loguru_context":
                logger_kwargs = item[1]
                break

        internal_id: str = logger_kwargs["internalId"]

        try:
            response: StreamingResponse = await call_next(request)
            logging.info(f"request with id {internal_id} successfully processed")

        except Exception as exception:
            if str(exception.args[0]).strip() == "":
                logging.exception(f"a handled error has occurred on the api while processing the request with id {internal_id}")

            else:
                logging.exception(
                    f"a not handled error has occurred on the api while processing the request with id {internal_id}: {exception.args[0]}"  # noqa: E501
                )

            response_stream: ContentStream = iter(["Internal Server Error"])

            response: StreamingResponse = StreamingResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=response_stream,
            )

        return response


error_handler: ErrorHandler = ErrorHandler()
