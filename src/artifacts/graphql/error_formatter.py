# ** info: python imports
import logging

# ** info: typing imports
from typing import Self

# ** info: ariadne imports
from ariadne import format_error

# ** info: graphql imports
from graphql import GraphQLFormattedError
from graphql import GraphQLError

# ** info: common artifacts imports
from src.artifacts.pattern.singleton import Singleton

__all__: list[str] = ["error_formatter"]


class ErrorFormatter(metaclass=Singleton):
    def __init__(self: Self) -> None:
        pass

    @staticmethod
    def formatter(error: GraphQLError, debug: bool) -> dict:
        logging.error(f"a not handled graphql error has occurred on the api server, error message: {error.message}")

        if debug is True:
            formatted: dict = format_error(error=error, debug=True)
            return formatted

        formatted: GraphQLFormattedError = error.formatted
        formatted["message"] = "Internal Server Error"
        del formatted["locations"]
        return formatted


error_formatter: ErrorFormatter = ErrorFormatter()
