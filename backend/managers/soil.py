from managers.base import BaseSensorManager
from models.soil import Soil


def get_soil_moisture_percent(value: int) -> int:
    percent = 100 - int((value / 1023) * 100)
    return max(0, min(100, percent))


class SoilSensorManager(BaseSensorManager):
    model = Soil

    # async def get(self):
    #     obj = await super().get()
    #     percent = get_soil_moisture_percent(obj.value)
    #     return BaseSensorSchema(
    #         value=percent
    #     )
