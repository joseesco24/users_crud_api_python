#!/usr/bin/env python3

# ** info: pydantic imports
# pylint: disable=no-name-in-module
from pydantic import BaseModel
from pydantic import Field

# pylint: disable=unused-variable
__all__: list[str] = ["ResponseDto"]


class ResponseDto(BaseModel):
    detail: str = Field(...)
