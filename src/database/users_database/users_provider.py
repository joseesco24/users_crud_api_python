# ** info: typing imports
from typing import List
from typing import Self
from typing import Any

# **info: sqlalchemy imports
from sqlalchemy import select

# ** info: users entity
from src.entities.users_entity import Users

# ** info: users dtos imports
from src.dtos.users_dtos import UserDto

# ** info: users database connection manager import
from src.database.users_database.connection_manager import CrudManagedSession
from src.database.users_database.connection_manager import connection_manager

# ** info: artifacts imports
from src.artifacts.pattern.singleton import Singleton

# pylint: disable=unused-variable
__all__: list[str] = ["users_provider"]


class UsersProvider(metaclass=Singleton):
    def add_user(
        self: Self,
        internal_id: str,
        estatal_id: int,
        first_name: str,
        last_name: str,
        phone_number: int,
        email: str,
        gender: str,
        birthday: str,
        creation: str,
        modification: str,
        password: str,
    ) -> UserDto:
        user_dto: UserDto = UserDto()

        new_user: Users = Users(
            internal_id=internal_id,
            estatal_id=estatal_id,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            email=email,
            gender=gender,
            birthday=birthday,
            creation=creation,
            modification=modification,
            password=password,
        )

        user_dto: UserDto = self._users_entity_to_users_public_dto(user=new_user)

        with CrudManagedSession() as crud_session:
            crud_session.add(new_user)

        return user_dto

    def fetch_users_data(self: Self, limit: int, offset: int) -> List[UserDto]:
        users_data: List[UserDto] = list()

        query: Any = (
            select(
                Users.internal_id,
                Users.estatal_id,
                Users.first_name,
                Users.last_name,
                Users.phone_number,
                Users.email,
                Users.gender,
                Users.birthday,
            )
            .select_from(Users)
            .order_by(Users.creation.desc())
            .limit(limit)
            .offset(offset)
        )

        results: List[Users] = connection_manager.get_query_session().execute(statement=query)

        users_data = list(map(self._users_entity_to_users_public_dto, results))

        return users_data

    def _users_entity_to_users_public_dto(self: Self, user: Users) -> UserDto:
        user_dto: UserDto = UserDto()

        user_dto.internalId = str(user.internal_id)
        user_dto.estatalId = str(user.estatal_id)
        user_dto.firstName = str(user.first_name)
        user_dto.lastName = str(user.last_name)
        user_dto.phoneNumber = int(user.phone_number)
        user_dto.email = str(user.email)
        user_dto.gender = str(user.gender)
        user_dto.birthday = str(user.birthday)

        return user_dto


users_provider: UsersProvider = UsersProvider()
