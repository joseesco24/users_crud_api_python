# ** info: python imports
import logging

# ** info: typing imports
from typing import List

# ** info: cache tools
from asyncache import cached

# ** info: users dtos imports
from src.dtos.users_dtos import UserFullDto
from src.dtos.users_dtos import UserPubDto

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
    async def users_full_resolver(self, limit: int, offset: int) -> List[UserFullDto]:
        """users_full_resolver

        usersFull root resolver

        """

        logging.debug("starting usersFull resolver method")

        response: List[UserFullDto] = users_provider.fetch_users_full_data(
            limit=limit, offset=offset
        )

        logging.debug("ending usersFull resolver method")

        return response

    @cached(cache=cache_manager.ttl_cache)
    async def users_pub_resolver(self, limit: int, offset: int) -> List[UserPubDto]:
        """users_pub_resolver

        usersPub root resolver

        """

        logging.debug("starting usersPub resolver method")

        response: List[UserPubDto] = users_provider.fetch_users_pub_data(
            limit=limit, offset=offset
        )

        logging.debug("ending usersPub resolver method")

        return response


users_resolvers: UsersResolvers = UsersResolvers()
