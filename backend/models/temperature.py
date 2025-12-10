from models.base import IntIdMixin, Base, SensorBase


class Temperature(Base, IntIdMixin, SensorBase):
    __tablename__ = "temperature"