#!/usr/bin/env python3

# ** info: python imports
import traceback
import logging
import json
import sys

# ** info: types imports
from types import FrameType

# ** info: loguru imports
from loguru import logger

__all__ = ["custom_logger"]


class CustomLogger:

    """custom logger

    a custom logger provider based on loguru loger

    """

    class CustomInterceptHandler(logging.Handler):
        def emit(self, record: logging.LogRecord):
            try:
                level: str = logger.level(record.levelname).name
            except ValueError:
                level: int = record.levelno

            frame: FrameType = logging.currentframe()
            depth: int = 2

            while frame.f_code.co_filename == logging.__file__:
                frame = frame.f_back
                depth += 1

            logger.opt(depth=depth, exception=record.exc_info).log(
                level, record.getMessage()
            )

    def custom_serializer(self, record) -> str:
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

        if record["extra"] is not None:
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

    def custom_log_sink(self, message) -> None:
        serialized = self.custom_serializer(message.record)
        sys.stdout.write(serialized)
        sys.stdout.write("\n")
        sys.stdout.flush()

    def setup_development_logging(self) -> None:

        """setup development logging

        this function overwrites the python root logger with a custom logger, so all the logs are
        written with the new overwritten configuration

        """

        fmt: str = "[{process.name}][{thread.name}][{time:YYYY-MM-DD HH:mm:ss.SSSSSS}]:{level} - {module}:{function}:{line} - {message}"

        # ** info: overwriting all the loggers configs with the new one
        logging.root.handlers = [self.CustomInterceptHandler()]
        logging.root.setLevel(logging.DEBUG)

        for name in logging.root.manager.loggerDict.keys():
            logging.getLogger(name).handlers = []
            logging.getLogger(name).propagate = True

        # ** info: loguru configs
        loguru_configs: dict = {
            "sink": sys.stdout,
            "serialize": False,
            "colorize": False,
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
        logging.root.handlers = [self.CustomInterceptHandler()]
        logging.root.setLevel(logging.DEBUG)

        for name in logging.root.manager.loggerDict.keys():
            logging.getLogger(name).handlers = []
            logging.getLogger(name).propagate = True

        # ** info: loguru configs
        loguru_configs: dict = {
            "sink": self.custom_log_sink,
            "serialize": True,
            "colorize": False,
            "format": fmt,
        }

        logger.configure(handlers=[loguru_configs])


custom_logger: CustomLogger = CustomLogger()
