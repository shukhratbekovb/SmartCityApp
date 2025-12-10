from pydantic import BaseModel


class LightMode(BaseModel):
    is_auto: bool

class Light(BaseModel):
    is_on: bool
