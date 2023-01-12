# ** info: python imports
import traceback
import logging
import json
import sys

# ** info: types imports
from types import FrameType
from typing import Optional
from typing import Union

# ** info: loguru imports
from loguru import logger

# ** info: common artifacts imports
from src.artifacts.pattern_utils.singleton import Singleton

# pylint: disable=unused-variable
__all__: list[str] = ["custom_logger"]


class CustomLogger(metaclass=Singleton):
    def __init__(self) -> None:
        pass

    def setup_development_logging(self) -> None:
        """setup development logging
        this function overwrites the python root logger with a custom logger, so all the logs are
        written with the new overwritten configuration
        """

        # ** info: optional add [{process.name}][{thread.name}] to fmt to see the thread and process names

        # pylint: disable=line-too-long
        fmt: str = "[<fg #66a3ff>{time:YYYY-MM-DD HH:mm:ss.SSSSSS}</fg #66a3ff>] <level>{level}</level> ({module}:{function}:<bold>{line}</bold>): {message}"

        # ** info: overwriting all the loggers configs with the new one
        logging.root.handlers = [self.__CustomInterceptHandler()]
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

        logger.configure(handlers=[loguru_configs])

    def setup_production_logging(self) -> None:
        """setup production logging
        this function overwrites the python root logger with a custom logger, so all the logs are
        written with the new overwritten configuration
        """

        fmt: str = "{message}"

        # ** info: overwriting all the loggers configs with the new one
        logging.root.handlers = [self.__CustomInterceptHandler()]
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

        logger.configure(handlers=[loguru_configs])

    def __custom_log_sink(self, message) -> None:
        serialized = self.__custom_serializer(message.record)
        sys.stdout.write(serialized)
        sys.stdout.write("\n")
        sys.stdout.flush()

    def __custom_serializer(self, record) -> str:
        subset: dict[str, any] = {
            "severity": record["level"].name,
            "timestamp": record["time"].strftime("%Y-%m-%d %H:%M:%S.%f"),
            "message": record["message"],
            "function": record["function"],
            "module": record["module"],
            "line": record["line"],
            "processName": record["process"].name,
            "processId": record["process"].id,
            "threadName": record["thread"].name,
            "threadId": record["thread"].id,
            "filePath": record["file"].path,
            "fileName": record["file"].name,
        }

        if record["extra"]:
            subset["payload"] = record["extra"]

        if record["exception"] is not None:
            error: Exception = record["exception"]

            error_traceback: traceback = error.traceback
            error_message: str = error.value.args[0]
            error_type: str = error.type.__name__
            string_traceback: str

            string_traceback = "".join(traceback.format_tb(error_traceback))

            subset["errorDetails"] = {
                "exceptionType": error_type,
                "errorMessage": error_message,
                "errorTraceback": string_traceback,
            }

        return json.dumps(subset)

    # pylint: disable=invalid-name
    class __CustomInterceptHandler(logging.Handler):
        def emit(self, record: logging.LogRecord):
            try:
                level: Union[str, int] = logger.level(record.levelname).name
            except ValueError:
                level = record.levelno

            frame: Optional[FrameType] = logging.currentframe()
            depth: int = 2

            while frame.f_code.co_filename == logging.__file__:
                frame = frame.f_back
                depth += 1

            logger.opt(depth=depth, exception=record.exc_info).log(
                level, record.getMessage()
            )


custom_logger: CustomLogger = CustomLogger()
