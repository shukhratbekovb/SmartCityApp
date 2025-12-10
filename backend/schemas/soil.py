from enum import Enum

from schemas.base import BaseSensorSchema

class SoilMoistureStatusEnum(str, Enum):
    DRY = "dry"
    NORMAL = "normal"
    WET = "wet"

class SoilMoistureRead(BaseSensorSchema):
    unit: str = '%'
    status: SoilMoistureStatusEnum = SoilMoistureStatusEnum.NORMAL
    value: float