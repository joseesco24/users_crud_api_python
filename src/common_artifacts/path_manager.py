#!/usr/bin/env python3

# ** info: python imports
import posixpath

# ** info: common artifacts imports
from src.common_artifacts.singleton import Singleton

__all__ = ["path_manager"]


class PathManager(metaclass=Singleton):
    def build_posix_path(self, *args: list[str]) -> str:

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


path_manager: PathManager = PathManager()
