#!/usr/bin/env python3

# ** info: python imports
import logging

# ** info: fastapi imports
from fastapi import APIRouter
from fastapi import status

from fastapi import Depends

# Commons
from src.artifacts.path_manager import build_posix_path

# Dtos
from src.core_modules.users.dtos.response_dto import ResponseDto
from src.core_modules.users.dtos.request_dto import RequestDto

__all__: list[str] = ["users_controller"]

users_controller: APIRouter = APIRouter(prefix=build_posix_path("users"))


@users_controller.get(
    response_model=ResponseDto,
    path=build_posix_path("data", "public"),
    status_code=status.HTTP_200_OK,
)
async def load_configuration_file(
    query: RequestDto = Depends(),
) -> ResponseDto:

    logging.debug("starting public data controller")

    logging.debug("ending public data controller")

    return ResponseDto(detail=f"{query.fileName} successfully validated")
