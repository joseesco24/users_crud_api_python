# Pydantic
from pydantic import BaseModel
from pydantic import Field

__all__ = ["ResponseDto"]


class ResponseDto(BaseModel):
    detail: str = Field(...)
