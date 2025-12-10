from fastapi import FastAPI, WebSocket
from starlette.middleware.cors import CORSMiddleware

from routers.dashboard import router as dashboard_router
from routers.air import router as air_router
from routers.receive import router as receive_router
from routers.soil import router as soil_router
from routers.esp import router as esp_router
from routers.light import router as light_router
app = FastAPI(
    title="Smart City App",
    description="Maded by WIUT Student Boburbek Shukhratbekov",
    version="1.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dashboard_router)
# app.include_router(light_router)
app.include_router(soil_router)
app.include_router(air_router)
app.include_router(receive_router)
app.include_router(light_router)
app.include_router(esp_router)
# app.include_router(voice_router)
