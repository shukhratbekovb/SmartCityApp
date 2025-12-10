from managers.base import BaseSensorManager
from models.temperature import Temperature


class TemperatureSensorManager(BaseSensorManager):
    model = Temperature

