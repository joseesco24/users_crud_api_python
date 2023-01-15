# ** info: python imports
from datetime import datetime

# ** info: artifacts imports
from src.artifacts.pattern.singleton import Singleton

# pylint: disable=unused-variable
__all__: list[str] = ["datetime_provider"]


class DatetimeProvider(metaclass=Singleton):
    def get_utc_time(self) -> datetime:
        return datetime.utcnow()

    def get_utc_iso_string(self) -> str:
        return self.get_utc_time().isoformat()


datetime_provider: DatetimeProvider = DatetimeProvider()
