from fastapi import APIRouter, Depends

from depedencies import get_db
from managers.gas import GasSensorManager
from managers.humidity import HumiditySensorManager
from managers.rain import RainSensorManager
from managers.temperature import TemperatureSensorManager
from models.gas import Gas
from models.humidity import Humidity
from models.temperature import Temperature

router = APIRouter(
    prefix="/air",
)

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession


async def get_sensor_chart_data(db: AsyncSession):
    temp_subq = (
        select(
            func.date_trunc("minute", Temperature.created_at).label("time"),
            func.avg(Temperature.value).label("temp")
        )
        .group_by("time")
        .subquery()
    )

    hum_subq = (
        select(
            func.date_trunc("minute", Humidity.created_at).label("time"),
            func.avg(Humidity.value).label("humidity")
        )
        .group_by("time")
        .subquery()
    )

    query = (
        select(
            temp_subq.c.time,
            temp_subq.c.temp,
            hum_subq.c.humidity
        )
        .join(hum_subq, temp_subq.c.time == hum_subq.c.time)
        .order_by(temp_subq.c.time)
    )

    result = await db.execute(query)
    rows = result.all()

    return [
        {
            "time": row.time.strftime("%H:%M"),
            "temp": round(row.temp),
            "humidity": round(row.humidity),
        }
        for row in rows
    ]


async def get_air_chart_data(db: AsyncSession):
    time_bucket = func.date_trunc("minute", Gas.created_at)

    stmt = (
        select(
            time_bucket.label("time"),
            func.avg(Gas.value).label("quality"),
        )
        .group_by(time_bucket)
        .order_by(time_bucket)
    )

    result = await db.execute(stmt)
    rows = result.all()

    data = [
        {
            "time": row.time.strftime("%H:%M"),
            "quality": round(row.quality)
        }
        for row in rows
    ]

    return data


@router.get(
    "/"
)
async def get_air(
        db: AsyncSession = Depends(get_db)
):
    r_manager = RainSensorManager(db)
    h_manager = HumiditySensorManager(db)
    t_manager = TemperatureSensorManager(db)
    g_manager = GasSensorManager(db)

    temp_chart = await get_sensor_chart_data(db)
    air_chart = await get_air_chart_data(db)

    return {
        "tempChart": temp_chart,
        "airChart": air_chart,
        "gas": (await g_manager.get()).value,
        "temperature": (await t_manager.get()).value,
        "humidity": (await h_manager.get()).value,
        "rain": (await r_manager.get()).value
    }
