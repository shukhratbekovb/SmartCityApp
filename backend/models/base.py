from datetime import datetime

from sqlalchemy import Column, BigInteger, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class IntIdMixin:
    id = Column(BigInteger, primary_key=True, autoincrement=True)

class SensorBase:
    value = Column(Integer)
    created_at = Column(DateTime, default=datetime.now)