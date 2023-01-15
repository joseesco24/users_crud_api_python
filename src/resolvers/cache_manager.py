# ** info: python imports
from datetime import timedelta
from datetime import datetime

# ** info: cache tools
from cachetools import TTLCache

# ** info: artifacts imports
from src.artifacts.pattern.singleton import Singleton
from src.artifacts.env.configs import configs

# pylint: disable=unused-variable
__all__: list[str] = ["cache_manager"]


class CacheManager(metaclass=Singleton):
    def __init__(self) -> None:
        self.ttl_cache: TTLCache = TTLCache(
            ttl=timedelta(seconds=configs.resolvers_cache_ttl),
            maxsize=configs.resolvers_cache_size,
            timer=datetime.utcnow,
        )


cache_manager: CacheManager = CacheManager()
