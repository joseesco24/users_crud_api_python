# ** info: python imports
from datetime import timedelta
from datetime import datetime

# ** info: cache tools
from cachetools import TTLCache

# ** info: artifacts imports
from src.artifacts.pattern.singleton import Singleton

# pylint: disable=unused-variable
__all__: list[str] = ["cache_manager"]


class CacheManager(metaclass=Singleton):
    # ** info: ttl cache implementation
    ttl_cache: TTLCache = TTLCache(
        maxsize=1024, ttl=timedelta(seconds=60), timer=datetime.utcnow
    )


cache_manager: CacheManager = CacheManager()
