from tortoise.models import Model
from tortoise import fields


class Admin(Model):
    class PydanticMeta:
        exclude = ["password"]
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=255)
    password = fields.CharField(max_length=255)
