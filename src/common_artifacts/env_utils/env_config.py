# ** info: python imports
from enum import Enum

# ** info: pydantic imports
from pydantic import BaseSettings
from pydantic import Field

# pylint: disable=unused-variable
__all__: list[str] = [r"env_configs"]


class EnvironmentMode(str, Enum):

    # pylint: disable=invalid-name
    development: str = r"development"

    # pylint: disable=invalid-name
    production: str = r"production"

    # pylint: disable=invalid-name
    testing: str = r"testing"


class EnvConfigs(BaseSettings):

    environment_mode: EnvironmentMode = Field(..., env=r"ENVIRONMENT_MODE")
    server_port: int = Field(..., env=r"SERVER_PORT")

    class Config:
        env_file = r".env"


env_configs: EnvConfigs = EnvConfigs()
