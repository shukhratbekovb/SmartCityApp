from models.base import IntIdMixin, Base, SensorBase


class Soil(Base, IntIdMixin, SensorBase):
    __tablename__ = "soil"
