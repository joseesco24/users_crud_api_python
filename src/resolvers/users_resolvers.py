# ** info: python imports
import logging

# ** info: typing imports
from typing import List
from typing import Any

# ** info: cache tools
from asyncache import cached

# ** info: resolvers cache
from src.resolvers.cache_manager import cache_manager

# ** info: artifacts imports
from src.artifacts.pattern.singleton import Singleton

# pylint: disable=unused-variable
__all__: list[str] = ["users_resolvers"]

users: List[Any] = [
    {
        "internalId": "34d4a2b0-6c94-4a30-ba54-2346a2ddaf59",
        "estatalId": 9192562972,
        "firstName": "Arlin",
        "lastName": "Lenham",
        "phoneNumber": 2080650944,
        "email": "alenhamrp@ca.gov",
        "gender": "Male",
        "birthday": "2012/03/08",
        "creation": "2004-10-19 10:23:54+02",
        "modification": "2004-10-19 10:23:54+02",
        "password": "01f8e301011b8a4f6aeec3afb62a22246ed8d5bd879a81a69ea414ffb38cffac",
    },
    {
        "internalId": "fbab6f6b-f58f-4453-84b4-add51c4ef3ff",
        "estatalId": 7965738053,
        "firstName": "Reynolds",
        "lastName": "Ripon",
        "phoneNumber": 1090004661,
        "email": "rriponrr@answers.com",
        "gender": "Male",
        "birthday": "1984/03/10",
        "creation": "2004-10-19 10:23:54+02",
        "modification": "2004-10-19 10:23:54+02",
        "password": "6157a2fffccf919e70513c189d24b22cfde2c06f098a336162881fda99e9298d",
    },
    {
        "internalId": "8dd93284-c27e-46bc-b251-fb1a7a432aab",
        "estatalId": 2885926469,
        "firstName": "Dulcia",
        "lastName": "Dyos",
        "phoneNumber": 1090100667,
        "email": "ddyosrq@google.cn",
        "gender": "Female",
        "birthday": "2000/09/02",
        "creation": "2004-10-19 10:23:54+02",
        "modification": "2004-10-19 10:23:54+02",
        "password": "5fa8500e0b6e6b48e388ca31ac7da22fc0efc94d4c86c09ec6de8171c3e0c6b8",
    },
]


class UsersResolvers(metaclass=Singleton):
    @cached(cache=cache_manager.ttl_cache)
    async def users_full_resolver(self, limit: int, offset: int) -> List[Any]:
        """users_full_resolver

        usersFull root resolver

        """

        logging.debug("starting usersFull resolver method")

        response: List[Any] = users

        logging.debug("ending usersFull resolver method")

        return response

    @cached(cache=cache_manager.ttl_cache)
    async def users_pub_resolver(self, limit: int, offset: int) -> List[Any]:
        """users_pub_resolver

        usersPub root resolver

        """

        logging.debug("starting usersPub resolver method")

        response: List[Any] = users

        logging.debug("ending usersPub resolver method")

        return response


users_resolvers: UsersResolvers = UsersResolvers()
