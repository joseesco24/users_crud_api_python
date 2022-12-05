# Python
from os.path import join
from os import environ
from os import path
import logging
import sys

# **info: appending src path to the system paths for absolute imports from src modules
sys.path.append(join(path.dirname(path.realpath(__file__)), "..", "."))

# Uvicorn
import uvicorn

# Starlette
from starlette.middleware.base import BaseHTTPMiddleware

# FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

# Routers
from core_modules.users.controllers.controller import users_controller

# Middlewares
from src.common_modules.middlewares.error_handler import error_handler_middleware
from src.common_modules.middlewares.logger import logging_middleware

from src.artifacts.logger import setup_logging

setup_logging()

from src.artifacts.config import configs

app = FastAPI()

#app.add_middleware(BaseHTTPMiddleware, dispatch=error_handler_middleware)
#app.add_middleware(BaseHTTPMiddleware, dispatch=logging_middleware)

app.add_middleware(CORSMiddleware)

app.include_router(users_controller)

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

uvicorn_server_configs = {
    "port": int(environ.get("PORT")) if environ.get("PORT") is not None else 10048,
    "log_level": "error" if configs.environment_mode == "production" else "debug",
    "app": app if configs.environment_mode == "production" else "main:app",
    "reload": False if configs.environment_mode == "production" else True,
    "access_log": False,
    "use_colors": False,
}

if __name__ == "__main__":
    uvicorn.run(**uvicorn_server_configs)
