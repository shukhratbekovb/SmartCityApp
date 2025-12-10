from models.base import Base, IntIdMixin, SensorBase


class Humidity(Base, IntIdMixin, SensorBase):
    __tablename__ = "humidity"
