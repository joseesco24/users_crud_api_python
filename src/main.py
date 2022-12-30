# ** info: python imports
from logging import Logger
from os.path import join
from os import environ
from os import path
import logging
import sys

# ** info: typing imports
from typing import List

# **info: appending src path to the system paths for absolute imports from src path
sys.path.append(join(path.dirname(path.realpath(__file__)), "..", "."))

# ** info: uvicorn imports
import uvicorn

# ** info: fastapi imports
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

# ** info: starlette imports
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.routing import BaseRoute

# ** info: routers imports
from core_modules.users.routers.router import users_router

# ** info: common artifacts imports
from src.common_artifacts.logging_utils.custom_logger import custom_logger
from src.common_artifacts.middlewares.error_handler import error_handler
from src.common_artifacts.env_utils.env_config import env_configs

# ---------------------------------------------------------------------------------------------------------------------
# ** info: initializing app routers
# ---------------------------------------------------------------------------------------------------------------------

routers: List[BaseRoute] = [users_router]

# ---------------------------------------------------------------------------------------------------------------------
# ** info: initializing app dependencies and mounting routes
# ---------------------------------------------------------------------------------------------------------------------

app: FastAPI = FastAPI(routes=routers)

# ---------------------------------------------------------------------------------------------------------------------
# ** info: setting up global app logging
# ---------------------------------------------------------------------------------------------------------------------

if env_configs.environment_mode == "production":
    custom_logger.setup_production_logging()
    logging.info(f"logger setup on {env_configs.environment_mode} mode")
else:
    custom_logger.setup_development_logging()
    logging.info(f"logger setup on {env_configs.environment_mode} mode")

# ---------------------------------------------------------------------------------------------------------------------
# ** info: setting up app middlewares
# ---------------------------------------------------------------------------------------------------------------------

app.add_middleware(CORSMiddleware)

app.add_middleware(BaseHTTPMiddleware, dispatch=error_handler)

# ---------------------------------------------------------------------------------------------------------------------
# ** info: disabling uvicorn access and error logs on production mode
# ---------------------------------------------------------------------------------------------------------------------

uvicorn_access: Logger = logging.getLogger("uvicorn.access")
uvicorn_error: Logger = logging.getLogger("uvicorn.erro")

if env_configs.environment_mode == "production":
    uvicorn_access.disabled = True
    uvicorn_error.disabled = True
else:
    uvicorn_access.disabled = False
    uvicorn_error.disabled = False

if __name__ == "__main__":
    logging.info(f"application started in {env_configs.environment_mode} mode")

if __name__ != "__main__":
    logging.info(f"application reloaded in {env_configs.environment_mode} mode")

# ---------------------------------------------------------------------------------------------------------------------
# ** info: setting up uvicorn asgi server with fast api app
# ---------------------------------------------------------------------------------------------------------------------

application_port: int = (
    int(environ.get("SERVER_PORT")) if environ.get("SERVER_PORT") is not None else 10048
)

uvicorn_server_configs: dict[str, any] = {
    "app": app if env_configs.environment_mode == "production" else "main:app",
    "reload": False if env_configs.environment_mode == "production" else True,
    "port": application_port,
    "log_level": "warning",
    "access_log": False,
    "use_colors": False,
    "host": "0.0.0.0",
}

logging.info(f"application starting on port {application_port}")

# ---------------------------------------------------------------------------------------------------------------------
# ** info: running app using the previous uvicorn asgi server settings
# ---------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    uvicorn.run(**uvicorn_server_configs)

if env_configs.environment_mode == "production":
    logging.debug("application ended")
