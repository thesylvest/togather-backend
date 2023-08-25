from tortoise import fields
from enum import Enum

from app.core.base.content_type import ContentType
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

    class PydanticMeta:
        computed = ("notification_data",)
    is_anon = fields.BooleanField(default=False)
    type = fields.CharEnumField(enum_type=NotificationType)

    sent_to: fields.ManyToManyRelation = fields.ManyToManyField(
        "models.User", related_name="notifications"
    )

    def notification_data(self) -> dict[str, str]:
        match self.type:
            case NotificationType.user:
                return {"computed": "compute"}
            case NotificationType.post:
                return {"computed": "compute"}
            case NotificationType.event:
                return {"computed": "compute"}
            case NotificationType.like:
                return {"computed": "compute"}
            case NotificationType.comment:
                return {"computed": "compute"}
        return {"computed": "not compute"}


class Tag(BaseDBModel, ContentType):
    class Meta:
        table = "tags"
    name = fields.CharField(max_length=255)


class Report(BaseDBModel, BaseCreatedAtModel, ContentType):
    class Meta:
        table = "reports"
    reason = fields.CharField(max_length=512)

    repoter: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "models.User", related_name="reports"
    )


class Hide(BaseDBModel, BaseCreatedAtModel, ContentType):
    class Meta:
        table = "hides"
    hider: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "models.User", related_name="hides"
    )


class Category(BaseDBModel):
    class Meta:
        table = "categories"
    name = fields.CharField(max_length=255)
    picture = fields.CharField(max_length=255, null=True)
