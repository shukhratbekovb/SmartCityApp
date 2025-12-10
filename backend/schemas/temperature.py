from schemas.base import BaseSensorSchema


class TemperatureRead(BaseSensorSchema):
    unit: str = '°C'
