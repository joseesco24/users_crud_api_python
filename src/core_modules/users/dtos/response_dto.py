#!/usr/bin/env python3

# ** info: pydantic imports
from pydantic import BaseModel
from pydantic import Field

__all__ = ["ResponseDto"]


class ResponseDto(BaseModel):
    detail: str = Field(...)
