# Python
from datetime import datetime
from functools import partial
import traceback
import logging
import sys

# Typing
from typing import Union
from typing import Dict
from typing import Any

# FastAPI
from fastapi import HTTPException
from fastapi import status

# SQL Alchemy
from sqlalchemy.exc import NoSuchTableError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.exc import IntegrityError
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy import MetaData
from sqlalchemy import select
from sqlalchemy import insert
from sqlalchemy import update
from sqlalchemy import column
from sqlalchemy import Table

# Commons
from src.commons.path_manager import get_file_name
from src.commons.yaml_reader import yaml_reader

# Dict hash
from dict_hash import dict_hash

__all__ = ["Postgres"]

script_name = get_file_name()


class Postgres:

    """postgres

    this class is instantiable, so for use it you would need to create a object based on it, the
    resulting object would provide methods that allow to interact with a postgres database in a
    simple way, all the class is based on Python SQLAlchemy library.
    """

    __generic_search_cache__ = {}
    __tables_cache__ = {}
    __dates_cache__ = {}

    def __init__(self, connection_string: str, schema: str = "public") -> None:
        self._connection_string = connection_string
        self._schema = schema

    def start_connection(self) -> None:

        """start connection

        starts a connection with the database using a synchronous SQLAlchemy engine.
        """

        try:

            self._db_engine = create_engine(url=self._connection_string)

            self._db_connection = self._db_engine.connect()
            self._metadata = MetaData(schema=self._schema)
            self._metadata.reflect(bind=self._db_engine)
            self._session = None

        except SQLAlchemyError:

            error_type = str(sys.exc_info()[0].__name__)
            error_message = str(sys.exc_info()[1])

            error_data = {
                "traceback": f"{traceback.format_exc(chain=False)}",
                "error_message": error_message,
                "error_type": error_type,
            }

            logging.error(
                yaml_reader.get_logg_message(script_name, "logg_001", error_data)
            )

            msg = yaml_reader.get_error_message(script_name, "error_001", error_data)

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=msg,
            )

    def check_mandatory_table_schema(
        self, table_name: str, table_keys: list[str]
    ) -> None:

        table_reflect = self.__reflect_table__(table_name=table_name)

        real_table_keys = set([column.name for column in table_reflect.columns])
        data_keys = set(table_keys)

        if not data_keys.issubset(real_table_keys):
            error_data = {
                "aditional_keys": ", ".join(list(data_keys - real_table_keys)),
                "table_name": table_name,
            }
            msg = yaml_reader.get_error_message(script_name, "error_003", error_data)
            logging.error(msg)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=msg,
            )

    def start_transaction(self) -> None:

        """start transaction

        starts a transaction context using a SQLAlchemy session.
        """

        if self._session == None:
            self._session = Session(bind=self._db_engine)

    def rollback_transaction(self) -> None:

        """rollback transaction

        rollbacks all the operations executed during the current transaction context.
        """

        if self._session == None:
            self._session.rollback()

    def commit_transaction(self) -> None:

        """rollback transaction

        commits all the operations executed during the current transaction context.
        """

        if self._session == None:
            self._session.commit()

    def get_payment_date_with_system_date(
        self, system_date: datetime, table_metadata: dict
    ) -> datetime:

        if system_date in self.__dates_cache__:

            return self.__dates_cache__[system_date]

        else:

            table = self.__reflect_table__(table_name=table_metadata["name"])

            statement = select(
                [table.columns[table_metadata["keys"]["paymentDate"]]]
            ).where(table.columns[table_metadata["keys"]["systemDate"]] == system_date)

            if self._session == None:
                result = self._db_engine.execute(statement=statement).one()[
                    table_metadata["keys"]["paymentDate"]
                ]
            else:
                result = self._session.execute(statement=statement).one()[
                    table_metadata["keys"]["paymentDate"]
                ]

            self.__dates_cache__[system_date] = result

            return result

    def geenric_search(self, table_name: datetime, filter: dict) -> Any:

        filter_hash = dict_hash(filter)

        result = None

        if (
            table_name in self.__generic_search_cache__
            and filter_hash in self.__generic_search_cache__[table_name]
        ):

            result = self.__generic_search_cache__[table_name][filter_hash]

        else:

            table = self.__reflect_table__(table_name=table_name)

            statement = select([column(list(table.primary_key)[0].name)])

            for key, value in filter.items():
                statement = statement.where(table.columns[key] == value)

            if self._session == None:
                result = self._db_engine.execute(statement=statement).one()[0]
            else:
                result = self._session.execute(statement=statement).one()[0]

            if table_name not in self.__generic_search_cache__:
                self.__generic_search_cache__[table_name] = {filter_hash: result}
            else:
                self.__generic_search_cache__[table_name][filter_hash] = result

        return result

    def flush_transaction(self) -> None:

        """flush transaction

        flushes all the operations executed during the current transaction context.
        """

        if self._session == None:
            self._session.flush()

    def close_transaction(self) -> None:

        """close transaction

        close the current transaction context.
        """

        if self._session == None:
            self._session.close()
            self._session = None

    def close_connection(self) -> None:

        """close connection

        close the current connection.
        """

        self._session.close() if self._session != None else None
        self._db_connection.close()
        self._db_engine.dispose()

    def update_one(self, table_name: str, data: dict, primary_key_value: Any) -> None:

        """update one

        updates one record in the database.
        """

        table = self.__reflect_table__(table_name=table_name)

        statement = (
            update(table)
            .values(**data)
            .where(table.primary_key.columns.values()[0] == primary_key_value)
        )

        if self._session == None:
            self._db_engine.execute(statement=statement)
        else:
            self._session.execute(statement=statement)

    def load_batch(self, data: list[dict], table_name: str) -> list[Any]:

        """load batch

        loads a list of registers to the indicated database table, the received registers are dicts
        where every dict the key corresponds with the column name and the value is the value that
        is going to be load to that column in the register.
        the example presented in the examples section will produce that the string (hello world) is
        loaded to the column "message" in the table "users".

        args:
        - data list(dict): the registers to load to the database.
        - table_name (str): the name of the table to load the register or registers.

        returns:
        - list(Any): the primary keys of the registers loaded

        example:
        - data = {message: "hello world"}, table_name = "users"
        """

        table_reflect = self.__reflect_table__(table_name=table_name)

        return list(
            map(
                partial(
                    self.__load__,
                    table_reflect,
                ),
                data,
            )
        )

    def load_one(self, data: dict, table_name: str) -> Any:

        """load one

        loads a single register to the indicated database table, the received register is a dict where
        every key corresponds with the column name and the value is the value that is going to be
        load to that column in the register.
        the example presented in the examples section will produce that the string (hello world) is
        loaded to the column "message" in the table "users".

        args:
        - data (dict): the register to load to the database
        - table_name (str): the name of the table to load the register or registers

        returns:
        - Any: the primary key of the register loaded

        example:
        - data = {message: "hello world"}, table_name = "users"
        """

        table_reflect = self.__reflect_table__(table_name=table_name)
        return self.__load__(table=table_reflect, data=data)

    def __load__(self, table: Table, data: dict) -> Union[Any, Dict]:

        if "lineno" in data:
            lineno = data["lineno"]
            del data["lineno"]
        else:
            lineno = 0

        try:

            statement = insert(table=table, values=data)

            if self._session == None:
                result = self._db_engine.execute(statement=statement)
            else:
                result = self._session.execute(statement=statement)

            return result.inserted_primary_key[0]

        except IntegrityError:

            error_list = str(sys.exc_info()[1]).split("\n")

            error_message = (
                error_list[0].strip() + " " + error_list[1].split("DETAIL:")[1].strip()
            )

            error_data = {"table_name": table.name, "error_detail": error_message}
            msg = yaml_reader.get_error_message(script_name, "error_004", error_data)
            logging.warning(msg)

            return {
                "error": {
                    "error type": "IntegrityError",
                    "error message": msg,
                    "lineno": lineno,
                }
            }

        except SQLAlchemyError:

            statement = str(statement.compile(compile_kwargs={"literal_binds": True}))

            custom_traceback = traceback.format_exc(chain=False, limit=4)
            error_type = str(sys.exc_info()[0].__name__)
            error_message = str(sys.exc_info()[1])

            error_data = {
                "error_type": error_type,
                "error_message": error_message,
                "traceback": custom_traceback,
            }

            logging.warning(
                yaml_reader.get_logg_message(script_name, "logg_003", error_data)
            )

            return {
                "error": {
                    "error message": error_message,
                    "error type": error_type,
                    "lineno": lineno,
                }
            }

    def __reflect_table__(self, table_name: str) -> Table:

        if table_name in self.__tables_cache__:

            table = self.__tables_cache__[table_name]

        else:

            try:

                table = Table(
                    table_name,
                    self._metadata,
                    schema=self._schema,
                    autoload_with=self._db_engine,
                )

                self.__tables_cache__[table_name] = table

            except NoSuchTableError:

                error_data = {"table_name": table_name}

                msg = yaml_reader.get_error_message(
                    script_name, "error_002", error_data
                )

                logging.error(msg)

                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=msg,
                )

            except SQLAlchemyError:

                error_type = str(sys.exc_info()[0].__name__)
                error_message = str(sys.exc_info()[1])

                error_data = {
                    "traceback": f"{traceback.format_exc(chain=False)}",
                    "error_message": error_message,
                    "error_type": error_type,
                    "table_name": table_name,
                }

                logging.error(
                    yaml_reader.get_logg_message(script_name, "logg_002", error_data)
                )

                msg = yaml_reader.get_error_message(
                    script_name, "error_002", error_data
                )

                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=msg,
                )

        return table
