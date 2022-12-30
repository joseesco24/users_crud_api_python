# ** info: python imports
import logging

# ** info: ariadne imports
from ariadne import format_error

# ** info: graphql imports
from graphql import GraphQLFormattedError
from graphql import GraphQLError

# ** info: common artifacts imports
from src.common_artifacts.metaclass.singleton import Singleton

# pylint: disable=unused-variable
__all__: list[str] = ["custom_error_formatter"]


class CustomErrorFormatter(metaclass=Singleton):
    def __init__(self) -> None:
        pass

    @staticmethod
    def formatter(error: GraphQLError, debug: bool) -> dict:

        logging.error(
            f"a not handled graphql error has occurred on the api server, error message: {error.message}"
        )

        if debug is True:
            formatted: dict = format_error(error=error, debug=True)
            return formatted

        formatted: GraphQLFormattedError = error.formatted
        formatted["message"] = "Internal Server Error"
        del formatted["locations"]
        return formatted


custom_error_formatter: CustomErrorFormatter = CustomErrorFormatter()
