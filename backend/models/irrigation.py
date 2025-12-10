from datetime import datetime

from sqlalchemy import Column, DateTime, String

from models.base import Base, IntIdMixin


class Irrigation(Base, IntIdMixin):
    __tablename__ = "irrigation"
    created_at = Column(DateTime, default=datetime.now)
    mode = Column(String(6))