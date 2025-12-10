from datetime import datetime

from enum import Enum

from pydantic import BaseModel


class StatusEnum(str, Enum):
    NORMAL = 'normal'
    WARNING = 'warning'
    CRITICAL = 'critical'


class BaseSensorSchema(BaseModel):
    value: int
