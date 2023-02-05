# ** info: typing imports
from typing import Callable
from typing import Dict
from typing import Self
from typing import Any

# ** info: loguru imports
from loguru import logger

# ** info: starlette imports
from starlette.responses import StreamingResponse
from starlette.datastructures import Headers
from starlette.requests import Request

# ** info: artifacts imports
from src.artifacts.datetime.datetime_provider import datetime_provider
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
        start_time: str = datetime_provider.get_utc_pretty_string()

        await self.__set_body__(request=request)

        base_url: str = str(request.base_url)
        full_url: str = str(request.url)

        request_headers: Headers = request.headers
        headers_rep: Dict[str, Any] = dict()
        for key in request_headers.keys():
            headers_rep[key] = str(request_headers[key])

        request_body: Dict[str, str] = dict(await request.json())

        endpoint_url: str = full_url.replace(base_url, "").strip().lower()

        internal_id: str = uuid_provider.get_str_uuid()
        external_id: str = internal_id

        with logger.contextualize(
            requestHeaders=headers_rep,
            requestBody=request_body,
            endpointUrl=endpoint_url,
            internalId=internal_id,
            externalId=external_id,
            startTime=start_time,
            fullUrl=full_url,
        ):
            response: StreamingResponse = await call_next(request)

        return response


logger_contextualizer: LoggerContextualizer = LoggerContextualizer()
