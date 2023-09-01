from tortoise import fields
from enum import Enum
import asyncio

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


class Report(BaseDBModel, BaseCreatedAtModel, ContentType):
    class Meta:
        table = "reports"
    reason = fields.TextField()

    reporter: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "models.User", related_name="reports"
    )


class Hide(BaseDBModel, BaseCreatedAtModel, ContentType):
    class Meta:
        table = "hides"
    hider: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "models.User", related_name="hides"
    )


class Rate(BaseDBModel, BaseCreatedAtModel, ContentType):
    class Meta:
        table = "rates"
    rate = fields.FloatField()
    rater: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "models.User", related_name="rates"
    )


class Tag(BaseDBModel, ContentType):
    class Meta:
        table = "tags"
    name = fields.CharField(max_length=255)


class Category(BaseDBModel):
    class Meta:
        table = "categories"

    class PydanticMeta:
        backward_relations = False
        exclude = ["follower"]
    name = fields.CharField(max_length=255)
    picture = fields.CharField(max_length=255, null=True)

    follower: fields.ManyToManyRelation = fields.ManyToManyField(
        "models.User", related_name="interests", backward_key="category_id"
    )


async def init_category(i):
    await Category.get_or_create(name=f"cat{i}", picture=None)

for i in range(10):
    loop = asyncio.get_event_loop()
    asyncio.run_coroutine_threadsafe(init_category(i), loop)
