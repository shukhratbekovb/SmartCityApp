from pydantic import BaseModel

class VoiceCommand(BaseModel):
    command: str