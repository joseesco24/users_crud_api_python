# !/usr/bin/python3
# type: ignore

# ** info: sqlalchemy imports
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Column
from sqlalchemy import Date

# ** info: sqlalchemy declarative imports
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

__all__: list[str] = ["Users"]


class Users(Base):
    __tablename__: str = "users"

    internal_id: Column = Column(String(40), primary_key=True)
    estatal_id: Column = Column(Integer, unique=True)
    first_name: Column = Column(String(50))
    last_name: Column = Column(String(50))
    phone_number: Column = Column(Integer)
    email: Column = Column(String(50))
    gender: Column = Column(String(50))
    birthday: Column = Column(Date)
    creation: Column = Column(DateTime(timezone=True))
    modification: Column = Column(DateTime(timezone=True))
    password: Column = Column(String(64))
