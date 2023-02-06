# ** info: python imports
from enum import Enum

# ** info: typing imports
from typing import Set

# ** info: pydantic imports
from pydantic import BaseSettings
from pydantic import Field

# pylint: disable=unused-variable
__all__: list[str] = ["configs"]


class EnvironmentMode(str, Enum):
    # pylint: disable=invalid-name
    development: str = "development"

    # pylint: disable=invalid-name
    production: str = "production"

    # pylint: disable=invalid-name
    testing: str = "testing"


class LoggingMode(str, Enum):
    # pylint: disable=invalid-name
    structured: str = "structured"

    # pylint: disable=invalid-name
    pretty: str = "pretty"


class Configs(BaseSettings):
    app_environment_mode: EnvironmentMode = Field(..., env="APP_ENVIRONMENT_MODE")
    app_logging_mode: LoggingMode = Field(..., env="APP_LOGGING_MODE")
    app_server_port: int = Field(..., env="APP_SERVER_PORT")

    app_use_database_health_check_middleware_exclude: Set[str] = Field(
        ..., env="APP_USE_DATABASE_HEALTH_CHECK_MIDDLEWARE_EXCLUDE"
    )
    app_use_database_health_check_middleware: bool = Field(..., env="APP_USE_DATABASE_HEALTH_CHECK_MIDDLEWARE")

    database_password: str = Field(..., env="DATABASE_PASSWORD")
    database_logs: bool = Field(..., env="DATABASE_LOGS")
    database_host: str = Field(..., env="DATABASE_HOST")
    database_name: str = Field(..., env="DATABASE_NAME")
    database_user: str = Field(..., env="DATABASE_USER")
    database_port: int = Field(..., env="DATABASE_PORT")

    cache_database_default_ttl: int = Field(..., env="CACHE_DATABASE_DEFAULT_TTL")
    cache_database_password: str = Field(..., env="CACHE_DATABASE_PASSWORD")
    cache_database_logs: bool = Field(..., env="CACHE_DATABASE_LOGS")
    cache_database_host: str = Field(..., env="CACHE_DATABASE_HOST")
    cache_database_name: str = Field(..., env="CACHE_DATABASE_NAME")
    cache_database_port: int = Field(..., env="CACHE_DATABASE_PORT")

    class Config:
        env_file = ".env"


configs: Configs = Configs()
