# !/usr/bin/python3
# type: ignore

# ** info: typing imports
from typing import List

# ** info: fastapi imports
from fastapi import APIRouter
from fastapi import status
from fastapi import Body

# ** info: artifacts imports
from src.artifacts.path.generator import generator

# ** info: health check dtos imports
from src.dtos.tv_programmation_dtos import TvProgrammationSearchRequestDto
from src.dtos.tv_programmation_dtos import TvProgrammationAddRequestDto
from src.dtos.tv_programmation_dtos import TvProgrammationResponseDto

# ** info: rest controllers imports
from rest_controllers.tv_channel_controller import tv_channel_controller

__all__: list[str] = ["tv_channel_router"]

tv_channel_router: APIRouter = APIRouter(prefix=generator.build_posix_path("tv-channel", "programmation"))


@tv_channel_router.get(
    path=generator.build_posix_path(""),
    response_model=List[TvProgrammationResponseDto],
    status_code=status.HTTP_200_OK,
)
async def search_tv_programattion(tv_programmation_search_request: TvProgrammationSearchRequestDto = Body(...)) -> List[TvProgrammationResponseDto]:
    tv_programmation_response: List[TvProgrammationResponseDto] = await tv_channel_controller.search_tv_programattion(tv_programmation_search_request)
    return tv_programmation_response


@tv_channel_router.post(
    path=generator.build_posix_path(""),
    response_model=TvProgrammationResponseDto,
    status_code=status.HTTP_200_OK,
)
async def add_tv_programattion(tv_programmation_add_request: TvProgrammationAddRequestDto = Body(...)) -> TvProgrammationResponseDto:
    tv_programmation_response: TvProgrammationResponseDto = await tv_channel_controller.add_tv_programattion(tv_programmation_add_request)
    return tv_programmation_response
