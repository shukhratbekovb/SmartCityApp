from fastapi import APIRouter, Depends

from sqlalchemy.ext.asyncio import AsyncSession

from depedencies import get_db

from managers.gas import GasSensorManager
from managers.humidity import HumiditySensorManager
from managers.rain import RainSensorManager
from managers.soil import SoilSensorManager
from managers.temperature import TemperatureSensorManager

router = APIRouter(
    prefix="/dashboard",
)

@router.get(
    "/",
)
async def get_dashboard(
        db: AsyncSession = Depends(get_db)
):
    h_manager = HumiditySensorManager(db)
    t_manager = TemperatureSensorManager(db)
    s_manager = SoilSensorManager(db)
    g_manager = GasSensorManager(db)
    ra_manager = RainSensorManager(db)

    humidity = await h_manager.get()
    temperature = await t_manager.get()
    soil = await s_manager.get()
    moisture = await s_manager.get()
    gas = await g_manager.get()
    rain = await ra_manager.get()

    return {
        "humidity": humidity.value,
        "temperature": temperature.value,
        "soil": soil.value,
        "moisture": moisture.value,
        "gas": gas.value,
        "rain": rain.value,
    }



