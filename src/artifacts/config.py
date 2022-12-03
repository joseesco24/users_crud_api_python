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


class __storage_mode__(str, Enum):

    local: str = "local"
    gcs: str = "gcs"


class __configs__(BaseSettings):

    # Environment configs.
    environment_mode: __environment_mode__ = Field(..., env="ENVIRONMENT_MODE")

    # Storage mode.
    storage_mode: __storage_mode__ = Field(..., env="STORAGE_MODE")

    # GCS configs.
    gcs_bucket_name: str = Field(..., env="GCS_BUCKET_NAME")

    transactional_files_folder_paths: list[str] = Field(
        ..., env="TRANSACTIONAL_FILES_FOLDER_PATHS"
    )

    configuration_files_folder_path: str = Field(
        ..., env="CONFIGURATION_FILES_FOLDER_PATH"
    )

    # Integrations.
    logger_service_url: HttpUrl = Field(..., env="LOGGER_SERVICE_URL")

    class Config:
        env_file = ".env"


configs: __configs__ = __configs__()
