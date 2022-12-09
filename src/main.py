#!/usr/bin/env python3

# ** info: python imports
from logging import Logger
from os.path import join
from os import environ
from os import path
import logging
import sys

# **info: appending src path to the system paths for absolute imports from src path
sys.path.append(join(path.dirname(path.realpath(__file__)), "..", "."))

# ** info: uvicorn imports
import uvicorn

# ** info: fastapi imports
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

# ** info: starlette imports
from starlette.middleware.base import BaseHTTPMiddleware

# ** info: routers imports
from core_modules.users.controllers.controller import users_controller

# ** info: custom middlewares imports
from common_modules.custom_middlewares.error_handler import error_handler

# ** info: common artifacts imports
from src.common_artifacts.large_process_thread_admin import large_process_thread_admin
from src.common_artifacts.custom_logger import custom_logger
from src.common_artifacts.env_config import env_configs

# ---------------------------------------------------------------------------------------------------------------------
# ** info: initializing app dependencies
# ---------------------------------------------------------------------------------------------------------------------

app: FastAPI = FastAPI()

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
# ** info: setting up app routers and middlewares
# ---------------------------------------------------------------------------------------------------------------------

app.add_middleware(CORSMiddleware)
app.add_middleware(BaseHTTPMiddleware, dispatch=error_handler)

app.include_router(users_controller)

# ---------------------------------------------------------------------------------------------------------------------
# ** info: setting up app shutdown and startup subrutines
# ---------------------------------------------------------------------------------------------------------------------


@app.on_event("startup")
async def startup_event():
    large_process_thread_admin.start_large_process_thread_admin()


@app.on_event("shutdown")
def shutdown_event():
    large_process_thread_admin.end_large_process_thread_admin()


# ---------------------------------------------------------------------------------------------------------------------
# ** info: disabling uvicorn access and error logs on production mode
# ---------------------------------------------------------------------------------------------------------------------

uvicorn_access: Logger = logging.getLogger("uvicorn.access")
uvicorn_error: Logger = logging.getLogger("uvicorn.error")

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
    int(environ.get("PORT")) if environ.get("PORT") is not None else 10048
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
