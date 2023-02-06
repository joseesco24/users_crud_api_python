# ** info: ariadne imports
from ariadne import ScalarType


__all__: list[str] = ["integer_scalar"]

integer_scalar: ScalarType = ScalarType("Integer")


@integer_scalar.serializer
def serialize_integer(value: int):
    return int(value)
