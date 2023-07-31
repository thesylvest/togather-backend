from tortoise import fields
from enum import Enum

from app.core.base.contenttype import ContentType
from app.core.base.models import (
    BaseCreatedAtModel,
    BaseDBModel,
)


class NotificationType(str, Enum):
    user = "user"
    post = "post"
    event = "event"
    like = "like"
    comment = "comment"


class Notification(BaseDBModel, BaseCreatedAtModel, ContentType):
    class Meta:
        table = "notifications"
    is_anon = fields.BooleanField(default=False)
    type = fields.CharEnumField(enum_type=NotificationType)

    sent_to: fields.ManyToManyRelation["models.User"] = fields.ManyToManyField(
        "models.User", related_name="notifications"
    )


class Tag(BaseDBModel, ContentType):
    class Meta:
        table = "tags"
    name = fields.CharField(max_length=255)


class Report(BaseDBModel, BaseCreatedAtModel, ContentType):
    class Meta:
        table = "reports"
    reason = fields.CharField(max_length=512)

    repoter: fields.ForeignKeyRelation["models.User"] = fields.ForeignKeyField(
        "models.User", related_name="reports"
    )


class Hide(BaseDBModel, BaseCreatedAtModel, ContentType):
    class Meta:
        table = "hides"
    hider: fields.ForeignKeyRelation["models.User"] = fields.ForeignKeyField(
        "models.User", related_name="hides"
    )
