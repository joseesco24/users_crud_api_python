# Pydantic
from pydantic import BaseModel
from pydantic import Field

__all__ = ["RequestDto"]


class RequestDto(BaseModel):
    fileName: str = Field(...)
