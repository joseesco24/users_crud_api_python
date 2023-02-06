# ** info: python imports
from asyncio import gather
import logging

# ** info: typing imports
from typing import Tuple
from typing import Self

# ** info: python imports
import psutil

# ** info: artifacts imports
from src.artifacts.pattern.singleton import Singleton

# ** info: databases connection managers imports
from src.database.cache_database.connection_manager import (
    connection_manager as cache_connection_manager,
)
from src.database.users_database.connection_manager import (
    connection_manager as users_connection_manager,
)

# ** info: health check dtos imports
from src.dtos.health_check_dtos import HealthCheckResponseDto

# pylint: disable=unused-variable
__all__: list[str] = ["health_check_service"]


class HealthCheckService(metaclass=Singleton):
    async def get_health_check_metrics(self: Self) -> HealthCheckResponseDto:
        health_check_response: HealthCheckResponseDto = HealthCheckResponseDto()

        are_databses_healty: bool = True

        cache_connections_health: Tuple[bool, bool] = await gather(
            cache_connection_manager._download_connection._check_connection_health(),
            cache_connection_manager._upload_connection._check_connection_health(),
        )

        is_download_connection_healthy: bool = cache_connections_health[0]
        is_upload_connection_healthy: bool = cache_connections_health[1]

        is_query_session_healthy: bool = users_connection_manager._check_query_session_health()

        if is_download_connection_healthy is False:
            logging.warning("cache download connection isn't healthy")
            are_databses_healty = False

        if is_upload_connection_healthy is False:
            logging.warning("cache upload connection isn't healthy")
            are_databses_healty = False

        if is_query_session_healthy is False:
            logging.warning("users query session isn't healthy")
            are_databses_healty = False

        health_check_response.redisDownloadConnection = is_download_connection_healthy
        health_check_response.redisUploadConnection = is_upload_connection_healthy
        health_check_response.postgresQuerySession = is_query_session_healthy
        health_check_response.allConnectionsOk = are_databses_healty

        health_check_response.memoryUsage = psutil.virtual_memory().percent
        health_check_response.cpuUsage = psutil.cpu_percent()

        logging.info("all databases are healthy")

        return health_check_response


health_check_service: HealthCheckService = HealthCheckService()
