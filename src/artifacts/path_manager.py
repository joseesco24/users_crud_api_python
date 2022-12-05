# Python
import posixpath

__all__ = ["build_posix_path"]


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
