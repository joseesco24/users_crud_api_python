# !/usr/bin/python3
# type: ignore

# ** info: pydantic imports
from pydantic import BaseModel
from pydantic import Field

# ** info: typing imports
from typing import Optional
from typing import List

__all__: list[str] = [
    "TvProgrammationSearchResponseRawReturnDto",
    "TvProgrammationSearchRequestDto",
    "TvProgrammationAddRequestDto",
    "TvProgrammationResponseDto",
]


class TvProgrammationSearchRequestDto(BaseModel):
    channelId: Optional[int] = Field(default=None)
    channelName: Optional[str] = Field(default=None)
    channelContentType: Optional[str] = Field(default=None)
    startHoure: Optional[str] = Field(default=None)
    endHoure: Optional[str] = Field(default=None)
    weeks: Optional[List[int]] = Field(default=None)
    days: Optional[List[int]] = Field(default=None)
    year: Optional[int] = Field(default=None)


class TvProgrammationAddRequestDto(BaseModel):
    channelId: int = Field(...)
    channelName: str = Field(...)
    channelContentType: str = Field(...)
    startHoure: str = Field(...)
    endHoure: str = Field(...)
    weeks: List[int] = Field(...)
    days: List[int] = Field(...)
    year: int = Field(...)


class TvProgrammationResponseDto(BaseModel):
    channelId: Optional[int] = None
    channelName: Optional[str] = None
    channelContentType: Optional[str] = None
    startHoure: Optional[str] = None
    endHoure: Optional[str] = None
    weeks: Optional[List[int]] = None
    days: Optional[List[int]] = None
    year: Optional[int] = None


class TvProgrammationSearchResponsePrettyReturnDto(BaseModel):
    data: Optional[List[str]] = None


class TvProgrammationSearchResponseRawReturnDto(BaseModel):
    data: Optional[List[TvProgrammationResponseDto]] = None
