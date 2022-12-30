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
from src.common_artifacts.metaclass.singleton import Singleton

# pylint: disable=unused-variable
__all__: list[str] = [r"custom_logger"]


class CustomLogger(metaclass=Singleton):
    def __init__(self) -> None:
        pass

    def setup_development_logging(self) -> None:

        """setup development logging
        this function overwrites the python root logger with a custom logger, so all the logs are
        written with the new overwritten configuration
        """

        fmt: str = "[{process.name}][{thread.name}][{time:YYYY-MM-DD HH:mm:ss.SSSSSS}]:{level} - {module}:{function}:{line} - {message}"

        # ** info: overwriting all the loggers configs with the new one
        logging.root.handlers = [self.__CustomInterceptHandler()]
        logging.root.setLevel(logging.DEBUG)

        for name in logging.root.manager.loggerDict.keys():
            logging.getLogger(name).handlers = list()
            logging.getLogger(name).propagate = True

        # ** info: loguru configs
        loguru_configs: dict = {
            r"sink": sys.stdout,
            r"serialize": False,
            r"colorize": False,
            r"format": fmt,
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
            r"sink": self.__custom_log_sink,
            r"serialize": True,
            r"colorize": False,
            r"format": fmt,
        }

        logger.configure(handlers=[loguru_configs])

    def __custom_log_sink(self, message) -> None:

        serialized = self.__custom_serializer(message.record)
        sys.stdout.write(serialized)
        sys.stdout.write("\n")
        sys.stdout.flush()

    def __custom_serializer(self, record) -> str:

        subset: dict[str, any] = {
            r"severity": record[r"level"].name,
            r"timestamp": record[r"time"].strftime("%Y-%m-%d %H:%M:%S.%f"),
            r"message": record[r"message"],
            r"function": record[r"function"],
            r"module": record[r"module"],
            r"line": record[r"line"],
            r"processName": record[r"process"].name,
            r"processId": record[r"process"].id,
            r"threadName": record[r"thread"].name,
            r"threadId": record[r"thread"].id,
            r"filePath": record[r"file"].path,
            r"fileName": record[r"file"].name,
        }

        if record[r"extra"]:
            subset[r"payload"] = record[r"extra"]

        if record[r"exception"] is not None:
            error: Exception = record[r"exception"]

            error_traceback: traceback = error.traceback
            error_message: str = error.value.args[0]
            error_type: str = error.type.__name__
            string_traceback: str

            string_traceback = "".join(traceback.format_tb(error_traceback))

            subset[r"errorDetails"] = {
                r"exceptionType": error_type,
                r"errorMessage": error_message,
                r"errorTraceback": string_traceback,
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
