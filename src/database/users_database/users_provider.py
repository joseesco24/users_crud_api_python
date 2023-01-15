# ** info: typing imports
from typing import List
from typing import Any

# **info: sqlalchemy imports
from sqlalchemy import select

# **info: sqlalchemy orm imports
from sqlalchemy.orm import Session

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
    def add_user(
        self,
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
    ) -> UserPublicDto:
        user_public_data: UserPublicDto = UserPublicDto

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

        session: Session = connection_manager.get_session()
        session.add(new_user)
        session.flush()

        user_public_data = self._users_entity_to_users_public_dto(user=new_user)

        return user_public_data

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
