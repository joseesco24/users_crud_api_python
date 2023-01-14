# ** info: typing imports
from typing import List
from typing import Any

# **info: sqlalchemy imports
from sqlalchemy import select

# ** info: users entity
from src.entities.users_entity import Users

# ** info: users dtos
from src.dtos.users_dtos import UserFullDto
from src.dtos.users_dtos import UserPubDto

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

        users_full_dto.internalId = user.internal_id
        users_full_dto.estatalId = user.estatal_id
        users_full_dto.firstName = user.first_name
        users_full_dto.lastName = user.last_name
        users_full_dto.phoneNumber = user.phone_number
        users_full_dto.email = user.email
        users_full_dto.gender = user.gender
        users_full_dto.birthday = user.birthday
        users_full_dto.creation = user.creation
        users_full_dto.modification = user.modification
        users_full_dto.password = user.password

        return users_full_dto

    def fetch_users_pub_data(self, limit: int, offset: int) -> List[UserPubDto]:
        users_pub_data: List[UserPubDto] = list()

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

        users_pub_data = list(map(self._users_entity_to_users_pub_dto, results))

        return users_pub_data

    def _users_entity_to_users_pub_dto(self, user: Users) -> UserPubDto:
        users_pub_dto: UserPubDto = UserPubDto()

        users_pub_dto.internalId = user.internal_id
        users_pub_dto.estatalId = user.estatal_id
        users_pub_dto.firstName = user.first_name
        users_pub_dto.lastName = user.last_name
        users_pub_dto.phoneNumber = user.phone_number
        users_pub_dto.email = user.email
        users_pub_dto.gender = user.gender
        users_pub_dto.birthday = user.birthday

        return users_pub_dto


users_provider: UsersProvider = UsersProvider()
