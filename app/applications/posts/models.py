from tortoise import fields

from app.core.base.models import (
    BaseCreatedUpdatedAtModel,
    LocationModel,
    BaseDBModel,
)


class Post(BaseDBModel, BaseCreatedUpdatedAtModel, LocationModel):
    class Meta:
        table = "posts"
    is_anon = fields.BooleanField(default=False)
    title = fields.CharField(max_length=255)
    media = fields.CharField(max_length=255, null=True)
    content = fields.TextField()

    comments: fields.ReverseRelation

    author_user: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "models.User", related_name="posts", null=True
    )
    author_club: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "models.Club", related_name="posts", null=True
    )


class Comment(BaseDBModel, BaseCreatedUpdatedAtModel):
    class Meta:
        table = "comments"
    is_anon = fields.BooleanField(default=False)
    content = fields.TextField()
    media = fields.CharField(max_length=255, null=True)

    comments: fields.ReverseRelation

    author: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "models.User", related_name="comments"
    )
    post: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "models.Post", related_name="comments"
    )
    reply_to: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "models.Comment", related_name="comments", null=True
    )
