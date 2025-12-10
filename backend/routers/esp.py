import asyncio

from fastapi import WebSocket, APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.websockets import WebSocketDisconnect

from depedencies import get_db
from managers.soil import SoilSensorManager
from models.irrigation import Irrigation
from models.soil import Soil

router = APIRouter(
    prefix="/ws",
)
connected_esp: WebSocket | None = None
esp_queue: asyncio.Queue = asyncio.Queue()


async def send_and_wait(command: str, timeout=3):
    if not connected_esp:
        return None

    await connected_esp.send_text(command)

    try:
        return await asyncio.wait_for(esp_queue.get(), timeout=timeout)
    except asyncio.TimeoutError:
        return None


@router.websocket("/")
async def websocket_endpoint(ws: WebSocket):
    global connected_esp

    await ws.accept()
    connected_esp = ws
    print("✅ ESP CONNECTED TO /ws/water")
    try:
        while True:
            msg = await ws.receive_text()
            print("ESP:", msg)
            await esp_queue.put(msg)
    except WebSocketDisconnect:
        connected_esp = None
        print("❌ ESP DISCONNECTED")


light_router = APIRouter(
    prefix="/light",
)


@light_router.post("/assign-mode")
async def assign_light_mode():
    if not connected_esp:
        return {"success": False}

    mode = await send_and_wait("LIGHT:MODE")

    if mode == "LIGHT:MANUAL":
        await connected_esp.send_text("LIGHT:AUTO")
    else:
        await connected_esp.send_text("LIGHT:MANUAL")

    return {"success": True}


@light_router.post("/light-turn")
async def turn_light():
    if not connected_esp:
        return {"success": False}
    light = await send_and_wait("LIGHT:INFO")
    if light == "LIGHT:ON":
        await send_and_wait("LIGHT:OFF")
    else:
        await send_and_wait("LIGHT:ON")
    return {"success": True}


@light_router.get(
    "/light-mode"
)
async def get_light_mode():
    # Пусть будет получать Arduino light mode
    if not connected_esp:
        return {"success": False}

    mode = await send_and_wait("LIGHT:MODE")

    if not mode:
        return {"success": False, "error": "ESP not responding"}

    return {"mode": mode}


@light_router.get("/")
async def get_light():
    if not connected_esp:
        return {"mode": "No Info", "info": "No Info"}

    mode = await send_and_wait("LIGHT:MODE")
    info = await send_and_wait("LIGHT:INFO")

    return {"mode": mode, "info": info}


soil_router = APIRouter(
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


@soil_router.post("/water-mode")
async def water_mode():
    if not connected_esp:
        return {"success": False}
    mode = await send_and_wait("WATER:MODE")
    if mode == "WATER:MANUAL":
        await send_and_wait("WATER:AUTO")
    else:
        await send_and_wait("WATER:MANUAL")
    return {"success": True}


@soil_router.post(
    "/water"
)
async def water():
    if connected_esp:
        await send_and_wait("START")
        return {"success": True}
    return {"success": False}


@soil_router.get(
    "/water-mode"
)
async def get_water_mode():
    if not connected_esp:
        return {"success": False}
    mode = await send_and_wait("WATER:MODE")
    if mode == "WATER:MANUAL":
        return {"mode": "MANUAL"}
    else:
        return {"mode": "AUTO"}


@soil_router.get(
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


traffic_router = APIRouter(
    prefix="/traffic",
)

@traffic_router.post("/traffic")
async def traffic():
    if not connected_esp:
        return {"success": False}
    status = await send_and_wait("PRIORITY:STATUS")
    if status == "PRIORITY:ON":
        await send_and_wait("PRIORITY:OFF")
    else:
        await send_and_wait("PRIORITY:ON")
    return {"success": True}