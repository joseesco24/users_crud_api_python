#!/usr/bin/env python3

# ** info: typing imports
from typing import Dict


class Singleton(type):

    """singleton

    a simple metaclass that allows to implement sigleton pattern easily

    """

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
