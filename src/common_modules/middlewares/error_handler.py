# Python
from datetime import datetime
import traceback
import logging
import uuid
import json
import sys

# Starlette
from starlette.responses import StreamingResponse
from starlette.responses import Response
from starlette.requests import Request

# FastAPI
from fastapi.responses import JSONResponse
from fastapi import status

# HTTPX
from httpx import ConnectError
from httpx import post

# App Files
from src.commons.yaml_reader import yaml_reader

# Commons
from src.commons.path_manager import get_file_name
from src.commons.singleton import Singleton
from src.commons.config import configs

__all__ = ["error_handler_middleware"]

script_name = get_file_name()

# TODO: Remove burned variables and delegate logging logic to a dedicated logger middleware


class ErrorHandlerMiddleware(metaclass=Singleton):
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

        """error handler

        this middleware is used for handling unhandled errors, without stopping the server and also
        leaving a error traceback in the loggs

        args:
        - call_next (callable): the path function
        - request (Request): the user request

        returns:
        - JSONResponse: the response between the path and the user or a default response on
        exception case
        """

        logging.info(yaml_reader.get_logg_message(script_name, "logg_001"))
        init_time_stamp = datetime.timestamp(datetime.now())

        await self.__set_body__(request=request)
        stack_trace = None
        level = None

        try:

            router_response: StreamingResponse = await call_next(request)
            stack_trace = None
            level = "INFO"

        except Exception:

            error_type = str(sys.exc_info()[0].__name__)
            error_message = str(sys.exc_info()[1])

            logging.error(
                f"internal server error - {error_type}: {error_message} \n\n {traceback.format_exc(chain=False)} \n\n"
            )

            router_response: StreamingResponse = JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "internal server error"},
            )

            stack_trace = traceback.format_exc(chain=False)
            level = "ERROR"

        end_time_stamp = datetime.timestamp(datetime.now())
        logging.info(yaml_reader.get_logg_message(script_name, "logg_002"))

        if level == "INFO":
            response_body = b""
            async for chunk in router_response.body_iterator:
                response_body += chunk

            response_headers = router_response.headers
            response_status_code = router_response.status_code

        else:
            response_body = b'{"detail": "internal server error"}'
            response_headers = {}
            response_status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

        if configs.environment_mode == "production":

            try:

                await self.__logg__(
                    response_body=response_body,
                    init_time_stamp=init_time_stamp,
                    end_time_stamp=end_time_stamp,
                    request=request,
                    stack_trace=stack_trace,
                    level=level,
                    response_headers=response_headers,
                    response_status_code=response_status_code,
                )

            except ConnectError:

                error_data = {"logger_url": str(configs.logger_service_url)}
                logging.info(
                    yaml_reader.get_error_message(script_name, "error_001", error_data)
                )

            except Exception:

                error_data = {"logger_url": str(configs.logger_service_url)}
                logging.info(
                    yaml_reader.get_error_message(script_name, "error_002", error_data)
                )

        return Response(
            content=response_body,
            status_code=response_status_code,
            headers=dict(response_headers),
            media_type=router_response.media_type,
        )

    async def __logg__(
        self,
        response_body: bytearray,
        init_time_stamp: float,
        end_time_stamp: float,
        request: Request,
        stack_trace: str,
        level: str,
        response_headers,
        response_status_code,
    ) -> None:

        request_body = await request.json()
        request_headers = request.headers
        request_url = str(request.url)
        uuid_tarcer = str(uuid.uuid4())

        code = "INFO00000"
        group = "process"

        message = "test message"

        userIdentity = {
            "sourceIp": "192.168.0.1",
            "accountId": "2658478555",
            "sessionId": "12e8aea7-b23a-46ae-90b4-ef2bd2965ed8",
            "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "sessionChannelId": "App-Internals",
        }

        response_body = dict(json.loads(response_body.decode()))
        response_body.update({"status": response_status_code})

        logg = {
            "level": level,
            "ruta": request_url,
            "stackTrace": stack_trace,
            "requestId": uuid_tarcer,
            "request": {
                "body": request_body,
                "headers": request_headers,
                "url": request_url,
            },
            "endTimeStamp": end_time_stamp,
            "response": {
                "body": response_body,
                "headers": response_headers,
            },
            "code": code,
            "group": group,
            "initTimeStamp": init_time_stamp,
            "message": message,
            "userIdentity": userIdentity,
        }

        logger_path = configs.logger_service_url

        post(logger_path, data=logg)


error_handler_middleware = ErrorHandlerMiddleware()
