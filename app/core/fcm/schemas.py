from pydantic import BaseModel

from app.core.base.schemas import ItemModel


class RegisterDeviceIn(BaseModel):
    name: str
    device_id: str
    registration_id: str
    device_type: str


class RegisterDeviceOut(BaseModel):
    device: str
    created: bool


class Device(ItemModel):
    name: str

    def allowed_actions(item, user):
        return ["oh yeah", "baby", str(user is None), item.device_type]
