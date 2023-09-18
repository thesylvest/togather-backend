from tortoise import fields, Model
from enum import Enum

from app.core.base.models import BaseCreatedAtModel, BaseDBModel, ContentType
from app.core.fcm.utils import send_notification
from app.core.base.utils import name2model
from app.core.base.media_manager import S3


class Notification(BaseDBModel, BaseCreatedAtModel, ContentType):
    class Type(str, Enum):
        connect_accepted = "connect_accept"
        connect_sent = "connect_sent"

    class Meta:
        table = "notifications"

    class PydanticMeta:
        exclude = ["sent_to"]
    is_anon = fields.BooleanField(default=False)
    notif_type = fields.CharEnumField(enum_type=Type, max_length=20)

    sent_to: fields.ManyToManyRelation = fields.ManyToManyField(
        "models.User", related_name="notifications"
    )

    async def notification_data(self) -> dict[str, str]:
        Model = name2model[self.item_type]
        item: BaseDBModel = await Model.get(id=self.item_id)
        data = {"title": "ToGather"}

        media = item.media_dict["media"][0] if item.media_dict else None  # This is default for most models

        match self.notif_type:
            case self.Type.connect_accepted:
                data["body"] = f"{item.username} isimli kullanıcı bağlantı isteğinizi kabul etti."
            case self.Type.connect_sent:
                data["body"] = f"{item.username} isimli kullanıcı size bağlantı isteği attı.",

        data["image"] = S3.get_file_url(media) if media else None
        return data

    async def send(self):
        my_data = await self.notification_data()
        return await send_notification(self.sent_to.all(), my_data["title"], my_data["body"], my_data["image"])

    @staticmethod
    async def create_and_sent(
        sent_to: list,
        notification_type: Type,
        item: Model,
        is_anon: bool = False
    ):
        notification = await Notification.create(
            notif_type=notification_type,
            item_id=item.id,
            item_type=item.__class__.__name__,
            is_anon=is_anon
        )
        await notification.sent_to.add(*sent_to)
        return await notification.send()


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

    class PydanticMeta:
        exclude = ["item_type", "item_id", "id"]
    name = fields.CharField(max_length=255)


class Category(BaseDBModel):
    class Meta:
        table = "categories"

    class PydanticMeta:
        backward_relations = False
        exclude = ["follower"]
        computed = ["picture"]
    name = fields.CharField(max_length=255)
    picture_name = fields.CharField(max_length=255, null=True)

    follower: fields.ManyToManyRelation = fields.ManyToManyField(
        "models.User", related_name="interests", backward_key="category_id"
    )

    def picture(self) -> str:
        return S3.get_file_url(self.picture_name) if self.picture_name else None
