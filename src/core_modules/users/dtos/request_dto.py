#!/usr/bin/env python3

# ** info: pydantic imports
from pydantic import BaseModel
from pydantic import Field

__all__: list[str] = ["RequestDto"]


class RequestDto(BaseModel):
    fileName: str = Field(...)
