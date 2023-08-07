from pydantic import BaseModel

from app.core.base.schemas import BaseOutModel


class RegisterDeviceIn(BaseModel):
    name: str
    device_id: str
    registration_id: str
    device_type: str


class RegisterDeviceOut(BaseModel):
    device: str
    created: bool


class DeviceOut(BaseOutModel):
    name: str
    device_id: str
    registration_id: str
    device_type: str

    @classmethod
    def add_fields(item, user):
        return dict()
