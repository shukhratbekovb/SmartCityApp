from enum import Enum

from schemas.base import BaseSensorSchema


class RainFall(Enum):
    DRY = "dry"
    LIGHT_RAIN = "light_rain"
    HEAVY_RAIN = "heavy_rain"


class RainRead(BaseSensorSchema):
    unit: str = '%'
    value: float
    status: RainFall = RainFall.DRY
