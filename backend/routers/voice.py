from fastapi import APIRouter

from schemas.voice import VoiceCommand

router = APIRouter(
    prefix="/voice",
)


@router.post(
    "/"
)
async def send_command(
        request: VoiceCommand,
):
    pass
