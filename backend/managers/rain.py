from managers.base import BaseSensorManager
from models.rain import Rain
from schemas.base import BaseSensorSchema


def get_rain_percent(value: int) -> int:
    return max(0, min(100, 100 - int((value / 1023) * 100)))


class RainSensorManager(BaseSensorManager):
    model = Rain

    # async def get(self):
    #     obj = await super().get()
    #     percent = get_rain_percent(obj.value)
    #     return BaseSensorSchema(
    #         value=percent
    #     )
