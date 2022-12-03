# Typing
from typing import Dict


class Singleton(type):
    __instances__: Dict = dict()

    def __call__(cls, *args, **kwargs):
        if cls not in cls.__instances__:
            cls.__instances__[cls]: object = super(Singleton, cls).__call__(
                *args, **kwargs
            )
        return cls.__instances__[cls]

    @classmethod
    def __clean_instances__(cls):
        cls.__instances__ = dict()
