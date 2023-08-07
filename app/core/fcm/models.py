from tortoise import fields
from enum import Enum

from app.core.base.models import BaseDBModel, BaseCreatedAtModel


class DeviceType(str, Enum):
    IOS = "ios"
    ANDROID = "android"
    WEB = "web"


class FCMDevice(BaseDBModel, BaseCreatedAtModel):
    class Meta:
        table = "devices"
    name = fields.CharField(max_length=255, blank=True, null=True)
    device_id = fields.CharField(blank=True, null=True, db_index=True, max_length=255)
    registration_id = fields.TextField()
    device_type = fields.CharEnumField(enum_type=DeviceType, max_length=10)

    user: fields.ForeignKeyRelation["models.User"] = fields.ForeignKeyField(
        "models.User", related_name="devices", on_delete=fields.base.CASCADE
    )
