# ** info: python imports
import logging
import json

# ** info: typing imports
from typing import Callable
from typing import Dict
from typing import Self
from typing import Any

# ** info: loguru imports
from loguru import logger

# ** info: starlette imports
from starlette.datastructures import MutableHeaders
from starlette.responses import StreamingResponse
from starlette.responses import ContentStream
from starlette.datastructures import Headers
from starlette.responses import Response
from starlette.requests import Request

# ** info: artifacts imports
from src.artifacts.datetime.datetime_provider import datetime_provider
from src.artifacts.uuid.uuid_provider import uuid_provider
from src.artifacts.pattern.singleton import Singleton

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

        endpoint_url: str = full_url.replace(base_url, "").strip().lower()

        request_headers: Headers = request.headers
        headers_rep: Dict[str, Any] = dict()
        for key in request_headers.keys():
            headers_rep[key] = str(request_headers[key])

        request_body: Dict[str, str]

        if await request.body():
            request_body = dict(await request.json())
        else:
            request_body = dict()

        internal_id: str = uuid_provider.get_str_uuid()

        if "requestId" in headers_rep:
            external_id: str = headers_rep["requestId"]
        else:
            external_id: str = internal_id

        response: Response

        with logger.contextualize(
            requestHeaders=headers_rep,
            requestBody=request_body,
            endpointUrl=endpoint_url,
            internalId=internal_id,
            externalId=external_id,
            startTime=start_time,
            fullUrl=full_url,
        ):
            router_response: StreamingResponse = await call_next(request)

            end_time: str = datetime_provider.get_utc_pretty_string()

            response_headers: MutableHeaders = router_response.headers
            response_headers_rep: Dict[str, Any] = dict()
            for key in response_headers.keys():
                response_headers_rep[key] = str(response_headers[key])

            response_content: bytes = b""
            async for chunk in router_response.body_iterator:
                if isinstance(chunk, bytes):
                    response_content += chunk

            response_body_rep: Dict[str, str] = dict(json.loads(response_content.decode()))

            response_status: int = router_response.status_code

            with logger.contextualize(
                responseHeaders=response_headers_rep,
                responseBody=response_body_rep,
                responseCode=response_status,
                endTime=end_time,
            ):
                logging.info(f"response details to request {internal_id}")

            content_literal: ContentStream = iter([response_content])

            response = StreamingResponse(
                media_type=router_response.media_type,
                headers=dict(response_headers),
                status_code=response_status,
                content=content_literal,
            )

        return response


logger_contextualizer: LoggerContextualizer = LoggerContextualizer()
