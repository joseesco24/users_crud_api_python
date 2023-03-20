# ** info: python imports
import functools
import hashlib
import logging

# ** info: fastapi imports
from fastapi import HTTPException

# ** info: graphql imports
from graphql import GraphQLError

# ** info: typing imports
from typing import Callable
from typing import Union
from typing import Self
from typing import Any

# ** info: databases imports
from src.database.cache_database.connection_manager import connection_manager
from src.database.cache_database.connection_manager import ConnectionManager

# ** info: artifacts imports
from src.artifacts.pattern.singleton import Singleton

__all__: list[str] = ["cache_provider"]


class CacheProvider(metaclass=Singleton):
    def __init__(self: Self, cache_connection_manager: ConnectionManager):
        self._connection_manager: ConnectionManager = cache_connection_manager

    def ttl_cache(self: Self, ttl: Union[int, None] = None) -> Any:
        def decorator(func: Callable) -> Callable:
            async def cache_wrapper(*args, **kwargs) -> Any:
                # ** info: generation function key
                key: str = hashlib.sha256((func.__name__ + str(args) + str(kwargs)).encode()).hexdigest()

                # ** info: searching key in the cache database
                cached_value: Union[None, Any] = await self._connection_manager.get(key=key)

                if cached_value is not None:
                    logging.info("returning requested value from redis cache")
                    return cached_value

                # ** info: executing the function
                try:
                    value: Any = await func(*args, **kwargs)

                    # ** info: storing the value in the cache database
                    if ttl is None:
                        await self._connection_manager.set_with_ttl(key=key, value=value)
                    else:
                        await self._connection_manager.set_with_ttl(key=key, value=value, time=ttl)

                    # ** info: returning
                    return value

                except HTTPException as error:
                    raise HTTPException(status_code=error.status_code, detail=error.detail)

                except GraphQLError as error:
                    raise GraphQLError(message=error.message, extensions=error.extensions)

            return functools.wraps(func)(cache_wrapper)

        return decorator


cache_provider: CacheProvider = CacheProvider(cache_connection_manager=connection_manager)
