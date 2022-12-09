#!/usr/bin/env python3

# ** info: python imports
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

# ** info: routers imports
from core_modules.users.controllers.controller import users_controller

from src.artifacts.logger import custom_logger

from src.artifacts.config import configs

# ---------------------------------------------------------------------------------------------------------------------
# ** info: initializing app dependencies
# ---------------------------------------------------------------------------------------------------------------------

app: FastAPI = FastAPI()

# ---------------------------------------------------------------------------------------------------------------------
# ** info: setting up global app logging
# ---------------------------------------------------------------------------------------------------------------------

if configs.environment_mode == "production":
    custom_logger.setup_production_logging()
    logging.info(f"logger setup on {configs.environment_mode} mode")
else:
    custom_logger.setup_development_logging()
    logging.info(f"logger setup on {configs.environment_mode} mode")

# ---------------------------------------------------------------------------------------------------------------------
# ** info: setting up app routers and middlewares
# ---------------------------------------------------------------------------------------------------------------------

app.add_middleware(CORSMiddleware)

app.include_router(users_controller)

# ---------------------------------------------------------------------------------------------------------------------
# ** info: disabling uvicorn access and error logs on production mode
# ---------------------------------------------------------------------------------------------------------------------

uvicorn_access = logging.getLogger("uvicorn.access")
uvicorn_error = logging.getLogger("uvicorn.error")

if configs.environment_mode == "production":
    uvicorn_access.disabled = True
    uvicorn_error.disabled = True
else:
    uvicorn_access.disabled = False
    uvicorn_error.disabled = False

if __name__ == "__main__":
    logging.info(f"application started in {configs.environment_mode} mode")

if __name__ != "__main__":
    logging.info(f"application reloaded in {configs.environment_mode} mode")

# ---------------------------------------------------------------------------------------------------------------------
# ** info: setting up uvicorn asgi server with fast api app
# ---------------------------------------------------------------------------------------------------------------------

application_port: int = (
    int(environ.get("PORT")) if environ.get("PORT") is not None else 10048
)

uvicorn_server_configs = {
    "app": app if configs.environment_mode == "production" else "main:app",
    "reload": False if configs.environment_mode == "production" else True,
    "port": application_port,
    "log_level": "warning",
    "access_log": False,
    "use_colors": False,
    "host": "0.0.0.0"
}

logging.info(f"application starting on port {application_port}")

# ---------------------------------------------------------------------------------------------------------------------
# ** info: running app using the previous uvicorn asgi server settings
# ---------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    uvicorn.run(**uvicorn_server_configs)
