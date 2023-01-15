from ariadne import ScalarType


# pylint: disable=unused-variable
__all__: list[str] = ["integer_scalar"]

integer_scalar: ScalarType = ScalarType("Integer")


@integer_scalar.serializer
def serialize_integer(value: int):
    return int(value)
