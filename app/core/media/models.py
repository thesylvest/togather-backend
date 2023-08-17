from tortoise import fields
from enum import Enum

from app.core.base.models import BaseDBModel, BaseCreatedAtModel


class FileType(str, Enum):
    JPEG = "image/jpeg"
    PNG = "image/png"
    MP4 = "video/mp4"


class File(BaseDBModel, BaseCreatedAtModel):
    class Meta:
        table = "files"
    file_name = fields.CharField(max_length=255, blank=True, null=True)
    file_type = fields.CharEnumField(enum_type=FileType, max_length=10)
