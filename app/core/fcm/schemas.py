from pydantic import BaseModel


class RegisterDeviceIn(BaseModel):
    name: str
    device_id: str
    registration_id: str
    device_type: str


class RegisterDeviceOut(BaseModel):
    device: str
    created: bool
