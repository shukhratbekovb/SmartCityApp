from models.base import Base, IntIdMixin, SensorBase


class Gas(Base, IntIdMixin, SensorBase):
    __tablename__ = "gas"