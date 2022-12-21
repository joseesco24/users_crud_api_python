#!/usr/bin/env python3

# ** info: python imports
from enum import Enum

# ** info: pydantic imports
from pydantic import BaseSettings
from pydantic import Field

# pylint: disable=unused-variable
__all__: list[str] = ["env_configs"]


class EnvironmentMode(str, Enum):

    # pylint: disable=invalid-name
    development: str = "development"
    # pylint: disable=invalid-name
    production: str = "production"
    # pylint: disable=invalid-name
    testing: str = "testing"


class EnvConfigs(BaseSettings):

    environment_mode: EnvironmentMode = Field(..., env="ENVIRONMENT_MODE")
    server_port: int = Field(..., env="SERVER_PORT")

    class Config:
        env_file = ".env"


env_configs: EnvConfigs = EnvConfigs()
