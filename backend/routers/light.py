from fastapi import APIRouter

from routers.esp import connected_esp

router = APIRouter(
    prefix="/light",
)


@router.post(
    "/assign-mode"
)
async def assign_light_mode(

):
    if connected_esp:
        await connected_esp.send_text("LIGHT:MODE")
        msg = await connected_esp.receive_text()
        if msg == "MANUAL":
            await connected_esp.send_text("LIGHT:AUTO")
        else:
            await connected_esp.send_text("LIGHT:MANUAL")
        return {"success": True}
    return {"success": False}


@router.post(
    "/light-turn"
)
async def turn_light(

):
    if connected_esp:
        await connected_esp.send_text("LIGHT:TURN")
        return {"success": True}
    return {"success": False}


@router.get(
    "/light-mode"
)
async def get_light_mode():
    # Пусть будет получать Arduino light mode
    if connected_esp:
        await connected_esp.send_text("LIGHT:MODE")
        msg = await connected_esp.receive_text()
        return {
            "mode": msg
        }
    return {"success": False}


@router.get(
    "/"
)
async def get_light():
    if connected_esp:
        await connected_esp.send_text("LIGHT:MODE")
        mode = await connected_esp.receive_text()
        await connected_esp.send_text("LIGHT:INFO")
        info = await connected_esp.receive_text()
        return {
            "mode": mode,
            "info": info
        }
    return {
        "mode": "No Info",
        "info": "No Info"
    }
