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
from sqlalchemy.orm import Session

# **info: sqlalchemy exc imports
from sqlalchemy.exc import SQLAlchemyError

# ** info: artifacts imports
from src.artifacts.datetime.datetime_provider import datetime_provider
from src.artifacts.uuid.uuid_provider import uuid_provider
from src.artifacts.pattern.singleton import Singleton
from src.artifacts.env.configs import configs

# pylint: disable=unused-variable
__all__: list[str] = ["connection_manager", "CrudSession", "QuerySession"]


class QuerySession(Session):
    def __init__(self, logs: bool, *args, **kwargs):
        self.session_creation: str = datetime_provider.get_utc_iso_string()
        self.session_id: str = uuid_provider.get_str_uuid()
        self._logs: bool = logs

        super().__init__(*args, **kwargs)

        self._post_init()

    def _post_init(self) -> None:
        if self._logs:
            logging.info(f"query session started with id: {self.session_id}")

    def commit_and_close(self) -> None:
        if self._logs:
            logging.info(
                f"committing and closing query session with id: {self.session_id}"
            )
        super().commit()
        super().close()

    def commit(self) -> None:
        if self._logs:
            logging.info(f"committing query session with id: {self.session_id}")
        super().commit()

    def close(self) -> None:
        if self._logs:
            logging.info(f"closing query session with id: {self.session_id}")
        super().close()


class CrudSession(Session):
    def __init__(self, logs: bool, *args, **kwargs):
        self.session_creation: str = datetime_provider.get_utc_iso_string()
        self.session_id: str = uuid_provider.get_str_uuid()
        self._logs: bool = logs

        super().__init__(*args, **kwargs)

        self._post_init()

    def _post_init(self) -> None:
        if self._logs:
            logging.info(f"crud session started with id: {self.session_id}")

    def commit_and_close(self) -> None:
        if self._logs:
            logging.info(
                f"committing and closing crud session with id: {self.session_id}"
            )
        super().commit()
        super().close()

    def commit(self) -> None:
        if self._logs:
            logging.info(f"committing crud session with id: {self.session_id}")
        super().commit()

    def close(self) -> None:
        if self._logs:
            logging.info(f"closing crud session with id: {self.session_id}")
        super().close()


class ConnectionManager(metaclass=Singleton):
    def __init__(
        self, user: str, password: str, host: str, port: int, database: str, logs: bool
    ):
        self._database: str = database
        self._password: str = password
        self._logs: bool = logs
        self._user: str = user
        self._host: str = host
        self._port: int = port

        self._query_session: Union[QuerySession, None] = None
        self._engine: Union[Engine, None] = None

    def _start_engine(self) -> None:
        if self._engine is None:
            self._engine = create_engine(
                f"postgresql://{self._user}:{self._password}@{self._host}:{self._port}/{self._database}"
            )

    def _end_engine(self) -> None:
        if self._query_session is not None:
            self._end_query_session()
        if self._engine is not None:
            self._engine.dispose()
            del self._engine
            gc.collect()
            self._engine = None

    def _start_query_session(self) -> None:
        if self._query_session is None:
            self._query_session = QuerySession(logs=self._logs, bind=self._engine)

    def _end_query_session(self) -> None:
        if self._query_session is not None:
            self._query_session.close()
            del self._query_session
            gc.collect()
            self._query_session = None

    def _reset_query_session(self) -> None:
        self._end_query_session()
        self._start_query_session()

    def _check_query_session_health(self) -> bool:
        try:
            self._query_session.execute("select 1")
            if self._logs:
                logging.debug(
                    f"query session {self._query_session.session_id} is healthy"
                )
            return True

        except SQLAlchemyError:
            if self._logs:
                logging.exception(
                    f"query session {self._query_session.session_id} isn't healthy"
                )
                logging.warning("creating a new query session")
            self._reset_query_session()
            return False

    def get_crud_session(self) -> CrudSession:
        self._start_engine()
        crud_session: CrudSession = CrudSession(logs=self._logs, bind=self._engine)
        if self._logs:
            logging.info(f"crud session started with id: {crud_session.session_id}")
            logging.info(f"using crud session with id: {crud_session.session_id}")
            logging.info(f"session healthy since: {crud_session.session_creation}")
        return crud_session

    def get_query_session(self) -> QuerySession:
        self._start_engine()
        self._start_query_session()
        if self._check_query_session_health() is False:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if self._logs:
            logging.info(
                f"using query session with id: {self._query_session.session_id}"
            )
            logging.info(
                f"session healthy since: {self._query_session.session_creation}"
            )
        return self._query_session


connection_manager: ConnectionManager = ConnectionManager(
    password=configs.database_password,
    database=configs.database_name,
    user=configs.database_user,
    host=configs.database_host,
    port=configs.database_port,
    logs=configs.database_logs,
)
