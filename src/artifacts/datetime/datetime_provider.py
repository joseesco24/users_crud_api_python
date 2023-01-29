# ** info: python imports
from datetime import timedelta
from datetime import datetime

# ** info: artifacts imports
from src.artifacts.pattern.singleton import Singleton

# pylint: disable=unused-variable
__all__: list[str] = ["datetime_provider"]


class DatetimeProvider(metaclass=Singleton):
    def get_utc_time(self) -> datetime:
        return datetime.utcnow()

    def get_utc_pretty_string(self) -> str:
        return self.prettify_date_time_obj(date_time_obj=self.get_utc_time())

    def get_utc_iso_string(self) -> str:
        return self.get_utc_time().isoformat()

    def prettify_date_time_obj(self, date_time_obj: datetime) -> str:
        return date_time_obj.strftime("%Y-%m-%d %H:%M:%S.%f")

    def prettify_time_delta_obj(self, time_delta_obj: timedelta) -> str:
        delta_days: int = time_delta_obj.days
        delta_houres: int = time_delta_obj.seconds // 3600
        delta_minutes: int = time_delta_obj.seconds % 3600 // 60
        delta_seconds: int = time_delta_obj.seconds % 3600 % 60

        return f"{delta_days} days {delta_houres} houres {delta_minutes} minutes {delta_seconds} seconds"


datetime_provider: DatetimeProvider = DatetimeProvider()
