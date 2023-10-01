# !/usr/bin/python3
# type: ignore

# ** info: typing imports
from typing import Self
from typing import List

# ** info: artifacts imports
from src.artifacts.datetime.datetime_provider import datetime_provider
from src.artifacts.uuid.uuid_provider import uuid_provider
from src.artifacts.pattern.singleton import Singleton

# ** info: resolvers cache
from src.database.cache_database.cache_provider import cache_provider

# ** info: users provider import
from src.database.postgres.tv_channel_provider import tv_programattion_provider

# ** info: health check dtos imports
from src.dtos.tv_programmation_dtos import TvProgrammationSearchRequestDto
from src.dtos.tv_programmation_dtos import TvProgrammationAddRequestDto
from src.dtos.tv_programmation_dtos import TvProgrammationResponseDto

__all__: list[str] = ["tv_channel_controller"]


class HealthCheckController(metaclass=Singleton):
    @cache_provider.ttl_cache(ttl=30)
    async def search_tv_programattion(
        self: Self, tv_programmation_search_request: TvProgrammationSearchRequestDto
    ) -> List[TvProgrammationResponseDto]:
        search_tv_programmation_data: List[TvProgrammationResponseDto]

        search_tv_programmation_data = tv_programattion_provider.search_tv_programattion(
            channel_id=tv_programmation_search_request.channelId,
            channel_name=tv_programmation_search_request.channelName,
            channel_content_type=tv_programmation_search_request.channelContentType,
            start_houre=tv_programmation_search_request.startHoure,
            end_houre=tv_programmation_search_request.endHoure,
            days=tv_programmation_search_request.days,
            weeks=tv_programmation_search_request.weeks,
            year=tv_programmation_search_request.year,
        )

        return search_tv_programmation_data

    async def add_tv_programattion(self: Self, tv_programmation_add_request: TvProgrammationAddRequestDto) -> TvProgrammationResponseDto:
        new_tv_programmation_data: TvProgrammationResponseDto

        modification: str = datetime_provider.get_utc_iso_string()
        creation: str = datetime_provider.get_utc_iso_string()
        programation_id: str = uuid_provider.get_str_uuid()

        channel_name = tv_programmation_add_request.channelName.lower()
        channel_content_type = tv_programmation_add_request.channelContentType.lower()

        new_tv_programmation_data = tv_programattion_provider.add_tv_programattion(
            programation_id=programation_id,
            channel_id=tv_programmation_add_request.channelId,
            channel_name=channel_name,
            channel_content_type=channel_content_type,
            start_houre=tv_programmation_add_request.startHoure,
            end_houre=tv_programmation_add_request.endHoure,
            days=tv_programmation_add_request.days,
            weeks=tv_programmation_add_request.weeks,
            year=tv_programmation_add_request.year,
            modification=modification,
            creation=creation,
        )

        return new_tv_programmation_data


tv_channel_controller: HealthCheckController = HealthCheckController()
