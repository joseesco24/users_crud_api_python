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
from src.dtos.tv_programmation_dtos import TvProgrammationSearchResponsePrettyReturnDto
from src.dtos.tv_programmation_dtos import TvProgrammationSearchResponseRawReturnDto
from src.dtos.tv_programmation_dtos import TvProgrammationSearchRequestDto
from src.dtos.tv_programmation_dtos import TvProgrammationAddRequestDto
from src.dtos.tv_programmation_dtos import TvProgrammationResponseDto

# ** info: rest controllers imports
from rest_controllers.tv_channel_controller import tv_channel_controller

__all__: list[str] = ["tv_channel_router"]

tv_channel_router: APIRouter = APIRouter(prefix=generator.build_posix_path("tv-channel", "programmation"))


@tv_channel_router.post(
    path=generator.build_posix_path("search-programmation-raw-return"),
    response_model=TvProgrammationSearchResponseRawReturnDto,
    status_code=status.HTTP_200_OK,
)
async def search_tv_programattion_raw_return(
    tv_programmation_search_request: TvProgrammationSearchRequestDto = Body(...),
) -> List[TvProgrammationResponseDto]:
    tv_programmation_response: List[TvProgrammationResponseDto] = await tv_channel_controller.search_tv_programattion(tv_programmation_search_request)
    for program in tv_programmation_response:
        program.duration = _minutos_entre_horas(program.startHoure, program.endHoure)
    return {"data": tv_programmation_response}


@tv_channel_router.post(
    path=generator.build_posix_path("search-programmation-pretty-return"),
    response_model=TvProgrammationSearchResponsePrettyReturnDto,
    status_code=status.HTTP_200_OK,
)
async def search_tv_programattion_pretty_return(
    tv_programmation_search_request: TvProgrammationSearchRequestDto = Body(...),
) -> List[TvProgrammationResponseDto]:
    tv_programmation_response: List[TvProgrammationResponseDto] = await tv_channel_controller.search_tv_programattion(tv_programmation_search_request)
    pretty_response: List[str] = list(map(lambda data: f"{data.channelName} de {data.startHoure} a de {data.endHoure}", tv_programmation_response))
    return {"data": pretty_response}


@tv_channel_router.post(
    path=generator.build_posix_path("add-programmation"),
    response_model=TvProgrammationResponseDto,
    status_code=status.HTTP_200_OK,
)
async def add_tv_programattion(tv_programmation_add_request: TvProgrammationAddRequestDto = Body(...)) -> TvProgrammationResponseDto:
    tv_programmation_response: TvProgrammationResponseDto = await tv_channel_controller.add_tv_programattion(tv_programmation_add_request)
    tv_programmation_response.duration = _minutos_entre_horas(tv_programmation_response.startHoure, tv_programmation_response.endHoure)
    return tv_programmation_response


def _minutos_entre_horas(hora1, hora2):
    hh1, mm1, ss1 = map(int, hora1.split(":"))
    hh2, mm2, ss2 = map(int, hora2.split(":"))
    minutos1 = hh1 * 60 + mm1 + ss1 / 60
    minutos2 = hh2 * 60 + mm2 + ss2 / 60
    diferencia = abs(minutos1 - minutos2)
    return int(diferencia)
