from datetime import date, datetime, time

from sqlalchemy import select, and_, desc

from sqlalchemy.ext.asyncio import AsyncSession

from schemas.base import BaseSensorSchema


class BaseManager:
    model = None

    def __init__(self, db: AsyncSession):
        self.db = db


class BaseSensorManager(BaseManager):
    async def add(
            self,
            value: int
    ):
        obj = self.model(value=value)
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)

    async def get(self):
        stmt = select(self.model).order_by(desc(self.model.created_at)).limit(1)
        result = await self.db.execute(stmt)
        obj = result.scalar_one_or_none()
        if not obj:
            return BaseSensorSchema(
                value=0
            )
        else:
            return BaseSensorSchema(
                value=obj.value
            )

    async def list(self):
        today = date.today()

        start_dt = datetime.combine(today, time.min)   # 00:00:00
        end_dt = datetime.combine(today, time.max)     # 23:59:59

        stmt = select(self.model).where(
            and_(
                self.model.created_at >= start_dt,
                self.model.created_at <= end_dt
            )
        ).order_by(self.model.created_at)

        result = await self.db.execute(stmt)
        objects = result.scalars().all()

        # ✅ Если вообще нет данных за день — отдаем нули по часам
        if not objects:
            return [
                {"time": f"{hour:02d}:00", "value": 0}
                for hour in range(24)
            ]

        data = []

        # ✅ Добавляем реальные апдейты (детально)
        for obj in objects:
            data.append({
                "time": obj.created_at.strftime("%d/%m/%Y %H:%M:%S"),
                "value": obj.value
            })

        return data
