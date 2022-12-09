#!/usr/bin/env python3

# ** info: python imports
import logging

# ** info: fastapi imports
from fastapi import APIRouter
from fastapi import status

from fastapi import Depends

# Commons
from src.common_artifacts.path_manager import path_manager

# Dtos
from src.core_modules.users.dtos.response_dto import ResponseDto
from src.core_modules.users.dtos.request_dto import RequestDto

__all__: list[str] = ["users_controller"]

users_controller: APIRouter = APIRouter(prefix=path_manager.build_posix_path("users"))


@users_controller.get(
    path=path_manager.build_posix_path("data", "public"),
    response_model=ResponseDto,
    status_code=status.HTTP_200_OK,
)
async def load_configuration_file(
    query: RequestDto = Depends(),
) -> ResponseDto:

    logging.debug("starting public data controller")

    logging.debug("ending public data controller")

    return ResponseDto(detail=f"{query.fileName} successfully validated")
