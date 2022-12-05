# Python
from enum import Enum

# Pydantic
from pydantic import BaseSettings
from pydantic import HttpUrl
from pydantic import Field


__all__ = ["configs"]


class __environment_mode__(str, Enum):

    development: str = "development"
    production: str = "production"
    testing: str = "testing"


class __configs__(BaseSettings):

    # Environment configs.
    environment_mode: __environment_mode__ = Field(..., env="ENVIRONMENT_MODE")

    class Config:
        env_file = ".env"


configs: __configs__ = __configs__()
