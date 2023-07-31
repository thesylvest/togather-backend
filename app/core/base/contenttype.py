from tortoise import Tortoise, fields
from enum import Enum


class ModelType(str, Enum):
    user = "User"
    post = "Post"
    comment = "Comment"
    event = "Event"
    club = "Club"
    place = "Place"


class ContentType:
    item_type = fields.CharEnumField(enum_type=ModelType)
    item_id = fields.IntField()

    async def get_item(self):
        Model = Tortoise.get_model(self.item_type)
        return Model, await Model.get(id=self.item_id)
