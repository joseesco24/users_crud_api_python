# ** info: typing imports
from typing import Optional

# ** info: pydantic imports
from pydantic import BaseModel

# pylint: disable=unused-variable
__all__ = ["HealthCheckResponseDto"]


class HealthCheckResponseDto(BaseModel):
    redisDownloadConnection: Optional[bool] = None
    redisUploadConnection: Optional[bool] = None
    postgresQuerySession: Optional[bool] = None
    allConnectionsOk: Optional[bool] = None
    memoryUsage: Optional[int] = None
    cpuUsage: Optional[int] = None
