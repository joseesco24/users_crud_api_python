# ** info: python imports
from uuid import UUID
import uuid

# ** info: artifacts imports
from src.artifacts.pattern.singleton import Singleton

# pylint: disable=unused-variable
__all__: list[str] = ["uuid_provider"]


class UuidProvider(metaclass=Singleton):
    def get_str_uuid(self) -> UUID:
        return str(uuid.uuid4())


uuid_provider: UuidProvider = UuidProvider()
