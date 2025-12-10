from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from depedencies import get_db
from managers.soil import SoilSensorManager
from models.irrigation import Irrigation
from models.soil import Soil
from routers.esp import connected_esp

router = APIRouter(
    prefix="/soil",
)


async def get_sort_chart_data(db: AsyncSession):
    time_bucket = func.date_trunc("minute", Soil.created_at)

    stmt = (
        select(
            time_bucket.label("time"),
            func.avg(Soil.value).label("moisture"),
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


@router.post(
    "/water"
)
async def water():
    if connected_esp:
        await connected_esp.send_text("START")
        return {"success": True}
    return {"success": False}


@router.get(
    "/"
)
async def get_soil(
        db: AsyncSession = Depends(get_db)
):
    s_manager = SoilSensorManager(db)
    soil = await s_manager.get()
    chart = await get_sort_chart_data(db)
    stmt = select(Irrigation).order_by(Irrigation.created_at.desc()).limit(5)
    result = await db.execute(stmt)
    irrigation = result.scalars().all()
    return {
        "soil": soil.value,
        "chart": chart,
        "irrigation": [
            {
                "created_at": i.created_at.strftime("%H:%M"),
                "mode": i.mode
            }
            for i in irrigation
        ]
    }
