from tortoise import fields

from app.core.base.models import BaseCreatedUpdatedAtModel, LocationModel, BaseDBModel


class Post(BaseDBModel, BaseCreatedUpdatedAtModel, LocationModel):
    class Meta:
        table = "posts"

    class PydanticMeta:
        backward_relations = False
        exclude = (
            "creator",
        )
    is_anon = fields.BooleanField(default=False)
    title = fields.CharField(max_length=255)
    media = fields.JSONField(null=True)
    content = fields.TextField()

    comments: fields.ReverseRelation

    category: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "models.Category", related_name="posts", null=True, on_delete=fields.SET_NULL
    )
    creator: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "models.User", related_name="posts", null=True
    )
    author_club: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "models.Club", related_name="posts", null=True
    )

    async def is_creator(self, user):
        if self.author_club:
            return await self.author_club.is_admin(user)
        return self.creator == user


class Comment(BaseDBModel, BaseCreatedUpdatedAtModel):
    class Meta:
        table = "comments"

    class PydanticMeta:
        backward_relations = False
        exclude = (
            "creator",
            "post",
        )
    is_anon = fields.BooleanField(default=False)
    content = fields.TextField()

    comments: fields.ReverseRelation

    creator: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "models.User", related_name="comments"
    )
    post: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "models.Post", related_name="comments"
    )
    reply_to: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "models.Comment", related_name="comments", null=True
    )

    async def is_creator(self, user):
        return self.creator == user
