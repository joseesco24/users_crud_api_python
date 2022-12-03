# Python
import logging
import sys

# Types
from types import FrameType

# Loguru
from loguru import logger

__all__ = ["setup_logging"]


class InterceptHandler(logging.Handler):
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


def setup_logging():

    """setup logging

    this function overwrites the Python root logger with a custom logger, so all the logs are
    written with the new overwritten configuration.
    """

    fmt: str = "[{process}][{time:YYYY-MM-DD HH:mm:ss.SS}]:{level} - {module}:{function}:{line} - {message}"

    logging.root.handlers = [InterceptHandler()]
    logging.root.setLevel(logging.DEBUG)

    for name in logging.root.manager.loggerDict.keys():
        logging.getLogger(name).handlers = []
        logging.getLogger(name).propagate = True

    logger.configure(handlers=[{"sink": sys.stdout, "colorize": False, "format": fmt}])
