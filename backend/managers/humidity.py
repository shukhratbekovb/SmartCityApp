from managers.base import BaseSensorManager
from models.humidity import Humidity


class HumiditySensorManager(BaseSensorManager):
    model = Humidity

