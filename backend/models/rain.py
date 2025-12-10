from models.base import Base, IntIdMixin, SensorBase


class Rain(Base, IntIdMixin, SensorBase):
    __tablename__ = "rain"