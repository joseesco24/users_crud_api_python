# !/usr/bin/python3
# type: ignore

# ** info: python imports
import logging

# ** info: graphql imports
# from graphql import GraphQLErrorExtensions
# from graphql import GraphQLError
# extensions: GraphQLErrorExtensions = {"code": "E001", "confirmation": "G"}
# raise GraphQLError(message="aaaa", extensions=extensions)

# ** info: typing imports
from typing import Union
from typing import List
from typing import Self

# ** info: users dtos imports
from src.dtos.users_dtos import UserDto

# ** info: users provider import
from src.database.users_database.users_provider import users_provider

# ** info: resolvers cache
from src.database.cache_database.cache_provider import cache_provider

# ** info: artifacts imports
from src.artifacts.datetime.datetime_provider import datetime_provider
from src.artifacts.uuid.uuid_provider import uuid_provider
from src.artifacts.pattern.singleton import Singleton

__all__: list[str] = ["users_resolvers"]


class UsersResolvers(metaclass=Singleton):
    async def add_user_resolver(
        self: Self,
        estatal_id: int,
        first_name: str,
        last_name: str,
        phone_number: int,
        email: str,
        gender: str,
        birthday: str,
        password: str,
    ) -> UserDto:
        """add_user_resolver

        usersFullData root resolver

        """

        logging.debug("starting usersFullData resolver method")

        modification: str = datetime_provider.get_utc_iso_string()
        creation: str = datetime_provider.get_utc_iso_string()
        internal_id: str = uuid_provider.get_str_uuid()

        first_name = first_name.lower()
        last_name = last_name.lower()

        response: UserDto = users_provider.add_user(
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

    @cache_provider.ttl_cache(ttl=120)
    async def users_resolver(
        self: Self,
        limit: int,
        offset: int,
        internal_id: Union[None, str],
        estatal_id: Union[None, int],
        first_name: Union[None, str],
        last_name: Union[None, str],
        phone_number: Union[None, int],
        email: Union[None, str],
        gender: Union[None, str],
        birthday: Union[None, str],
    ) -> List[UserDto]:
        """users_resolver

        users root resolver

        """

        logging.debug("starting users resolver method")

        response: List[UserDto] = users_provider.fetch_users_data(
            limit=limit,
            offset=offset,
            internal_id=internal_id,
            estatal_id=estatal_id,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            email=email,
            gender=gender,
            birthday=birthday,
        )

        logging.debug("ending users resolver method")

        return response


users_resolvers: UsersResolvers = UsersResolvers()
