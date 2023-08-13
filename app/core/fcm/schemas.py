from tortoise.contrib.pydantic import pydantic_model_creator
from pydantic import BaseModel

from app.core.base.schemas import BaseOutSchema
from app.core.fcm.models import FCMDevice


class RegisterDeviceIn(BaseModel):
    name: str
    device_id: str
    registration_id: str
    device_type: str


class RegisterDeviceOut(BaseModel):
    device: str
    created: bool


class DeviceOut(BaseOutSchema):
    pydantic_model = pydantic_model_creator(FCMDevice)
