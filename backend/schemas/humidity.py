from schemas.base import BaseSensorSchema


class HumidityRead(BaseSensorSchema):
    unit: str = '%'
