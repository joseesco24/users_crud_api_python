# !/usr/bin/python3
# type: ignore

# ** info: python imports
import traceback
import logging
import json
import sys

# ** info: typing imports
from typing import Union
from typing import Dict
from typing import Self
from typing import Any

# ** info: types imports
from types import TracebackType
from types import FrameType

# ** info: loguru imports
from loguru import logger

# ** info: loguru _recattrs imports
from loguru._recattrs import RecordException

# ** info: artifacts imports
from src.artifacts.datetime.datetime_provider import datetime_provider
from src.artifacts.uuid.uuid_provider import uuid_provider
from src.artifacts.pattern.singleton import Singleton

__all__: list[str] = ["custom_logger"]


class CustomLogger(metaclass=Singleton):
    def __init__(self: Self) -> None:
        self._extras: Dict[str, str] = {
            "internalId": "397d4343-2855-4c92-b64b-58ee82006e0b",
            "externalId": "397d4343-2855-4c92-b64b-58ee82006e0b",
            "appInstanceId": uuid_provider.get_str_uuid(),
            "appName": "users_crud_api_python",
            "responseHeaders": "undefined",
            "requestHeaders": "undefined",
            "responseBody": "undefined",
            "responseCode": "undefined",
            "requestBody": "undefined",
            "endpointUrl": "undefined",
            "startTime": "undefined",
            "endTime": "undefined",
            "fullUrl": "undefined",
            "group": "undefined",
        }

    def setup_pretty_logging(self: Self) -> None:
        """setup pretty logging
        this function overwrites the python root logger with a custom logger, so all the logs are
        written with the new overwritten configuration
        """

        # ** info: optional add [{process.name}][{thread.name}] to fmt to see the thread and process names

        fmt: str = "[<fg #66a3ff>{time:YYYY-MM-DD HH:mm:ss.SSSSSS!UTC}</fg #66a3ff>:<fg #fc03cf>{extra[internalId]}</fg #fc03cf>] <level>{level}</level> ({module}:{function}:<bold>{line}</bold>): {message}"  # noqa: E501

        # ** info: overwriting all the loggers configs with the new one
        logging.root.handlers = [self._CustomInterceptHandler()]
        logging.root.setLevel(logging.DEBUG)

        for name in logging.root.manager.loggerDict.keys():
            logging.getLogger(name).handlers = list()
            logging.getLogger(name).propagate = True

        # ** info: loguru configs
        loguru_configs: dict = {
            "sink": sys.stdout,
            "serialize": False,
            "colorize": True,
            "format": fmt,
        }

        logger.configure(extra=self._extras)
        logger.configure(handlers=[loguru_configs])

    def setup_structured_logging(self: Self) -> None:
        """setup structured logging
        this function overwrites the python root logger with a custom logger, so all the logs are
        written with the new overwritten configuration
        """

        fmt: str = "{message}"

        # ** info: overwriting all the loggers configs with the new one
        logging.root.handlers = [self._CustomInterceptHandler()]
        logging.root.setLevel(logging.DEBUG)

        for name in logging.root.manager.loggerDict.keys():
            logging.getLogger(name).handlers = list()
            logging.getLogger(name).propagate = True

        # ** info: loguru configs
        loguru_configs: dict = {
            "sink": self.__custom_log_sink,
            "serialize": True,
            "colorize": False,
            "format": fmt,
        }

        logger.configure(extra=self._extras)
        logger.configure(handlers=[loguru_configs])

    def __custom_log_sink(self: Self, message) -> None:
        serialized = self.__custom_serializer(message.record)
        sys.stdout.write(serialized)
        sys.stdout.write("\n")
        sys.stdout.flush()

    def __custom_serializer(self: Self, record) -> str:
        subset: Dict[str, Any] = {
            "loggId": uuid_provider.get_str_uuid(),
            "severity": record["level"].name,
            "timestamp": datetime_provider.get_utc_pretty_string(),
            "message": record["message"],
            "execution": {
                "group": record["extra"]["group"],
                "function": record["function"],
                "module": record["module"],
                "line": record["line"],
                "processName": record["process"].name,
                "processId": record["process"].id,
                "threadName": record["thread"].name,
                "threadId": record["thread"].id,
                "filePath": record["file"].path,
                "fileName": record["file"].name,
            },
            "request": {
                "externalId": record["extra"]["externalId"],
                "internalId": record["extra"]["internalId"],
                "body": record["extra"]["requestBody"],
                "headers": record["extra"]["requestHeaders"],
                "endpointUrl": record["extra"]["endpointUrl"],
                "fullUrl": record["extra"]["fullUrl"],
                "startTime": record["extra"]["startTime"],
            },
            "response": {
                "body": record["extra"]["responseBody"],
                "headers": record["extra"]["responseHeaders"],
                "status": record["extra"]["responseCode"],
                "endTime": record["extra"]["endTime"],
            },
            "app": {
                "name": record["extra"]["appName"],
                "id": record["extra"]["appInstanceId"],
                "aliveTime": datetime_provider.prettify_time_delta_obj(record["elapsed"]),
            },
        }

        if record["exception"] is not None:
            error: RecordException = record["exception"]

            error_traceback: TracebackType = error.traceback
            error_message: str = error.value.args[0]
            error_type: str = error.type.__name__
            string_traceback: str

            string_traceback = "".join(traceback.format_tb(error_traceback))

            subset["error"] = {
                "type": error_type,
                "message": error_message,
                "traceback": string_traceback,
            }

        return json.dumps(subset)

    class _CustomInterceptHandler(logging.Handler):
        def emit(self: Self, record: logging.LogRecord):
            level: Union[str, int]

            try:
                level = logger.level(record.levelname).name
            except ValueError:
                level = record.levelno

            frame: FrameType = logging.currentframe()
            depth: int = 2

            while frame.f_code.co_filename == logging.__file__:
                frame = frame.f_back
                depth += 1

            logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


custom_logger: CustomLogger = CustomLogger()
