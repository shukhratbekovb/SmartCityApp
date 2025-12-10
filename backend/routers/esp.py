from fastapi import WebSocket, APIRouter
from starlette.websockets import WebSocketDisconnect

router = APIRouter(
    prefix="/ws",
)
connected_esp: WebSocket | None = None


@router.websocket("/")
async def websocket_endpoint(ws: WebSocket):
    global connected_esp

    await ws.accept()
    connected_esp = ws
    print("✅ ESP CONNECTED TO /ws/water")
    try:
        while True:
            pass
    except WebSocketDisconnect:
        connected_esp = None
        print("❌ ESP DISCONNECTED")
