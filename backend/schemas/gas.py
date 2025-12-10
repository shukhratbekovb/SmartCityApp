from schemas.base import BaseSensorSchema


class GasRead(BaseSensorSchema):
    unit: str = 'ppm'
