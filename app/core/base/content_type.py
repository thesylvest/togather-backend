from tortoise import Tortoise, fields
from enum import Enum


class ContentType:
    class ModelType(str, Enum):
        user = "User"
        post = "Post"
        comment = "Comment"
        event = "Event"
        club = "Club"
        place = "Place"
    item_type = fields.CharEnumField(enum_type=ModelType)
    item_id = fields.IntField()

    async def get_item(self):
        Model = Tortoise.apps.get("models")[self.item_type]
        return Model, await Model.get_or_none(id=self.item_id)

    @classmethod
    async def get_by_item(cls, item):
        print(item.__class__.__name__)
        return cls.filter(item_id=item.id, item_type=item.__class__.__name__)
