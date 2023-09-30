# !/usr/bin/python3
# type: ignore

# ** info: typing imports
from typing import Union
from typing import List
from typing import Self
from typing import Any

# **info: sqlalchemy imports
from sqlalchemy import select

# ** info: users entity
from src.entities.programmation_entity import TvProgramation

# ** info: users dtos imports
from src.dtos.tv_programmation_dtos import TvProgrammationResponseDto

# ** info: users database connection manager import
from src.database.postgres.connection_manager import CrudManagedSession

# ** info: artifacts imports
from src.artifacts.pattern.singleton import Singleton
from src.artifacts.env.configs import configs

__all__: list[str] = ["tv_programattion_provider"]


class TvProgramattionProvider(metaclass=Singleton):
    def __init__(self: Self):
        self.connection_manager: CrudManagedSession = CrudManagedSession(
            password=configs.tv_database_password,
            database=configs.tv_database_name,
            user=configs.tv_database_user,
            host=configs.tv_database_host,
            port=configs.tv_database_port,
            logs=configs.tv_database_logs,
        )

    def search_tv_programattion(
        self: Self,
        channel_id: Union[None, str],
        channel_name: Union[None, str],
        channel_content_type: Union[None, str],
        start_houre: Union[None, str],
        end_houre: Union[None, str],
        days: Union[None, List[int]],
        weeks: Union[None, List[int]],
        year: Union[None, int],
    ) -> List[TvProgrammationResponseDto]:
        search_tv_programmation_data: List[TvProgrammationResponseDto]

        query: Any = select(
            TvProgramation.channel_id,
            TvProgramation.channel_name,
            TvProgramation.channel_content_type,
            TvProgramation.start_houre,
            TvProgramation.end_houre,
            TvProgramation.days,
            TvProgramation.weeks,
            TvProgramation.year,
        )

        if channel_id is not None:
            query = query.where(TvProgramation.channel_id == channel_id)

        if channel_name is not None:
            query = query.where(TvProgramation.channel_name.like(f"{channel_name}%"))

        if channel_content_type is not None:
            query = query.where(TvProgramation.channel_content_type.like(f"{channel_content_type}%"))

        if start_houre is not None:
            query = query.where(TvProgramation.start_houre == start_houre)

        if end_houre is not None:
            query = query.where(TvProgramation.end_houre == end_houre)

        if year is not None:
            query = query.where(TvProgramation.year == year)

        query = query.order_by(TvProgramation.creation.desc())

        results: List[TvProgrammationResponseDto] = self.connection_manager.query_session.execute(statement=query)

        if days is not None:
            results = filter((lambda result: self._have_at_least_one_common_element(days, result.days)), results)

        if weeks is not None:
            results = filter((lambda result: self._have_at_least_one_common_element(weeks, result.weeks)), results)

        search_tv_programmation_data = list(map(self._tv_programation_entity_to_tv_programation_public_dto, results))

        return search_tv_programmation_data

    def add_tv_programattion(
        self: Self,
        programation_id: str,
        channel_id: int,
        channel_name: str,
        channel_content_type: str,
        start_houre: str,
        end_houre: str,
        weeks: List[int],
        days: List[int],
        year: int,
        modification: str,
        creation: str,
    ) -> TvProgrammationResponseDto:
        new_tv_programmation_data: TvProgrammationResponseDto

        new_tv_programation: TvProgramation = TvProgramation(
            programation_id=programation_id,
            channel_id=channel_id,
            channel_name=channel_name,
            channel_content_type=channel_content_type,
            start_houre=start_houre,
            end_houre=end_houre,
            weeks=weeks,
            days=days,
            year=year,
            modification=modification,
            creation=creation,
        )

        new_tv_programmation_data: TvProgrammationResponseDto = self._tv_programation_entity_to_tv_programation_public_dto(
            tv_programation=new_tv_programation
        )

        with self.connection_manager as crud_session:
            crud_session.add(new_tv_programation)

        return new_tv_programmation_data

    def _tv_programation_entity_to_tv_programation_public_dto(self: Self, tv_programation: TvProgramation) -> TvProgrammationResponseDto:
        tv_programmation_dto: TvProgrammationResponseDto = TvProgrammationResponseDto()

        tv_programmation_dto.channelId = int(tv_programation.channel_id)
        tv_programmation_dto.channelName = str(tv_programation.channel_name)
        tv_programmation_dto.channelContentType = str(tv_programation.channel_content_type)
        tv_programmation_dto.startHoure = str(tv_programation.start_houre)
        tv_programmation_dto.endHoure = str(tv_programation.end_houre)
        tv_programmation_dto.weeks = tv_programation.weeks
        tv_programmation_dto.days = tv_programation.days
        tv_programmation_dto.year = int(tv_programation.year)

        return tv_programmation_dto

    def _have_at_least_one_common_element(self: Self, array1: List[any], array2: List[any]) -> bool:
        for element in array1:
            if element in array2:
                return True
        return False


tv_programattion_provider: TvProgramattionProvider = TvProgramattionProvider()
