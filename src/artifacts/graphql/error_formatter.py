# !/usr/bin/python3
# type: ignore

# ** info: python imports
import logging

# ** info: typing imports
from typing import Self

# ** info: ariadne imports
from ariadne import format_error

# ** info: graphql imports
from graphql import GraphQLError

# ** info: common artifacts imports
from src.artifacts.pattern.singleton import Singleton

__all__: list[str] = ["error_formatter"]


class ErrorFormatter(metaclass=Singleton):
    def __init__(self: Self) -> None:
        pass

    @staticmethod
    def formatter(error: GraphQLError, debug: bool) -> dict:
        if error.extensions == {}:
            logging.error(f"a not handled graphql error has occurred on the api server, error message: {error.message}")

        if debug is True:
            formatted: dict = format_error(error=error, debug=True)  # type: ignore
            return formatted

        formatted: dict = error.formatted  # type: ignore

        if error.extensions == {}:
            formatted["message"] = "Internal Server Error"
        else:
            formatted["message"] = error.message

        del formatted["locations"]
        del formatted["path"]

        return formatted


error_formatter: ErrorFormatter = ErrorFormatter()
