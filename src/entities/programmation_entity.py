# !/usr/bin/python3
# type: ignore

# ** info: sqlalchemy imports
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Column
from sqlalchemy import Time


# ** info: sqlalchemy declarative imports
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

__all__: list[str] = ["TvProgramation"]


class TvProgramation(Base):
    __tablename__: str = "tv_programation"

    programation_id: Column = Column(String(40), primary_key=True)
    channel_id: Column = Column(Integer, nullable=False)
    channel_name: Column = Column(String(200), nullable=False)
    channel_content_type: Column = Column(String(200), nullable=False)
    start_houre: Column = Column(Time, nullable=False)
    end_houre: Column = Column(Time, nullable=False)
    weeks: Column = Column(ARRAY(Integer), nullable=False)
    days: Column = Column(ARRAY(Integer), nullable=False)
    year: Column = Column(Integer, nullable=False)
    creation: Column = Column(DateTime(timezone=True))
    modification: Column = Column(DateTime(timezone=True))
