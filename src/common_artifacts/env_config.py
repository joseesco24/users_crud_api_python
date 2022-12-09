#!/usr/bin/env python3

# ** info: python imports
from enum import Enum

# ** info: pydantic imports
from pydantic import BaseSettings
from pydantic import Field


__all__ = ["configs"]


class __environment_mode__(str, Enum):

    development: str = "development"
    production: str = "production"
    testing: str = "testing"


class EnvConfigs(BaseSettings):

    environment_mode: __environment_mode__ = Field(..., env="ENVIRONMENT_MODE")

    class Config:
        env_file = ".env"


env_configs: EnvConfigs = EnvConfigs()
