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
from src.artifacts.env.configs import configs

__all__: list[str] = ["authentication_handler"]


class AuthenticationHandler(metaclass=Singleton):

    """authentication handler
    this class provides a custom authentication middleware for fastapi based applications
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

        is_authenticated: bool = False

        if endpoint_url in configs.app_database_health_check_middleware_exclude:
            logging.info("jumping authentication middleware validations")
            is_authenticated = True

        else:
            # todo: create a real authentication logic here
            is_authenticated = True

        request_context: Context = contextvars.copy_context()
        logger_kwargs: Dict = dict()

        for item in request_context.items():
            if item[0].name == "loguru_context":
                logger_kwargs = item[1]
                break

        internal_id: str = logger_kwargs["internalId"]

        if is_authenticated:
            logging.info(f"the request with id {internal_id} was successfully authorized")
            response: StreamingResponse = await call_next(request)

        else:
            logging.error(f"the request with id {internal_id} was not successfully authorized")
            response_stream: ContentStream = iter(["Not Authorized"])

            response: StreamingResponse = StreamingResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content=response_stream,
            )

        return response


authentication_handler: AuthenticationHandler = AuthenticationHandler()
