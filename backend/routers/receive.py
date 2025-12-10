from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from depedencies import get_db
from managers.gas import GasSensorManager
from managers.humidity import HumiditySensorManager
from managers.rain import RainSensorManager
from managers.soil import SoilSensorManager
from managers.temperature import TemperatureSensorManager
from models.irrigation import Irrigation

router = APIRouter(
    prefix="/api",
)


# ===== DATA MODEL =====
class SensorData(BaseModel):
    value: int


@router.post("/temperature")
async def receive_temperature(
        data: SensorData,
        db: AsyncSession = Depends(get_db)
):
    print(f"[{datetime.now()}] 🌡️ Temperature: {data.value}")
    manager = TemperatureSensorManager(db)
    await manager.add(data.value)
    return {"status": "ok", "sensor": "temperature", "value": data.value}


@router.post("/humidity")
async def receive_humidity(
        data: SensorData,
        db: AsyncSession = Depends(get_db)
):
    print(f"[{datetime.now()}] 💧 Humidity: {data.value}")
    manager = HumiditySensorManager(db)
    await manager.add(data.value)
    return {"status": "ok", "sensor": "humidity", "value": data.value}


@router.post("/gas")
async def receive_gas(
        data: SensorData,
        db: AsyncSession = Depends(get_db)
):
    print(f"[{datetime.now()}] 🔥 Gas: {data.value}")
    manager = GasSensorManager(db)
    await manager.add(data.value)
    return {"status": "ok", "sensor": "gas", "value": data.value}


@router.post("/rain")
async def receive_rain(
        data: SensorData,
        db: AsyncSession = Depends(get_db)
):
    print(f"[{datetime.now()}] 🌧️ Rain: {data.value}")
    manager = RainSensorManager(db)
    await manager.add(data.value)
    return {"status": "ok", "sensor": "rain", "value": data.value}


@router.post("/soil")
async def receive_soil(
        data: SensorData,
        db: AsyncSession = Depends(get_db)
):
    print("🌱 SOIL:", data.value)
    manager = SoilSensorManager(db)
    await manager.add(data.value)
    return {
        "status": "ok",
        "soil": data.value
    }


@router.post(
    "/irrigation"
)
async def receive_irrigation(
        db: AsyncSession = Depends(get_db)
):
    obj = Irrigation(mode="manual")
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
