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
from src.artifacts.pattern.singleton import Singleton

# pylint: disable=unused-variable
__all__: list[str] = ["users_resolvers"]


class UsersResolvers(metaclass=Singleton):
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
