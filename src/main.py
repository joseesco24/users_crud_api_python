# Python
from os.path import join
from os import environ
from os import path
import logging
import sys
import gc

# Uvicorn
import uvicorn

# Starlette
from starlette.middleware.base import BaseHTTPMiddleware

# FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import APIRouter
from fastapi import FastAPI

# Appending src path to the system paths for absolute imports from app modules
sys.path.append(join(path.dirname(path.realpath(__file__)), "..", "."))

# App Files
from src.commons.yaml_reader import yaml_reader
from src.commons.config import configs

# Commons
from src.commons.path_manager import build_posix_path
from src.commons.logger import setup_logging

# Custom Middlewares
from src.middlewares.error_handler import error_handler_middleware
from src.middlewares.logger import logging_middleware

# Routers
from src.routers.validation_router import validation_router
from src.routers.loading_router import loading_router


app_metadata = yaml_reader.get_app_metadata()

docs_url, redoc_url = None, None
if configs.environment_mode == "development":
    docs_url = build_posix_path("swagger", "apispec")
    redoc_url = build_posix_path("redoc", "apispec")

app = FastAPI(
    title=app_metadata["title"],
    description=app_metadata["description"],
    version=app_metadata["version"],
    openapi_tags=yaml_reader.get_tags_metadata(),
    redoc_url=redoc_url,
    docs_url=docs_url,
)

del app_metadata
gc.collect()

routers = [validation_router, loading_router]

main_router = APIRouter()

for router in routers:
    main_router.include_router(router)

del routers
gc.collect()

app.add_middleware(BaseHTTPMiddleware, dispatch=error_handler_middleware)
app.add_middleware(BaseHTTPMiddleware, dispatch=logging_middleware)
app.add_middleware(CORSMiddleware)

app.include_router(main_router)

setup_logging()

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
    "port": int(environ.get("PORT")) if environ.get("PORT") is not None else 3024,
    "log_level": "error" if configs.environment_mode == "production" else "debug",
    "app": app if configs.environment_mode == "production" else "main:app",
    "reload": False if configs.environment_mode == "production" else True,
    "access_log": False,
    "use_colors": False,
    "host": "0.0.0.0",
}

if __name__ == "__main__":
    uvicorn.run(**uvicorn_server_configs)
