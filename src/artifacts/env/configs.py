# !/usr/bin/python3
# type: ignore

# ** info: python imports
from enum import Enum

# ** info: typing imports
from typing import Set

# ** info: pydantic imports
from pydantic_settings import BaseSettings
from pydantic import Field

__all__: list[str] = ["configs"]


class EnvironmentMode(str, Enum):
    development: str = "development"
    production: str = "production"
    testing: str = "testing"


class LoggingMode(str, Enum):
    structured: str = "structured"
    pretty: str = "pretty"


class Configs(BaseSettings):
    # ** info: app configs
    app_environment_mode: EnvironmentMode = Field(..., env="APP_ENVIRONMENT_MODE")
    app_logging_mode: LoggingMode = Field(..., env="APP_LOGGING_MODE")
    app_server_port: int = Field(..., env="APP_SERVER_PORT")
    app_database_health_check_middleware_exclude: Set[str] = Field(..., env="APP_DATABASE_HEALTH_CHECK_MIDDLEWARE_EXCLUDE")
    app_use_database_health_check_middleware: bool = Field(..., env="APP_USE_DATABASE_HEALTH_CHECK_MIDDLEWARE")
    app_authentication_handler_middleware_exclude: Set[str] = Field(..., env="APP_AUTHENTICATION_HANDLER_MIDDLEWARE_EXCLUDE")
    app_use_authentication_handler_middleware: bool = Field(..., env="APP_USE_AUTHENTICATION_HANDLER_MIDDLEWARE")

    # ** info: users database credentials
    database_password: str = Field(..., env="DATABASE_PASSWORD")
    database_logs: bool = Field(..., env="DATABASE_LOGS")
    database_host: str = Field(..., env="DATABASE_HOST")
    database_name: str = Field(..., env="DATABASE_NAME")
    database_user: str = Field(..., env="DATABASE_USER")
    database_port: int = Field(..., env="DATABASE_PORT")

    # ** info: cache database credentials
    cache_database_default_ttl: int = Field(..., env="CACHE_DATABASE_DEFAULT_TTL")
    cache_database_password: str = Field(..., env="CACHE_DATABASE_PASSWORD")
    cache_database_logs: bool = Field(..., env="CACHE_DATABASE_LOGS")
    cache_database_host: str = Field(..., env="CACHE_DATABASE_HOST")
    cache_database_name: str = Field(..., env="CACHE_DATABASE_NAME")
    cache_database_port: int = Field(..., env="CACHE_DATABASE_PORT")

    class Config:
        env_file = ".env"


configs: Configs = Configs()
