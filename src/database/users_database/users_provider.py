# ** info: typing imports
from typing import List
from typing import Any

# **info: sqlalchemy imports
from sqlalchemy import select

# ** info: users entity
from src.entities.users_entity import Users

# ** info: users dtos imports
from src.dtos.users_dtos import UserPublicDto
from src.dtos.users_dtos import UserFullDto

# ** info: users database connection manager import
from src.database.users_database.connection_manager import connection_manager

# ** info: artifacts imports
from src.artifacts.pattern.singleton import Singleton

# pylint: disable=unused-variable
__all__: list[str] = ["users_provider"]


class UsersProvider(metaclass=Singleton):
    def fetch_users_full_data(self, limit: int, offset: int) -> List[UserFullDto]:
        users_full_data: List[UserFullDto] = list()

        query: Any = (
            select(
                [
                    Users.internal_id,
                    Users.estatal_id,
                    Users.first_name,
                    Users.last_name,
                    Users.phone_number,
                    Users.email,
                    Users.gender,
                    Users.birthday,
                    Users.creation,
                    Users.modification,
                    Users.password,
                ]
            )
            .select_from(Users)
            .order_by(Users.creation.desc())
            .limit(limit)
            .offset(offset)
        )

        results: List[Users] = connection_manager.get_session().execute(statement=query)

        users_full_data = list(map(self._users_entity_to_users_full_dto, results))

        return users_full_data

    def _users_entity_to_users_full_dto(self, user: Users) -> UserFullDto:
        users_full_dto: UserFullDto = UserFullDto()

        users_full_dto.internalId = str(user.internal_id)
        users_full_dto.estatalId = str(user.estatal_id)
        users_full_dto.firstName = str(user.first_name)
        users_full_dto.lastName = str(user.last_name)
        users_full_dto.phoneNumber = int(user.phone_number)
        users_full_dto.email = str(user.email)
        users_full_dto.gender = str(user.gender)
        users_full_dto.birthday = str(user.birthday)
        users_full_dto.creation = str(user.creation)
        users_full_dto.modification = str(user.modification)
        users_full_dto.password = str(user.password)

        return users_full_dto

    def fetch_users_public_data(self, limit: int, offset: int) -> List[UserPublicDto]:
        users_pub_data: List[UserPublicDto] = list()

        query: Any = (
            select(
                [
                    Users.internal_id,
                    Users.estatal_id,
                    Users.first_name,
                    Users.last_name,
                    Users.phone_number,
                    Users.email,
                    Users.gender,
                    Users.birthday,
                ]
            )
            .select_from(Users)
            .order_by(Users.creation.desc())
            .limit(limit)
            .offset(offset)
        )

        results: List[Users] = connection_manager.get_session().execute(statement=query)

        users_pub_data = list(map(self._users_entity_to_users_public_dto, results))

        return users_pub_data

    def _users_entity_to_users_public_dto(self, user: Users) -> UserPublicDto:
        users_pub_dto: UserPublicDto = UserPublicDto()

        users_pub_dto.internalId = str(user.internal_id)
        users_pub_dto.estatalId = str(user.estatal_id)
        users_pub_dto.firstName = str(user.first_name)
        users_pub_dto.lastName = str(user.last_name)
        users_pub_dto.phoneNumber = int(user.phone_number)
        users_pub_dto.email = str(user.email)
        users_pub_dto.gender = str(user.gender)
        users_pub_dto.birthday = str(user.birthday)

        return users_pub_dto


users_provider: UsersProvider = UsersProvider()
