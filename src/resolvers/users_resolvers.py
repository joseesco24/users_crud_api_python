# ** info: python imports
import logging

# ** info: typing imports
from typing import List

# ** info: cache tools
from asyncache import cached

# ** info: users dtos imports
from src.dtos.users_dtos import UserPublicDto
from src.dtos.users_dtos import UserFullDto

# ** info: users provider import
from src.database.users_database.users_provider import users_provider

# ** info: resolvers cache
from src.resolvers.cache_manager import cache_manager

# ** info: artifacts imports
from src.artifacts.datetime.datetime_provider import datetime_provider
from src.artifacts.uuid.uuid_provider import uuid_provider
from src.artifacts.pattern.singleton import Singleton

# pylint: disable=unused-variable
__all__: list[str] = ["users_resolvers"]


class UsersResolvers(metaclass=Singleton):
    async def add_user_resolver(
        self,
        estatal_id: int,
        first_name: str,
        last_name: str,
        phone_number: int,
        email: str,
        gender: str,
        birthday: str,
        password: str,
    ) -> List[UserFullDto]:
        """add_user_resolver

        usersFullData root resolver

        """

        logging.debug("starting usersFullData resolver method")

        modification: str = datetime_provider.get_utc_iso_string()
        creation: str = datetime_provider.get_utc_iso_string()
        internal_id: str = uuid_provider.get_str_uuid()

        response: List[UserFullDto] = users_provider.add_user(
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

        logging.debug("ending usersFullData resolver method")

        return response

    @cached(cache=cache_manager.ttl_cache)
    async def users_full_data_resolver(
        self, limit: int, offset: int
    ) -> List[UserFullDto]:
        """users_full_data_resolver

        usersFullData root resolver

        """

        logging.debug("starting usersFullData resolver method")

        response: List[UserFullDto] = users_provider.fetch_users_full_data(
            limit=limit, offset=offset
        )

        logging.debug("ending usersFullData resolver method")

        return response

    @cached(cache=cache_manager.ttl_cache)
    async def users_public_data_resolver(
        self, limit: int, offset: int
    ) -> List[UserPublicDto]:
        """users_public_data_resolver

        usersPublicData root resolver

        """

        logging.debug("starting usersPublicData resolver method")

        response: List[UserPublicDto] = users_provider.fetch_users_public_data(
            limit=limit, offset=offset
        )

        logging.debug("ending usersPublicData resolver method")

        return response


users_resolvers: UsersResolvers = UsersResolvers()
