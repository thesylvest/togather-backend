from tortoise import fields
from enum import Enum

from app.core.base.models import BaseDBModel


class SupportedLanguages(str, Enum):
    TR = "tr"
    EN = "en"


class Language(BaseDBModel):
    class Meta:
        table = "languages"
    lang = fields.CharEnumField(max_length=3, enum_type=SupportedLanguages)
    data = fields.JSONField(null=True)
