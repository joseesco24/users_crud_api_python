# Python
from ntpath import basename
import posixpath
import traceback

__all__ = ["build_posix_path", "get_file_name"]


def build_posix_path(*args: list[str]) -> str:

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


def get_file_name() -> str:

    """get file name

    this function returns the name of their caller module

    returns:
    - str: the name of the script without extension
    """

    (filename, _, _, _) = traceback.extract_stack()[-2]
    return basename(filename).split(".")[0]
