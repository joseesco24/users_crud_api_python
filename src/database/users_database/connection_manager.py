# ** info: python imports
import logging
import gc

# ** info: typing imports
from typing import Union

# ** info: fastapi imports
from fastapi import HTTPException
from fastapi import status

# **info: sqlalchemy engine imports
from sqlalchemy.engine import Engine

# **info: sqlalchemy imports
from sqlalchemy import create_engine

# **info: sqlalchemy orm imports
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session

# **info: sqlalchemy exc imports
from sqlalchemy.exc import SQLAlchemyError

# ** info: artifacts imports
from src.artifacts.datetime.datetime_provider import datetime_provider
from src.artifacts.uuid.uuid_provider import uuid_provider
from src.artifacts.pattern.singleton import Singleton
from src.artifacts.env.configs import configs

# pylint: disable=unused-variable
__all__: list[str] = ["connection_manager"]


class MySession(Session):
    def __init__(self, *args, **kwargs):
        self.session_creation: str = datetime_provider.get_utc_iso_string()
        self.session_id: str = uuid_provider.get_str_uuid()
        super().__init__(*args, **kwargs)


class ConnectionManager(metaclass=Singleton):
    def __init__(self, user: str, password: str, host: str, port: int, database: str):
        self._database: str = database
        self._password: str = password
        self._user: str = user
        self._host: str = host
        self._port: int = port

        self._session: Union[MySession, None] = None
        self._engine: Union[Engine, None] = None

    def _start_engine(self) -> None:
        if self._engine is None:
            self._engine = create_engine(
                f"postgresql://{self._user}:{self._password}@{self._host}:{self._port}/{self._database}"
            )

    def _end_engine(self) -> None:
        if self._session is not None:
            self._end_session()
        if self._engine is not None:
            self._engine.dispose()

            del self._engine
            gc.collect()

            self._engine = None

    def _start_session(self) -> None:
        if self._session is None:
            self._session = sessionmaker(class_=MySession, bind=self._engine)()

            logging.debug(f"session started with id {self._session.session_id}")

    def _end_session(self) -> None:
        if self._session is not None:
            logging.debug(f"ending session with id {self._session.session_id}")

            self._session.close()

            del self._session
            gc.collect()

            self._session = None

    def _reset_session(self) -> None:
        self._end_session()
        self._start_session()

    def _check_session_health(self) -> bool:
        try:
            self._session.execute("select 1")

            logging.debug(f"session {self._session.session_id} is healthy")

            return True

        except SQLAlchemyError:
            logging.exception(
                f"session {self._session.session_id} is not healthy - creating a new session"
            )

            self._reset_session()

            return False

    def get_session(self) -> Session:
        self._start_engine()
        self._start_session()

        if self._check_session_health() is False:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

        logging.info(
            f"using session: {self._session.session_id} - session healthy since: {self._session.session_creation}"
        )

        return self._session


connection_manager: ConnectionManager = ConnectionManager(
    password=configs.database_password,
    database=configs.database_name,
    user=configs.database_user,
    host=configs.database_host,
    port=configs.database_port,
)
