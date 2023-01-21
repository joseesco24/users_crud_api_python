# ** info: python imports
from enum import Enum

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


class Configs(BaseSettings):
    environment_mode: EnvironmentMode = Field(..., env="ENVIRONMENT_MODE")
    server_port: int = Field(..., env="SERVER_PORT")

    database_password: str = Field(..., env="DATABASE_PASSWORD")
    database_host: str = Field(..., env="DATABASE_HOST")
    database_name: str = Field(..., env="DATABASE_NAME")
    database_user: str = Field(..., env="DATABASE_USER")
    database_port: int = Field(..., env="DATABASE_PORT")

    cache_database_password: str = Field(..., env="CACHE_DATABASE_PASSWORD")
    cache_database_logs: bool = Field(..., env="CACHE_DATABASE_LOGS")
    cache_database_host: str = Field(..., env="CACHE_DATABASE_HOST")
    cache_database_name: str = Field(..., env="CACHE_DATABASE_NAME")
    cache_database_port: int = Field(..., env="CACHE_DATABASE_PORT")
    cache_ttl: int = Field(..., env="RESOLVERS_CACHE_TTL")

    resolvers_cache_size: int = Field(..., env="RESOLVERS_CACHE_SIZE")

    class Config:
        env_file = ".env"


configs: Configs = Configs()
