# Python
import logging

# Starlette
from starlette.responses import StreamingResponse
from starlette.requests import Request

# App Files
from src.commons.yaml_reader import yaml_reader

# Commons
from src.commons.path_manager import get_file_name
from src.commons.singleton import Singleton

__all__ = ["logging_middleware"]

script_name = get_file_name()

from fastapi import Request

# TODO: make this middleware work instead of using error_handler_middleware for both porposes


class LoggingMiddleware(metaclass=Singleton):
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

        logging.info(yaml_reader.get_logg_message(script_name, "logg_001"))

        # await self.__set_body__(request=request)
        # request_body = await request.json()
        response: StreamingResponse = await call_next(request)

        # response_status_code = response.status_code
        # uuid_tarcer = str(uuid.uuid4())

        logging.info(yaml_reader.get_logg_message(script_name, "logg_002"))

        return response


logging_middleware = LoggingMiddleware()
