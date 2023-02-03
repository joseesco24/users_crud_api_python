# ** info: python imports
import posixpath

# ** info: typing imports
from typing import Self

# ** info: artifacts imports
from src.artifacts.pattern.singleton import Singleton

# pylint: disable=unused-variable
__all__: list[str] = ["generator"]


class Generator(metaclass=Singleton):
    def build_posix_path(self: Self, *args: list[str]) -> str:
        """build posix path
        this function takes all the received string arguments and concatenate each one of the
        arguments into a posix path
        args:
        - args (list[str]): the name of the file to load
        returns:
        - str: posix resulting path
        """

        partial_path: str = posixpath.join(*args)
        return f"/{partial_path}".strip()


generator: Generator = Generator()
