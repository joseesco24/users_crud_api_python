"""main.py

this module is the incharge of assemble and execute the app

"""

# ** info: python imports
from logging import Logger
from os.path import join
from os import path
import logging
import sys

# ** info: typing imports
from typing import Dict
from typing import List
from typing import Any

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

# ** info: rest based routers imports
from src.controllers.health_check import health_check_router

# ** info: graphql based routers imports
from src.main_router import main_router

# ** info: artifacts imports
from src.artifacts.logging.custom_logger import custom_logger
from src.artifacts.env.configs import configs

# ** info: middlewares imports
from src.middlewares.database_health_check import database_health_check
from src.middlewares.logger_contextualizer import logger_contextualizer
from src.middlewares.error_handler import error_handler


# ---------------------------------------------------------------------------------------------------------------------
# ** info: initializing app graphql based routers
# ---------------------------------------------------------------------------------------------------------------------

routers: List[BaseRoute] = [main_router]

# ---------------------------------------------------------------------------------------------------------------------
# ** info: initializing app dependencies and mounting graphql based routes
# ---------------------------------------------------------------------------------------------------------------------

app: FastAPI = FastAPI(routes=routers)

# ---------------------------------------------------------------------------------------------------------------------
# ** info: mounting rest based routes
# ---------------------------------------------------------------------------------------------------------------------

app.include_router(health_check_router)

# ---------------------------------------------------------------------------------------------------------------------
# ** info: setting up global app logging
# ---------------------------------------------------------------------------------------------------------------------

if configs.app_environment_mode == "production":
    custom_logger.setup_production_logging()
    logging.info(f"logger setup on {configs.app_environment_mode} mode")
else:
    custom_logger.setup_development_logging()
    logging.info(f"logger setup on {configs.app_environment_mode} mode")

# ---------------------------------------------------------------------------------------------------------------------
# ** info: setting up app middlewares
# ---------------------------------------------------------------------------------------------------------------------

if configs.app_use_database_health_check_middleware is True:
    logging.info("databases health check middleware active")
    app.add_middleware(BaseHTTPMiddleware, dispatch=database_health_check)

app.add_middleware(BaseHTTPMiddleware, dispatch=logger_contextualizer)
app.add_middleware(BaseHTTPMiddleware, dispatch=error_handler)

app.add_middleware(CORSMiddleware)

# ---------------------------------------------------------------------------------------------------------------------
# ** info: disabling uvicorn access and error logs on production mode
# ---------------------------------------------------------------------------------------------------------------------

uvicorn_access: Logger = logging.getLogger("uvicorn.access")
uvicorn_error: Logger = logging.getLogger("uvicorn.erro")

if configs.app_environment_mode == "production":
    uvicorn_access.disabled = True
    uvicorn_error.disabled = True
else:
    uvicorn_access.disabled = False
    uvicorn_error.disabled = False

if __name__ == "__main__":
    logging.info(f"application started in {configs.app_environment_mode} mode")

if __name__ != "__main__":
    logging.info(f"application reloaded in {configs.app_environment_mode} mode")

# ---------------------------------------------------------------------------------------------------------------------
# ** info: setting up uvicorn asgi server with fast api app
# ---------------------------------------------------------------------------------------------------------------------


uvicorn_server_configs: Dict[str, Any] = {
    "use_colors": False if configs.app_environment_mode == "production" else True,
    "app": app if configs.app_environment_mode == "production" else "main:app",
    "reload": False if configs.app_environment_mode == "production" else True,
    "reload_includes": ["*.py", "*.graphql"],
    "reload_excludes": ["*.pyc", "*.pyo"],
    "port": configs.app_server_port,
    "log_level": "warning",
    "access_log": False,
    "host": "0.0.0.0",
}

logging.info(f"application starting on port {configs.app_server_port}")

# ---------------------------------------------------------------------------------------------------------------------
# ** info: running app using the previous uvicorn asgi server settings
# ---------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    uvicorn.run(**uvicorn_server_configs)

if configs.app_environment_mode == "production":
    logging.debug("application ended")
